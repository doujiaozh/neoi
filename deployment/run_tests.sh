#!/bin/bash
# NeoAI - 测试套件运行脚本
# 执行所有单元测试和集成测试

set -e

echo "🧪 NeoAI 测试套件"
echo "=================="

cd neoi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装测试依赖
echo "🔧 安装测试依赖..."
pip install -q pytest pytest-asyncio

# 运行测试
echo "🚀 运行单元测试..."
pytest tests/ -v --tb=short --color=yes

# 生成覆盖率报告
echo "📊 生成覆盖率报告..."
pytest tests/ --cov=core --cov=distributed --cov-report=html --cov-report=term

# 显示覆盖率摘要
echo ""
echo "📈 覆盖率统计:"
coverage report -m

echo ""
echo "✅ 测试完成!"
echo "📂 HTML 报告: htmlcov/index.html"
