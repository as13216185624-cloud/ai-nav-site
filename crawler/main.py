#!/usr/bin/env python3
"""
九万AI - 自动抓取 + AI评分系统
每天自动从 Civitai/Reddit 抓取全球优秀AI作品，AI多维度打分筛选，自动发布到网站
部署：腾讯云服务器 cron 每天执行
"""

import os, sys, json, re, time, hashlib, subprocess
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# ===================== 配置 =====================
BASE_DIR = Path(__file__).resolve().parent.parent  # ai-nav-site/
SHOWCASE_JSON = BASE_DIR / "showcase.json"
SHOWCASE_DIR = BASE_DIR / "showcase"
GIT_REMOTE = "origin"
GIT_BRANCH = "main"

# API 密钥（优先从环境变量读取）
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# 抓取配置
CIVITAI_LIMIT = 30          # Civitai 每次抓取数量
MIN_AI_SCORE = 6.0           # 低于此分不收录
MAX_NEW_PER_DAY = 12         # 每天最多新增
IMAGE_MAX_WIDTH = 800        # 图片压缩宽度

# ===================== 1. 数据源 =====================

def fetch_civitai(limit=30):
    """Civitai 热门图片 API（免费，无需认证）"""
    print(f"[Civitai] 抓取中 (limit={limit})...")
    url = "https://civitai.com/api/v1/images"
    params = {"limit": limit, "sort": "Most Reactions", "period": "Day", "nsfw": "None"}
    headers = {"User-Agent": "JiuWanAI-Bot/1.0"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Civitai] ❌ 请求失败: {e}")
        return []

    works = []
    for item in data.get("items", []):
        meta = item.get("meta", {}) or {}
        prompt = (meta.get("prompt") or "").strip()
        if not prompt or len(prompt) < 10:
            continue

        image_url = item.get("url", "")
        if not image_url:
            continue

        works.append({
            "source": "Civitai",
            "source_id": f"civitai_{item.get('id')}",
            "source_url": f"https://civitai.com/images/{item.get('id')}",
            "title": _gen_title(prompt),
            "author": item.get("username") or "Anonymous",
            "tool": _guess_tool(prompt, item),
            "type": "image",
            "prompt": prompt,
            "tags": _extract_tags(prompt),
            "likes": (item.get("stats") or {}).get("reactionCount", 0),
            "image_url": image_url,
            "width": item.get("width", 0),
            "height": item.get("height", 0),
            "date": datetime.now().strftime("%Y-%m-%d"),
        })
    print(f"[Civitai] 获取 {len(works)} 条有效作品")
    return works


def fetch_reddit_sd(limit=25):
    """Reddit r/StableDiffusion 热门帖"""
    print(f"[Reddit] 抓取中 (limit={limit})...")
    url = f"https://www.reddit.com/r/StableDiffusion/hot.json?limit={limit}"
    headers = {"User-Agent": "JiuWanAI-Bot/1.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Reddit] ❌ 请求失败: {e}")
        return []

    works = []
    for post in data.get("data", {}).get("children", []):
        p = post["data"]
        title = p.get("title", "")
        url_overridden = p.get("url_overridden_by_dest", "")

        # 只收图片帖
        if not url_overridden or not any(url_overridden.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            continue

        works.append({
            "source": "Reddit",
            "source_id": f"reddit_{p.get('id')}",
            "source_url": f"https://reddit.com{p.get('permalink')}",
            "title": title[:80] if title else "Untitled",
            "author": p.get("author", "Anonymous"),
            "tool": "Stable Diffusion",
            "type": "image",
            "prompt": title,
            "tags": _extract_tags(title),
            "likes": p.get("score", 0),
            "image_url": url_overridden,
            "width": 0, "height": 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
        })
    print(f"[Reddit] 获取 {len(works)} 条有效作品")
    return works


# ===================== 2. AI 评分 =====================

def ai_score_batch(works, api_key):
    """批量 AI 评分（减少 API 调用次数）"""
    if not api_key or not works:
        return

    print(f"[AI评分] 开始评估 {len(works)} 件作品...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    scored = 0
    for i, w in enumerate(works):
        prompt_snippet = w.get("prompt", "")[:400]
        tags_str = ", ".join(w.get("tags", [])[:8])

        system_prompt = """你是AI艺术评审专家。对每件AI作品从5个维度评分(1-10)，并给出20字内中文评语。
严格只输出JSON，不要任何其他文字：
{"creativity":8.5,"technical":8.0,"aesthetic":9.0,"novelty":7.5,"overall":8.3,"review":"构图大胆色彩和谐"}"""

        user_msg = f"""作品信息：
提示词: {prompt_snippet}
标签: {tags_str}
点赞: {w.get('likes', 0)}

请评分："""

        try:
            resp = requests.post(
                DEEPSEEK_URL,
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.6,
                    "max_tokens": 200,
                },
                timeout=25,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            m = re.search(r'\{[^{}]*"overall"[^{}]*\}', content)
            if m:
                scores = json.loads(m.group())
                w["ai_score"] = {
                    "creativity": round(scores.get("creativity", 7), 1),
                    "technical": round(scores.get("technical", 7), 1),
                    "aesthetic": round(scores.get("aesthetic", 7), 1),
                    "novelty": round(scores.get("novelty", 7), 1),
                    "overall": round(scores.get("overall", 7), 1),
                    "review": scores.get("review", "")[:30],
                }
                scored += 1
                print(f"  [{i+1}/{len(works)}] {w['title'][:30]} → {w['ai_score']['overall']}分")

            time.sleep(0.5)  # 避免触发限流

        except Exception as e:
            print(f"  [{i+1}/{len(works)}] ❌ {w['title'][:30]}: {e}")
            # 评分失败给默认分
            w["ai_score"] = _default_score(w)

    print(f"[AI评分] 完成 {scored}/{len(works)} 件")


def _default_score(work):
    """无 API 时的默认评分（基于点赞数估算）"""
    likes = work.get("likes", 0)
    base = min(8.5, 6.0 + (likes / 500))
    return {
        "creativity": round(base - 0.3, 1),
        "technical": round(base, 1),
        "aesthetic": round(base + 0.2, 1),
        "novelty": round(base - 0.5, 1),
        "overall": round(base, 1),
        "review": "热门作品",
    }


# ===================== 3. 图片处理 =====================

def download_and_save(work):
    """下载图片、压缩、保存到 showcase/ 目录"""
    try:
        resp = requests.get(work["image_url"], headers={"User-Agent": "JiuWanAI/1.0"}, timeout=30)
        resp.raise_for_status()

        img = Image.open(BytesIO(resp.content))
        # 转 RGB（处理 RGBA/CMYK）
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
            # 白色背景
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, img).convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 等比缩放
        w, h = img.size
        if w > IMAGE_MAX_WIDTH:
            ratio = IMAGE_MAX_WIDTH / w
            img = img.resize((IMAGE_MAX_WIDTH, int(h * ratio)), Image.LANCZOS)

        # 文件名
        file_id = work["source_id"].replace("/", "_").replace(":", "_")
        filename = f"{file_id}.jpg"
        filepath = SHOWCASE_DIR / filename

        img.save(filepath, "JPEG", quality=82, optimize=True)
        work["image"] = f"showcase/{filename}"
        print(f"  📥 图片已保存: {filename} ({img.size[0]}x{img.size[1]})")
        return True
    except Exception as e:
        print(f"  ❌ 图片下载失败: {e}")
        return False


# ===================== 4. 去重 =====================

def load_existing():
    """加载现有作品"""
    if SHOWCASE_JSON.exists():
        with open(SHOWCASE_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def dedup(new_works, existing):
    """基于 source_id 和 prompt 相似度去重"""
    existing_ids = {w.get("source_id", "") for w in existing}
    existing_prompts = {_norm(w.get("prompt", "")) for w in existing}

    filtered = []
    for w in new_works:
        if w["source_id"] in existing_ids:
            continue
        if _norm(w.get("prompt", "")) in existing_prompts:
            continue
        filtered.append(w)

    print(f"[去重] {len(new_works)} → {len(filtered)} 件新作品")
    return filtered


def _norm(text):
    """文本归一化（用于去重比较）"""
    return re.sub(r'\s+', ' ', text.lower().strip())[:100]


# ===================== 5. 发布 =====================

def publish(works, existing):
    """更新 showcase.json 并 Git 提交"""
    # 按 AI 综合评分排序
    works.sort(key=lambda w: w.get("ai_score", {}).get("overall", 0), reverse=True)

    # 合并
    all_works = works + existing

    # 重新分配 ID
    for i, w in enumerate(all_works):
        w["id"] = i + 1

    # 写入
    with open(SHOWCASE_JSON, "w", encoding="utf-8") as f:
        json.dump(all_works, f, ensure_ascii=False, indent=2)

    print(f"[发布] showcase.json 已更新（共 {len(all_works)} 件作品）")

    # Git 操作
    try:
        subprocess.run(["git", "-C", str(BASE_DIR), "add", "showcase.json", "showcase/"], check=True)
        status = subprocess.run(
            ["git", "-C", str(BASE_DIR), "status", "--porcelain"],
            capture_output=True, text=True
        )
        if status.stdout.strip():
            subprocess.run(
                ["git", "-C", str(BASE_DIR), "commit", "-m",
                 f"auto: 每日AI作品更新 - {len(works)}件新作 ({datetime.now().strftime('%m-%d')})"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(BASE_DIR), "push", GIT_REMOTE, GIT_BRANCH],
                check=True, timeout=60,
            )
            print(f"[发布] ✅ 已推送到 GitHub")
        else:
            print(f"[发布] 无变更，跳过推送")
    except Exception as e:
        print(f"[发布] ⚠️ Git 操作失败: {e}")
        print(f"[发布] showcase.json 已本地更新，请手动推送")


# ===================== 辅助函数 =====================

def _gen_title(prompt):
    """从 prompt 生成简短标题"""
    # 取第一个逗号前的内容，或前40个字符
    parts = prompt.replace("\n", " ").split(",")
    title = parts[0].strip()
    if len(title) > 50:
        title = title[:47] + "..."
    return title or "AI Artwork"


def _extract_tags(text):
    """从文本提取关键词标签"""
    keywords = [
        "cyberpunk", "fantasy", "anime", "realistic", "photorealistic",
        "portrait", "landscape", "sci-fi", "dark", "neon", "nature",
        "character", "concept art", "digital art", "illustration",
        "国风", "古风", "赛博", "水墨", "机甲", "幻想", "暗黑",
        "仙侠", "武侠", "治愈", "科幻", "神话",
    ]
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
    return found[:5] if found else ["AI艺术"]


def _guess_tool(prompt, item):
    """推测使用的工具"""
    prompt_lower = prompt.lower()
    model_name = str(item.get("model", "")).lower() if isinstance(item, dict) else ""

    if "midjourney" in prompt_lower or "midjourney" in model_name:
        return "Midjourney"
    if "dall-e" in prompt_lower or "dalle" in model_name:
        return "DALL·E"
    if "flux" in prompt_lower or "flux" in model_name:
        return "Flux"
    if "sd3" in model_name or "stable diffusion 3" in prompt_lower:
        return "Stable Diffusion 3"
    return "Stable Diffusion"


# ===================== 主流程 =====================

def main():
    print("=" * 60)
    print(f"  九万AI 自动抓取系统 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 0. 确保目录存在
    SHOWCASE_DIR.mkdir(exist_ok=True)

    # 1. 加载现有作品
    existing = load_existing()
    print(f"[现有] {len(existing)} 件作品")

    # 2. 多源抓取
    all_new = []
    all_new.extend(fetch_civitai(CIVITAI_LIMIT))
    all_new.extend(fetch_reddit_sd(20))

    if not all_new:
        print("[结果] 未获取到新作品，结束")
        return

    # 3. 去重
    new_works = dedup(all_new, existing)
    if not new_works:
        print("[结果] 全部重复，无需更新")
        return

    # 4. AI 评分
    if DEEPSEEK_KEY:
        ai_score_batch(new_works, DEEPSEEK_KEY)
    else:
        print("[AI评分] ⚠️ 未配置 DEEPSEEK_API_KEY，使用估算评分")
        for w in new_works:
            w["ai_score"] = _default_score(w)

    # 5. 筛选：只保留高分作品
    qualified = [w for w in new_works if w["ai_score"]["overall"] >= MIN_AI_SCORE]
    print(f"[筛选] {len(new_works)} → {len(qualified)} 件（≥{MIN_AI_SCORE}分）")

    if not qualified:
        print("[结果] 无高分作品，结束")
        return

    # 6. 限制每天新增数量，取 top N
    qualified = qualified[:MAX_NEW_PER_DAY]

    # 7. 下载图片
    print(f"\n[下载] 开始下载 {len(qualified)} 张图片...")
    success = []
    for w in qualified:
        if download_and_save(w):
            success.append(w)
    print(f"[下载] 成功 {len(success)}/{len(qualified)}")

    if not success:
        print("[结果] 图片下载全部失败，结束")
        return

    # 8. 发布
    print()
    publish(success, existing)

    print()
    print("=" * 60)
    print(f"  ✅ 完成！新增 {len(success)} 件作品，总计 {len(existing) + len(success)} 件")
    print(f"  🌐 网站: https://jiuwanai.com")
    print("=" * 60)


if __name__ == "__main__":
    main()
