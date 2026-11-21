#!/usr/bin/env python3
"""
P2P Network Layer
P2P网络层 - 分布式算力聚合通信协议
"""

import asyncio
import json
import logging
import hashlib
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import threading


class NodeType(Enum):
    """节点类型"""
    MINER = "miner"          # 算力矿工
    WORKER = "worker"        # 工作节点
    MASTER = "master"        # 主节点
    FULL = "full"            # 全节点


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    address: str
    port: int
    node_type: NodeType
    capabilities: Dict[str, Any]
    last_heartbeat: float
    total_compute_power: float = 0.0  # 总算力 (TFLOPS)
    current_load: float = 0.0           # 当前负载 (0-1)
    
    def to_dict(self):
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "node_type": self.node_type.value,
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat,
            "total_compute_power": self.total_compute_power,
            "current_load": self.current_load
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        data["node_type"] = NodeType(data["node_type"])
        return cls(**data)


@dataclass
class Message:
    """消息包"""
    msg_id: str
    timestamp: float
    sender_id: str
    receiver_id: str
    msg_type: str
    payload: Dict[str, Any]
    signature: str = ""
    
    def to_bytes(self) -> bytes:
        """序列化"""
        data = asdict(self)
        # 移除签名
        data["signature"] = ""
        return json.dumps(data).encode()
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "Message":
        """反序列化"""
        json_data = json.loads(data.decode())
        return cls(**json_data)


class P2PNetwork:
    """P2P网络"""
    
    def __init__(self, node_id: Optional[str] = None, port: int = 8765):
        self.logger = logging.getLogger(__name__)
        self.node_id = node_id or hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        self.port = port
        self.public_key = None
        self.private_key = None
        
        # 节点信息
        self.my_node = NodeInfo(
            node_id=self.node_id,
            address="0.0.0.0",
            port=port,
            node_type=NodeType.WORKER,
            capabilities={"gpu": False, "cpu_cores": 4},
            last_heartbeat=time.time()
        )
        
        # 网络状态
        self.connected_nodes: Dict[str, NodeInfo] = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        
        # 通信套接字
        self.server_socket = None
        self.client_socket = None
        
        # 消息处理回调
        self.message_handlers: Dict[str, callable] = {}
        
        self.logger.info(f"P2P node initialized (ID: {self.node_id})")
    
    async def start(self):
        """启动P2P网络"""
        self.running = True
        
        # 启动接收线程
        receive_task = asyncio.create_task(self._receive_loop())
        
        # 启动发送线程
        send_task = asyncio.create_task(self._send_loop())
        
        # 启动心跳线程
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # 启动发现线程
        discovery_task = asyncio.create_task(self._discovery_loop())
        
        self.logger.info("P2P network started")
    
    async def stop(self):
        """停止P2P网络"""
        self.running = False
        
        # 关闭所有连接
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        
        self.logger.info("P2P network stopped")
    
    async def connect_to_peer(self, peer_address: str, peer_port: int):
        """连接到对等节点"""
        try:
            # 创建TCP连接
            reader, writer = await asyncio.open_connection(peer_address, peer_port)
            
            # 发送连接请求
            connect_msg = Message(
                msg_id=hashlib.sha256(str(time.time()).encode()).hexdigest(),
                timestamp=time.time(),
                sender_id=self.node_id,
                receiver_id="*",
                msg_type="CONNECT",
                payload={
                    "node_info": self.my_node.to_dict(),
                    "request_ack": True
                }
            )
            
            await self._send_message(writer, connect_msg)
            
            # 接收响应
            response = await self._receive_message(reader)
            if response and response.msg_type == "CONNECT_ACK":
                # 更新对等节点信息
                peer_info = NodeInfo.from_dict(response.payload["node_info"])
                self.connected_nodes[peer_info.node_id] = peer_info
                self.logger.info(f"🔗 连接到对等节点: {peer_info.node_id} @ {peer_address}:{peer_port}")
        
        except Exception as e:
            self.logger.error(f"❌ 连接对等节点失败: {e}")
    
    async def broadcast_message(self, message_type: str, payload: Dict[str, Any]):
        """广播消息"""
        message = Message(
            msg_id=hashlib.sha256(str(time.time()).encode()).hexdigest(),
            timestamp=time.time(),
            sender_id=self.node_id,
            receiver_id="*",
            msg_type=message_type,
            payload=payload
        )
        
        # 发送到所有连接的节点
        for node_id, node_info in self.connected_nodes.items():
            try:
                await self._send_to_node(node_info.address, node_info.port, message)
            except Exception as e:
                self.logger.error(f"📡 广播失败 to {node_id}: {e}")
    
    def register_message_handler(self, msg_type: str, handler: callable):
        """注册消息处理函数"""
        self.message_handlers[msg_type] = handler
    
    async def _receive_loop(self):
        """接收消息循环"""
        # 启动TCP服务器
        self.server_socket = await asyncio.start_server(
            self._handle_client_connection,
            "0.0.0.0",
            self.port
        )
        
        async with self.server_socket:
            await self.server_socket.serve_forever()
    
    async def _send_loop(self):
        """发送消息循环"""
        while self.running:
            try:
                message_data = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                # 处理队列中的消息
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"📤 发送循环错误: {e}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                # 更新自己的心跳
                self.my_node.last_heartbeat = time.time()
                
                # 广播心跳
                await self.broadcast_message("HEARTBEAT", {
                    "node_info": self.my_node.to_dict()
                })
                
                # 清理超时节点
                self._cleanup_stale_nodes()
                
                await asyncio.sleep(30)  # 30秒心跳
                
            except Exception as e:
                self.logger.error(f"💓 心跳循环错误: {e}")
    
    async def _discovery_loop(self):
        """节点发现循环"""
        while self.running:
            try:
                # 随机发现新节点（简化）
                await asyncio.sleep(60)  # 每分钟发现一次
                
            except Exception as e:
                self.logger.error(f"🔍 发现循环错误: {e}")
    
    async def _handle_client_connection(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        self.logger.info(f"🤝 新连接: {addr}")
        
        try:
            # 接收连接消息
            message = await self._receive_message(reader)
            
            if message and message.msg_type == "CONNECT":
                # 发送连接确认
                ack_msg = Message(
                    msg_id=hashlib.sha256(str(time.time()).encode()).hexdigest(),
                    timestamp=time.time(),
                    sender_id=self.node_id,
                    receiver_id=message.sender_id,
                    msg_type="CONNECT_ACK",
                    payload={
                        "node_info": self.my_node.to_dict(),
                        "accepted": True
                    }
                )
                await self._send_message(writer, ack_msg)
                
                # 存储节点信息
                if "node_info" in message.payload:
                    node_info = NodeInfo.from_dict(message.payload["node_info"])
                    self.connected_nodes[node_info.node_id] = node_info
                
                # 处理消息
                async for msg in self._stream_messages(reader):
                    await self._process_message(msg)
                    
        except Exception as e:
            self.logger.error(f"❌ 处理客户端连接错误: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            if message and message.sender_id in self.connected_nodes:
                del self.connected_nodes[message.sender_id]
    
    async def _receive_message(self, reader) -> Optional[Message]:
        """接收单个消息"""
        # 读取消息长度
        try:
            length_data = await asyncio.wait_for(reader.readexactly(4), timeout=30)
        except asyncio.exceptions.IncompleteReadError:
            return None
        
        length = int.from_bytes(length_data, 'big')
        
        # 读取消息内容
        data = await asyncio.wait_for(reader.readexactly(length), timeout=30)
        
        return Message.from_bytes(data)
    
    async def _stream_messages(self, reader) -> Message:
        """流式读取消息"""
        while True:
            msg = await self._receive_message(reader)
            if msg is None:
                break
            yield msg
    
    async def _send_message(self, writer, message: Message):
        """发送消息"""
        data = message.to_bytes()
        length = len(data).to_bytes(4, 'big')
        writer.write(length + data)
        await writer.drain()
    
    async def _send_to_node(self, address: str, port: int, message: Message):
        """发送到指定节点"""
        try:
            reader, writer = await asyncio.open_connection(address, port)
            await self._send_message(writer, message)
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            self.logger.error(f"📤 发送消息到 {address}:{port} 失败: {e}")
            
            # 从连接列表中移除
            for node_id, node_info in list(self.connected_nodes.items()):
                if node_info.address == address and node_info.port == port:
                    del self.connected_nodes[node_id]
                    break
    
    async def _process_message(self, message: Message):
        """处理消息"""
        self.logger.debug(f"📨 接收到消息: {message.msg_type} from {message.sender_id}")
        
        # 调用对应的处理函数
        if message.msg_type in self.message_handlers:
            try:
                await self.message_handlers[message.msg_type](message)
            except Exception as e:
                self.logger.error(f"🔄 消息处理错误: {e}")
    
    def _cleanup_stale_nodes(self):
        """清理超时节点"""
        current_time = time.time()
        stale_nodes = [
            node_id for node_id, node_info in self.connected_nodes.items()
            if current_time - node_info.last_heartbeat > 90
        ]
        
        for node_id in stale_nodes:
            del self.connected_nodes[node_id]
            self.logger.info(f"🗑️ 移除超时节点: {node_id}")
    
    def get_connected_nodes(self) -> Dict[str, NodeInfo]:
        """获取已连接的节点"""
        return self.connected_nodes.copy()
    
    def get_my_node_info(self) -> NodeInfo:
        """获取自己的节点信息"""
        return self.my_node


# 需要导入
import time
