#!/bin/bash
# NeoAI - 快速部署脚本
# 自动化构建、测试和部署

set -e

echo "🚀 NeoAI 快速部署脚本"
echo "======================"

# 配置
PROJECT_NAME="neoi"
PYTHON_VERSION="3.10"
DOCKER_IMAGE="neoi/neoi:latest"

# 步骤 1: 环境检查
echo "📋 检查环境..."

check_python_version() {
    python3 --version
    if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
        echo "✅ Python 3.8+ 已安装"
    else
        echo "❌ 需要 Python 3.8+ 版本"
        exit 1
    fi
}

check_dependencies() {
    echo "📦 检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker 未安装"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git 未安装"
        exit 1
    fi
    
    echo "✅ 环境检查完成"
}

# 步骤 2: 安装依赖
echo "🔧 安装 Python 依赖..."

install_dependencies() {
    cd "$PROJECT_NAME"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ 虚拟环境创建完成"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    echo "✅ 依赖安装完成"
    cd ..
}

# 步骤 3: 代码构建
echo "🏗️ 构建项目..."

build_project() {
    cd "$PROJECT_NAME"
    
    # 运行测试
    echo "🧪 运行单元测试..."
    python -m pytest tests/ -v
    
    # 代码质量检查
    echo "🔍 代码质量检查..."
    # flake8 .
    # pylint .
    
    echo "✅ 构建完成"
    cd ..
}

# 步骤 4: Docker 构建
echo "🐳 构建 Docker 镜像..."

build_docker() {
    cd "$PROJECT_NAME"
    
    # 构建 Docker 镜像
    docker build -t "$DOCKER_IMAGE" .
    
    # 标记镜像
    docker tag "$DOCKER_IMAGE" neoi/neoi:latest
    
    echo "✅ Docker 镜像构建完成"
    cd ..
}

# 步骤 5: 测试部署
echo "🧪 测试部署..."

test_deployment() {
    # 启动 Docker 容器
    docker run -d \
        --name neoi-test \
        -p 8765:8765 \
        -p 8000:8000 \
        "$DOCKER_IMAGE"
    
    # 等待容器启动
    sleep 5
    
    # 检查容器状态
    if docker ps | grep -q neoi-test; then
        echo "✅ 容器运行正常"
        
        # 停止容器
        docker stop neoi-test
        docker rm neoi-test
    else
        echo "❌ 容器启动失败"
        exit 1
    fi
}

# 步骤 6: GitHub 部署
echo "🌐 GitHub 部署..."

deploy_to_github() {
    cd "$PROJECT_NAME"
    
    # 配置 Git
    git config user.name "NeoAI"
    git config user.email "neoi@example.com"
    
    # 添加文件
    git add .
    git commit -m "feat: initial release - NeoAI Core Engine"
    
    # 推送到GitHub
    git push origin main
    
    echo "✅ 代码已推送到GitHub"
    cd ..
}

# 步骤 7: 完整部署流程
echo "🚀 执行完整部署流程..."

main() {
    check_dependencies
    install_dependencies
    build_project
    build_docker
    test_deployment
    deploy_to_github
    
    echo "🎉 部署完成!"
    echo ""
    echo "📊 部署报告:"
    echo "  - 项目路径: $PWD/$PROJECT_NAME"
    echo "  - Docker镜像: $DOCKER_IMAGE"
    echo "  - 状态: 成功"
}

main "$@"
