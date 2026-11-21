# NeoAI - 核心引擎

## 项目结构

neoi/
├── main.py              # 入口点
├── core/
│   ├── engine.py        # 主引擎
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── compressor.py    # 记忆压缩
│   │   └── retriever.py   # 记忆检索
│   ├── decoder/
│   │   ├── __init__.py
│   │   ├── fast_decoder.py  # 极速解码器
│   │   └── cuda_opt.py    # CUDA优化
│   └── security/
│       ├── __init__.py
│       ├── reverse_engineer.py  # 逆向工程
│       └── protocol_fuzz.py   # 协议模糊测试
├── distributed/
│   ├── __init__.py
│   ├── p2p_network.py     # P2P网络
│   ├── compute_cluster.py # 计算集群
│   └── scheduler.py       # 任务调度
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── deploy.sh
│   └── setup_github.sh
├── tests/
│   ├── test_memory.py
│   ├── test_decoder.py
│   └── test_security.py
├── requirements.txt
└── pyproject.toml
