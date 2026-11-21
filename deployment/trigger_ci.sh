#!/bin/bash
# NeoAI - GitHub Actions 手动触发脚本
# 用于手动触发 CI/CD 流水线

echo "🚀 手动触发 CI/CD 流水线..."

# 检查 GitHub CLI 是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ 需要先安装 GitHub CLI"
    exit 1
fi

# 触发 Workflow
gh workflow run ci.yml -r main

echo "✅ CI/CD 流水线已触发"
echo "📊 查看运行状态: https://github.com/neoi/neoi/actions"
