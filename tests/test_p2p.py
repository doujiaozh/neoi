#!/usr/bin/env python3
"""
P2P网络测试
"""

import asyncio
import pytest
from distributed.p2p_network import P2PNetwork, NodeType


@pytest.mark.asyncio
async def test_p2p_network_init():
    """测试P2P网络初始化"""
    network = P2PNetwork()
    
    print(f"✅ P2P网络初始化完成 (ID: {network.node_id})")


@pytest.mark.asyncio
async def test_node_info():
    """测试节点信息"""
    network = P2PNetwork()
    node_info = network.get_my_node_info()
    
    assert node_info.node_id is not None
    assert node_info.node_type == NodeType.WORKER
    assert node_info.port == 8765
    
    print(f"✅ 节点信息验证完成")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
