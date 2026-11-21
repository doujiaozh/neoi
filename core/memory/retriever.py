#!/usr/bin/env python3
"""
Memory Retriever (Lightweight Version)
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from .compressor import MemoryChunk, MemoryCompressor

@dataclass
class MemoryResult:
    memory_dict: dict  # 修复：改用字典接收
    similarity: float
    rank: int
    
    def to_dict(self):
        return {
            "memory": self.memory_dict,
            "similarity": float(self.similarity),
            "rank": self.rank
        }

class MemoryRetriever:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compressor = MemoryCompressor()
    
    async def initialize(self):
        await self.compressor.initialize()
        self.logger.info("Memory retriever operational")
    
    async def retrieve(self, query: str, top_k: int = 5, min_similarity: float = 0.3) -> List[MemoryResult]:
        if not query: return []
        
        results = await self.compressor.recall(query, top_k, min_similarity)
        memory_results = []
        
        for i, res in enumerate(results):
            memory_results.append(MemoryResult(
                memory_dict=res["memory"],
                similarity=res["similarity"],
                rank=i + 1
            ))
        return memory_results

    async def count_memories(self) -> int:
        return len(self.compressor.memory_db)