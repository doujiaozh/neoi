#!/usr/bin/env python3
"""简化测试脚本 - 仅测试核心记忆功能"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.memory.compressor import MemoryCompressor

async def test_memory():
    print("NeoAI Memory System Test")
    print("=" * 40)
    
    compressor = MemoryCompressor()
    await compressor.initialize()
    print("✅ Memory compressor initialized")
    
    # 测试压缩
    test_text = "NeoAI is an innovative distributed AI system that provides next-generation computing capabilities."
    print(f"\nTesting compression with text: {test_text}")
    
    result = compressor.compress(test_text, level=0)
    print(f"✅ Compression result: {result}")
    
    # 测试检索（异步）
    results = await compressor.recall("distributed AI", top_k=3)
    print(f"✅ Retrieval results count: {len(results)}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_memory())
