#!/usr/bin/env python3
"""
Main Entry Point
NeoAI 主入口
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import NeoAIEngine


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
