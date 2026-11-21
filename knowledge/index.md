# NeoAI 知识库文档索引

## 核心架构
- [系统架构设计](../docs/architecture.md) - 完整架构设计文档

## 核心模块
- [记忆压缩系统](../core/memory/compressor.py) - 层次化记忆压缩
- [记忆检索器](../core/memory/retriever.py) - 语义检索技术
- [极速解码器](../core/decoder/fast_decoder.py) - 高性能推理引擎
- [安全推理模块](../core/security/reverse_engineer.py) - 逆向工程分析

## 分布式计算
- [P2P网络层](../distributed/p2p_network.py) - 分布式通信协议
- [计算集群](../distributed/compute_cluster.py) - 算力聚合调度
- [任务调度器](../distributed/scheduler.py) - 优先级任务管理

## 部署配置
- [Docker 部署](../Dockerfile) - 容器化配置
- [GitHub Actions](../.github/workflows/ci.yml) - CI/CD 流水线
- [一键部署脚本](../deployment/deploy.sh) - 自动化部署

## 测试
- [记忆测试](../tests/test_memory.py) - 记忆系统测试
- [安全测试](../tests/test_security.py) - 安全模块测试
- [集群测试](../tests/test_cluster.py) - 分布式测试
- [P2P测试](../tests/test_p2p.py) - 网络层测试
