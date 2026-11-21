#!/bin/bash
# NeoAI - 系统架构验证脚本
# 验证所有核心模块是否正常工作

echo "🔍 NeoAI 系统架构验证"
echo "====================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 验证计数器
PASS=0
FAIL=0

# 验证函数
check_module() {
    local name=$1
    local command=$2
    
    echo -n "验证 $name... "
    
    if eval $command > /dev/null 2>&1; then
        echo -e " ${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e " ${RED}❌ FAIL${NC}"
        ((FAIL++))
    fi
}

check_file_exists() {
    local name=$1
    local path=$2
    
    echo -n "检查 $name... "
    
    if [ -f "$path" ]; then
        echo -e " ${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e " ${RED}❌ FAIL${NC}"
        ((FAIL++))
    fi
}

echo ""
echo "📋 文件完整性检查"
echo "-----------------"

check_file_exists "README.md" "neoi/README.md"
check_file_exists "main.py" "neoi/main.py"
check_file_exists "engine.py" "neoi/core/engine.py"
check_file_exists "compressor.py" "neoi/core/memory/compressor.py"
check_file_exists "fast_decoder.py" "neoi/core/decoder/fast_decoder.py"
check_file_exists "reverse_engineer.py" "neoi/core/security/reverse_engineer.py"
check_file_exists "p2p_network.py" "neoi/distributed/p2p_network.py"
check_file_exists "compute_cluster.py" "neoi/distributed/compute_cluster.py"
check_file_exists "scheduler.py" "neoi/distributed/scheduler.py"
check_file_exists "Dockerfile" "neoi/Dockerfile"
check_file_exists "requirements.txt" "neoi/requirements.txt"

echo ""
echo "🐳 环境检查"
echo "-----------"

check_module "Python 版本" "python3 --version"
check_module "Git" "git --version"
check_module "Docker" "docker --version"

echo ""
echo "🧪 模块功能验证"
echo "----------------"

cd neoi

# 测试导入
check_module "核心模块导入" "python3 -c 'from core.engine import NeoAIEngine'"
check_module "记忆模块导入" "python3 -c 'from core.memory.compressor import MemoryCompressor'"
check_module "解码器导入" "python3 -c 'from core.decoder.fast_decoder import FastDecoder'"
check_module "安全模块导入" "python3 -c 'from core.security.reverse_engineer import SecurityExpert'"
check_module "分布式模块导入" "python3 -c 'from distributed.p2p_network import P2PNetwork'"

echo ""
echo "📊 验证结果"
echo "----------"
echo -e "通过: ${GREEN}$PASS${NC}"
echo -e "失败: ${RED}$FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 所有验证通过!NeoAI 系统就绪${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 部分验证失败，请检查配置${NC}"
    exit 1
fi
