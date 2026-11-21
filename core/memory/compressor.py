#!/usr/bin/env python3
"""
Memory Compression System (Lightweight Version)
"""
import hashlib
import logging
import re
import time
from typing import Dict, List, Any
from dataclasses import dataclass

class SimHash:
    def __init__(self, text, hash_bits=64):
        self.hash_bits = hash_bits
        self._hash = self._compute_simhash(text)
    
    def _compute_simhash(self, text):
        if not text: return 0
        words = self._tokenize(text)
        bit_counts = [0] * self.hash_bits
        for word in words:
            word_hash = int(hashlib.sha1(word.encode()).hexdigest(), 16)
            for i in range(self.hash_bits):
                bit_counts[i] += 1 if (word_hash >> i) & 1 else -1
        
        hash_value = 0
        for i, count in enumerate(bit_counts):
            if count > 0: hash_value |= (1 << i)
        return hash_value
    
    def _tokenize(self, text):
        text = text.strip()
        # 兼容中英文分词（英文按单词，中文按单字）
        words = re.findall(r'[\w]+|[^\w\s]', text, re.UNICODE)
        return [w.lower() for w in words if w.strip()]

    def similarity(self, other_hash):
        if self._hash == other_hash: return 1.0
        distance = bin(self._hash ^ other_hash).count('1')
        return 1.0 - (distance / self.hash_bits)

@dataclass
class MemoryChunk:
    id: str
    content: str
    level: int
    timestamp: float
    keywords: List[str]
    simhash: int
    
    def to_dict(self):
        return {
            "id": self.id, "content": self.content, "level": self.level,
            "timestamp": self.timestamp, "keywords": self.keywords, "simhash": self.simhash
        }

class MemoryCompressor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_db: List[MemoryChunk] = []
        self.index: Dict[str, MemoryChunk] = {}
        self.max_memory_size = 1000
    
    async def initialize(self):
        self.logger.info("Memory compressor initialized")
    
    def generate_id(self, content: str) -> str:
        return hashlib.sha256(f"{content}{time.time()}".encode()).hexdigest()[:16]
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        if not text: return []
        word_freq = {}
        words = re.findall(r'[\w]+|[a-zA-Z]+', text, re.UNICODE)
        for word in words:
            word = word.lower()
            if len(word) > 2 and word not in ['the', 'is', 'at', 'on', 'in']:
                word_freq[word] = word_freq.get(word, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    def compress(self, text: str, level: int = 0) -> Dict[str, Any]:
        if not text.strip(): return {"success": False, "error": "Empty text"}
        
        keywords = self.extract_keywords(text)
        simhash = SimHash(text)
        memory_id = self.generate_id(text)
        
        chunk = MemoryChunk(memory_id, text, level, time.time(), keywords, simhash._hash)
        self.memory_db.append(chunk)
        self.index[memory_id] = chunk
        
        if len(self.memory_db) > self.max_memory_size:
            oldest = self.memory_db.pop(0)
            del self.index[oldest.id]
            
        return {
            "success": True, "id": memory_id,
            "content": text[:50] + "..." if len(text) > 50 else text,
            "keywords": keywords, "simhash": simhash._hash
        }
    
    async def recall(self, query: str, top_k: int = 5, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        if not query: return []
        query_simhash = SimHash(query)
        query_keywords = self.extract_keywords(query)
        results = []
        
        for chunk in self.memory_db:
            # 性能优化：直接用存好的 hash 算，不要再重新计算
            similarity = query_simhash.similarity(chunk.simhash)
            set1, set2 = set(chunk.keywords), set(query_keywords)
            keyword_match = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0.0
            
            score = (similarity + keyword_match) / 2
            if score >= min_similarity:
                results.append({"memory": chunk.to_dict(), "similarity": score})
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    async def get_all_memory(self): return [c.to_dict() for c in self.memory_db]
    async def clear_memory(self):
        self.memory_db.clear(); self.index.clear()