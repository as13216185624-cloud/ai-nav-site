from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io, os, time, uuid, logging, requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI 电商作图 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
DASHSCOPE_API_KEY = "sk-ws-H.RPHEYDR.xEV5.MEUCIQC-fjnkgnR0WeGXAGJxpCSMLNta3GmgYhvXaf2kx7m_RAIgQ-4gMdqLZPnEyjm7l6Bwo7G_smugZvwk_9HKQ-pKrOw"
DASHSCOPE_BG_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/background-generation/generation/"
TEMP_DIR = "/opt/rembg-server/temp_images"

# Scene presets
SCENE_PROMPTS = {
    "marble": "luxury white marble surface, soft natural window light, high-end product photography, elegant and clean",
    "wood": "warm wooden tabletop, golden natural sunlight, rustic cozy aesthetic, lifestyle product shot",
    "minimal": "pure white studio background, soft diffused lighting, minimalist product photography, clean composition",
    "nature": "fresh green plants and natural sunlight, outdoor botanical setting, organic lifestyle photography",
    "pink": "soft pink pastel background, dreamy romantic aesthetic, feminine beauty product photography",
    "studio": "professional photography studio with gradient gray background, commercial lighting setup, clean product shot",
    "warm": "cozy warm interior, golden hour sunlight through window, lifestyle home photography",
    "dark": "dramatic dark background with rim lighting, premium luxury product shot, high contrast",
    "kitchen": "modern bright kitchen counter, natural morning light, clean and fresh product photography",
    "desk": "minimalist white desk setup, soft ambient light, tech and lifestyle product photography",
}

# 模型字典
models = {}

@app.on_event("startup")
async def load_models():
    from rembg import new_session
    os.makedirs(TEMP_DIR, exist_ok=True)
    logger.info("加载抠图模型...")
    try:
        models["isnet"] = new_session("isnet-general-use")
        logger.info("isnet (Pro版) 模型加载完成")
    except Exception as e:
        logger.error(f"isnet 加载失败: {e}")
    try:
        models["u2net"] = new_session("u2net")
        logger.info("u2net (免费版) 模型加载完成")
    except Exception as e:
        logger.error(f"u2net 加载失败: {e}")
    logger.info(f"已加载 {len(models)} 个模型: {list(models.keys())}")

@app.get("/health")
async def health():
    return {"status": "ok", "models": list(models.keys())}

@app.get("/temp/{filename}")
async def serve_temp(filename: str):
    filepath = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(filepath) or ".." in filename:
        raise HTTPException(status_code=404)
    return FileResponse(filepath, media_type="image/png")

def do_removebg(image_data: bytes, model_name: str) -> bytes:
    from rembg import remove
    model = models.get(model_name)
    if model is None:
        raise HTTPException(status_code=503, detail=f"模型 {model_name} 未就绪")
    input_image = Image.open(io.BytesIO(image_data))
    if input_image.mode != "RGB":
        input_image = input_image.convert("RGB")
    output_image = remove(input_image, session=model, post_process_mask=True)
    buf = io.BytesIO()
    output_image.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.getvalue()

@app.post("/api/removebg")
async def remove_bg_free(file: UploadFile = File(...)):
    """免费版抠图 (u2net)"""
    start = time.time()
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")
    try:
        result = do_removebg(data, "u2net")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {e}")
    elapsed = time.time() - start
    logger.info(f"免费版抠图完成，耗时 {elapsed:.2f}s")
    return Response(content=result, media_type="image/png",
                    headers={"X-Process-Time": f"{elapsed:.2f}", "X-Model": "u2net"})

@app.post("/api/removebg-pro")
async def remove_bg_pro(file: UploadFile = File(...)):
    """Pro版抠图 (isnet，边缘更精细)"""
    start = time.time()
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")
    try:
        result = do_removebg(data, "isnet")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {e}")
    elapsed = time.time() - start
    logger.info(f"Pro版抠图完成，耗时 {elapsed:.2f}s")
    return Response(content=result, media_type="image/png",
                    headers={"X-Process-Time": f"{elapsed:.2f}", "X-Model": "isnet"})

@app.post("/api/generate-scene")
async def generate_scene(file: UploadFile = File(...), scene: str = Form("minimal")):
    """AI 场景图生成 — 给抠好的透明图换上专业电商场景"""
    start = time.time()
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传透明 PNG 图片")
    
    img_data = await file.read()
    if len(img_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")
    
    # Ensure RGBA
    img = Image.open(io.BytesIO(img_data))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_data = buf.getvalue()
    
    # Encode image as base64 for DashScope (avoids public URL requirement)
    import base64 as b64
    img_base64 = b64.b64encode(img_data).decode("utf-8")
    base64_url = f"data:image/png;base64,{img_base64}"
    
    prompt = SCENE_PROMPTS.get(scene, SCENE_PROMPTS["minimal"])
    
    logger.info(f"AI场景生成: scene={scene}, image_size={len(img_data)}bytes")
    
    # Create DashScope task with base64 image
    headers = {
        "X-DashScope-Async": "enable",
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "wanx-background-generation-v2",
        "input": {
            "base_image_url": base64_url,
            "ref_prompt": prompt
        },
        "parameters": {"model_version": "v3", "n": 1}
    }
    
    resp = requests.post(DASHSCOPE_BG_URL, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"DashScope 错误: {resp.text[:200]}")
    
    task_id = resp.json()["output"]["task_id"]
    logger.info(f"DashScope任务已创建: {task_id}")
    
    # Poll for result (max 60s)
    for i in range(60):
        time.sleep(1)
        r = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}
        )
        result = r.json()
        status = result["output"]["task_status"]
        if status == "SUCCEEDED":
            img_url = result["output"]["results"][0]["url"]
            img_resp = requests.get(img_url, timeout=30)
            elapsed = time.time() - start
            logger.info(f"AI场景生成完成，耗时 {elapsed:.1f}s")
            return Response(content=img_resp.content, media_type="image/png",
                          headers={"X-Process-Time": f"{elapsed:.1f}", "X-Scene": scene})
        elif status == "FAILED":
            raise HTTPException(status_code=500, detail="场景生成失败，请换张图片或场景重试")
    
    raise HTTPException(status_code=504, detail="场景生成超时，请重试")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
