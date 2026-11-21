# NeoAI - 下一代分布式AI架构

> 超越边界的计算引擎 | 无限上下文 · 极速推理 · 分布式算力聚合

## 🎯 项目愿景

构建一个**可扩展的、模块化的AI系统**，通过：
- **记忆压缩**：基于LLM的层次化记忆系统
- **安全推理**：逆向工程/安全分析专用模块
- **分布式计算**：P2P算力聚合协议
- **全平台部署**：Web/PC/边缘设备自适应

## 📦 核心模块

```
neoi/
├── core/               # 核心引擎
│   ├── engine.py       # 主引擎
│   ├── memory/         # 记忆压缩系统
│   ├── decoder/        # 极速解码器
│   └── security/       # 安全推理模块
├── distributed/        # 分布式协议
│   ├── p2p_network.py
│   └──算力聚合算法
├── deployment/         # 部署脚本
└── docs/               # 文档
```

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动核心引擎
python main.py

# 部署到GitHub
./deploy.sh
```

## 📄 许可证

MIT License - 开源、自由、共享
