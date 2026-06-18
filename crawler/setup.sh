#!/bin/bash
# 九万AI 服务器部署脚本
# 在腾讯云 Ubuntu 上执行：bash setup.sh

set -e

echo "========================================"
echo "  九万AI 自动抓取系统 - 服务器部署"
echo "========================================"

# 1. 安装系统依赖
echo "[1/5] 安装系统依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv git

# 2. 克隆仓库
echo "[2/5] 克隆仓库..."
cd /home
if [ -d "ai-nav-site" ]; then
    echo "  仓库已存在，执行 git pull..."
    cd ai-nav-site
    git pull origin main
else
    git clone https://github.com/as13216185624-cloud/ai-nav-site.git
    cd ai-nav-site
fi

# 3. 安装 Python 依赖
echo "[3/5] 安装 Python 依赖..."
pip3 install -q requests Pillow

# 4. 设置环境变量
echo "[4/5] 配置环境变量..."
# ⚠️ 请在 .env 文件中填入你的 DeepSeek API Key
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# DeepSeek API Key（用于AI评分，在 https://platform.deepseek.com 获取）
# 新用户注册送500万tokens免费额度，足够用很久
DEEPSEEK_API_KEY=你的key填这里
EOF
    echo "  ⚠️ .env 文件已创建，请编辑填入 DEEPSEEK_API_KEY"
else
    echo "  .env 已存在，跳过"
fi

# 5. 设置定时任务
echo "[5/5] 配置 cron 定时任务（每天凌晨3点执行）..."
CRON_JOB="0 3 * * * cd /home/ai-nav-site && . .env && python3 crawler/main.py >> /home/ai-nav-site/crawler/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "crawler/main.py"; echo "$CRON_JOB") | crontab -
echo "  ✅ cron 已配置"

echo ""
echo "========================================"
echo "  ✅ 部署完成！"
echo "========================================"
echo ""
echo "📋 后续步骤："
echo "1. 编辑 .env 填入 DeepSeek API Key:"
echo "   nano /home/ai-nav-site/.env"
echo ""
echo "2. 配置 Git 推送凭据（用你的 GitHub Token）:"
echo "   git config --global user.email 'jiuwai@coze.email'"
echo "   git config --global user.name 'JiuWanAI Bot'"
echo "   git remote set-url origin https://TOKEN@github.com/as13216185624-cloud/ai-nav-site.git"
echo ""
echo "3. 手动运行一次测试:"
echo "   cd /home/ai-nav-site && . .env && python3 crawler/main.py"
echo ""
echo "4. 查看定时任务日志:"
echo "   tail -f /home/ai-nav-site/crawler/cron.log"
