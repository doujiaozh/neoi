# NeoAI 快速开始指南

## 🚀 5分钟快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/neoi/neoi.git
cd neoi

# 安装 Python 依赖
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 运行核心引擎

```bash
python main.py
```

### 3. 查看系统状态

```python
# 在另一个 Python 会话中
from core.engine import NeoAIEngine

engine = NeoAIEngine()
await engine.start()

# 检查状态
status = engine.get_status()
print(status)
```

## 📚 进一步学习

- [系统架构](docs/architecture.md)
- [API 文档](docs/api.md)
- [部署指南](deployment/README.md)
- [性能优化](docs/performance.md)

## 🔧 常见问题

### Q: 依赖安装失败？
A: 确保 Python >= 3.10，安装系统依赖：`apt-get install build-essential`

### Q: CUDA 设备未检测到？
A: 确保安装 NVIDIA 驱动和 CUDA Toolkit

### Q: 内存不足？
A: 使用模型量化：`modelquantization=True`

## 💻 Docker 部署

```bash
# 使用 Docker
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📞 获取帮助

- [GitHub Issues](https://github.com/neoi/neoi/issues)
- [Discord 社区](https://discord.gg/neoi)
- [文档中心](https://docs.neoi.ai)

---

**🎉 你已经准备好探索 NeoAI 了!**
