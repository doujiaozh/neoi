#!/usr/bin/env python3
"""
记忆系统测试
"""

import asyncio
import pytest
from core.memory.compressor import MemoryCompressor, MemoryLevel


@pytest.mark.asyncio
async def test_memory_compression():
    """测试记忆压缩功能"""
    compressor = MemoryCompressor()
    await compressor.initialize()
    
    test_text = "这是一个测试文本，用于测试NeoAI的记忆压缩功能。NeoAI是一个创新的分布式AI系统架构。"
    result = await compressor.compress(test_text, MemoryLevel.SHORT_TERM)
    
    assert result["success"] is True
    assert "id" in result
    assert "summary" in result
    assert "compression_ratio" in result
    
    print(f"✅ 记忆压缩完成: {result['compression_ratio']:.2f}x")


@pytest.mark.asyncio
async def test_memory_retrieval():
    """测试记忆检索功能"""
    compressor = MemoryCompressor()
    await compressor.initialize()
    
    # 存储一些记忆
    await compressor.compress("NeoAI是分布式AI系统", MemoryLevel.SHORT_TERM)
    await compressor.compress("使用P2P网络聚合算力", MemoryLevel.MEDIUM_TERM)
    
    # 检索记忆
    results = await compressor.recall("分布式AI系统", top_k=2)
    
    assert len(results) > 0
    assert all("memory" in r and "similarity" in r for r in results)
    
    print(f"✅ 记忆检索完成: {len(results)} 个结果")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
