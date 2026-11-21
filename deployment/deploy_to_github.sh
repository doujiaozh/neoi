#!/bin/bash
# NeoAI - 一键部署到GitHub
# 自动化构建、测试、打包和部署

set -e

echo "🚀 NeoAI 一键部署"
echo "=================="

# 配置
PROJECT_NAME="neoi"
BRANCH="main"

# 步骤 1: 环境准备
echo "📋 步骤 1: 环境准备..."

if ! command -v git &> /dev/null; then
    echo "❌ 需要先安装 Git"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ 需要先安装 Docker"
    exit 1
fi

echo "✅ 环境准备完成"

# 步骤 2: 代码检查
echo "🔍 步骤 2: 代码质量检查..."

cd "$PROJECT_NAME"

# Python 依赖安装
echo "📦 安装 Python 依赖..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# 运行测试
echo "🧪 运行单元测试..."
python -m pytest tests/ -q

echo "✅ 测试通过"

# 步骤 3: Docker 构建
echo "🐳 步骤 3: 构建 Docker 镜像..."

docker build -t neoi/neoi:latest .
docker tag neoi/neoi:latest neoi/neoi:dev

echo "✅ Docker 镜像构建完成"

# 步骤 4: GitHub 部署
echo "🌐 步骤 4: 推送到 GitHub..."

cd ..

# 配置 Git
git config user.name "NeoAI"
git config user.email "neoi@example.com"

# 初始化 Git 仓库
if [ ! -d "$PROJECT_NAME/.git" ]; then
    cd "$PROJECT_NAME"
    git init
    git add .
    git commit -m "feat: initial release - NeoAI Core Engine"
    git branch -M main
    git remote add origin https://github.com/neoi/neoi.git
    cd ..
fi

# 拉取最新代码
cd "$PROJECT_NAME"
git pull origin main

# 提交更改
git add .
git commit -m "feat: update deployment configuration"

# 推送到 GitHub
echo "📤 推送到 GitHub..."
git push origin main --force

echo "✅ 代码已推送到 GitHub"

# 步骤 5: 创建 GitHub Release
echo "🏷️ 步骤 5: 创建 Release..."

# 获取版本代码
VERSION="v1.0.0"
TAG="$VERSION"

# 创建 Release (需要 GitHub Token)
curl -X POST \
  -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
  -d "{\"tag_name\": \"$TAG\", \"target_commitish\": \"main\", \"name\": \"$VERSION\", \"body\": \"NeoAI 初始版本发布\", \"draft\": false, \"prerelease\": false}" \
  "https://api.github.com/repos/neoi/neoi/releases"

echo "✅ Release 创建完成"

# 步骤 6: 部署到 DockerHub
echo "🐋 步骤 6: 部署到 DockerHub..."

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push neoi/neoi:latest
docker push neoi/neoi:dev

echo "✅ DockerHub 推送完成"

# 完成
echo ""
echo "🎉 部署完成!"
echo ""
echo "📊 部署摘要:"
echo "  - GitHub 仓库: https://github.com/neoi/neoi"
echo "  - Docker 镜像: neoi/neoi:latest"
echo "  - 版本: $VERSION"
echo "  - 状态: ✅ 成功"
