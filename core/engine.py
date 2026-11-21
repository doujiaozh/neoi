#!/usr/bin/env python3
"""
NeoAI Core Engine (Lightweight Version)
主引擎 - 协调所有核心模块
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入核心模块
from core.memory.compressor import MemoryCompressor
from core.memory.retriever import MemoryRetriever
from core.decoder.fast_decoder import FastDecoder
from core.security.reverse_engineer import SecurityExpert
from distributed.p2p_network import P2PNetwork
from distributed.compute_cluster import ComputeCluster
from distributed.scheduler import TaskScheduler


class NeoAIEngine:
    """NeoAI 核心引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化核心模块（轻量级）
        self.memory_compressor = MemoryCompressor()
        self.memory_retriever = MemoryRetriever()
        self.fast_decoder = FastDecoder()
        self.security_expert = SecurityExpert()
        
        # 分布式组件
        self.p2p_network = P2PNetwork()
        self.compute_cluster = ComputeCluster()
        self.task_scheduler = TaskScheduler()
        
        self.is_running = False
    
    async def initialize(self):
        """初始化引擎"""
        self.logger.info("Initializing NeoAI engine...")
        
        # 初始化记忆系统
        await self.memory_compressor.initialize()
        await self.memory_retriever.initialize()
        
        # 初始化解码器
        await self.fast_decoder.initialize()
        
        # 初始化分布式网络
        await self.p2p_network.start()
        
        # 启动计算集群
        await self.compute_cluster.initialize()
        
        self.logger.info("NeoAI engine initialized successfully")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        request_type = request.get("type")
        
        if request_type == "memory_compress":
            return await self._compress_memory(request)
        elif request_type == "memory_retrieve":
            return await self._retrieve_memory(request)
        elif request_type == "distribute_task":
            return await self._distribute_task(request)
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    async def _compress_memory(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """压缩记忆"""
        text = request.get("text", "")
        level = request.get("level", 0)
        
        result = self.memory_compressor.compress(text, level)
        
        if result.get("success"):
            return {"status": "success", "data": result}
        else:
            return {"status": "error", "message": result.get("error")}
    
    async def _retrieve_memory(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """检索记忆"""
        query = request.get("query", "")
        top_k = request.get("top_k", 5)
        
        results = await self.memory_retriever.retrieve(query, top_k)
        
        return {
            "status": "success",
            "data": [r.to_dict() for r in results],
            "count": len(results)
        }
    
    async def _distribute_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """分发任务"""
        from distributed.compute_cluster import TaskPriority
        
        task_data = request.get("task", {})
        
        task_id = await self.compute_cluster.submit_task(
            "memory_task",
            task_data,
            TaskPriority.NORMAL
        )
        
        return {
            "status": "success",
            "task_id": task_id
        }
    
    async def start(self):
        """启动引擎"""
        self.is_running = True
        await self.initialize()
        self.logger.info("NeoAI engine running")
    
    async def shutdown(self):
        """关闭引擎"""
        self.is_running = False
        await self.p2p_network.stop()
        await self.compute_cluster.shutdown()
        self.logger.info("NeoAI engine shutdown complete")


async def main():
    """主函数"""
    print("NeoAI - Next Generation AI Architecture")
    print("=" * 50)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('neoi.log')
        ]
    )
    
    # 创建引擎实例
    engine = NeoAIEngine()
    
    try:
        # 启动引擎
        await engine.start()
        
        print("\nExample interactions:")
        print("Query memory: type='memory_retrieve', query='What is AI'")
        print("Compress text: type='memory_compress', text='...'")
        print("Distribute task: type='distribute_task', task={...}")
        
        # 示例测试
        test_requests = [
            {"type": "memory_compress", "text": "NeoAI is an innovative distributed AI system"},
            {"type": "memory_retrieve", "query": "distributed AI"},
            {"type": "distribute_task", "task": {"algorithm": "test", "data": "sample"}}
        ]
        
        for request in test_requests:
            print(f"\nExecuting: {request}")
            result = await engine.process_request(request)
            print(f"Result: {result}")
        
    except KeyboardInterrupt:
        print("\nShutting down NeoAI...")
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
