#!/usr/bin/env python3
"""
分布式计算测试
"""

import asyncio
import pytest
from distributed.compute_cluster import ComputeCluster, TaskPriority


@pytest.mark.asyncio
async def test_cluster_creation():
    """测试集群初始化"""
    cluster = ComputeCluster()
    
    print(f"✅ 计算集群创建完成")


@pytest.mark.asyncio
async def test_task_submission():
    """测试任务提交"""
    cluster = ComputeCluster()
    
    task_id = await cluster.submit_task(
        "test_task",
        {"test_data": "sample"},
        TaskPriority.NORMAL
    )
    
    assert task_id is not None
    assert len(task_id) == 16
    
    print(f"✅ 任务提交完成: {task_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
