#!/usr/bin/env python3
"""
Compute Cluster Manager
计算集群管理器 - 分布式算力调度与分配
"""

import asyncio
import logging
import hashlib
import time
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .scheduler import TaskScheduler


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ComputeTask:
    """计算任务"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_nodes: List[str] = None
    result: Any = None
    error: str = None
    created_at: float = None
    started_at: float = None
    completed_at: float = None
    timeout: int = 300  # 默认超时5分钟
    
    def __post_init__(self):
        if self.assigned_nodes is None:
            self.assigned_nodes = []
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_nodes": self.assigned_nodes,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "timeout": self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        data["priority"] = TaskPriority(data["priority"])
        data["status"] = TaskStatus(data["status"])
        return cls(**data)


@dataclass
class NodeCapacity:
    """节点容量"""
    node_id: str
    cpu_cores: int
    memory_gb: float
    gpu_count: int = 0
    gpu_memory_gb: float = 0.0
    max_concurrent_tasks: int = 10
    current_tasks: int = 0
    
    def available_capacity(self) -> float:
        """可用容量"""
        return 1.0 - (self.current_tasks / self.max_concurrent_tasks)
    
    def to_dict(self):
        return asdict(self)


class ComputeCluster:
    """计算集群"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 集群状态
        self.nodes: Dict[str, NodeCapacity] = {}
        self.tasks: Dict[str, ComputeTask] = {}
        self.task_queue: asyncio.PriorityQueue = None
        
        # 任务调度
        self.scheduler = TaskScheduler()
        self._node_manager = NodeManager()
        
        # 回调函数
        self.on_task_complete: Optional[Callable] = None
        self.on_task_fail: Optional[Callable] = None
        
        self.running = False
        
        self.logger.info("Compute cluster initialized")
    
    async def initialize(self):
        """初始化集群"""
        self.task_queue = asyncio.PriorityQueue()
        self.running = True
        
        # 启动调度循环
        scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        self.logger.info("Compute cluster running")
    
    async def shutdown(self):
        """关闭集群"""
        self.running = False
        
        # 取消所有任务
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING or task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.CANCELLED
                task.error = "Cluster shutting down"
        
        self.logger.info("Compute cluster stopped")
    
    async def add_node(self, node_id: str, capacity: NodeCapacity):
        """添加计算节点"""
        self.nodes[node_id] = capacity
        self.logger.info(f"Added compute node: {node_id} (CPU: {capacity.cpu_cores}, GPU: {capacity.gpu_count})")
        
        # 广播节点加入
        await self._broadcast_node_event("NODE_JOINED", capacity.to_dict())
    
    async def remove_node(self, node_id: str):
        """移除计算节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.logger.info(f"🗑️ 移除计算节点: {node_id}")
            
            # 重新分配该节点上的任务
            await self._reassign_node_tasks(node_id)
            
            # 广播节点退出
            await self._broadcast_node_event("NODE_LEFT", {"node_id": node_id})
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """提交任务"""
        task_id = hashlib.sha256(f"{time.time()}_{task_type}_{id(payload)}".encode()).hexdigest()[:16]
        
        task = ComputeTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority
        )
        
        self.tasks[task_id] = task
        
        # 添加到任务队列
        await self.task_queue.put((priority.value, task.created_at, task_id))
        
        self.logger.info(f"Submitted task: {task_id} (Type: {task_type}, Priority: {priority.value})")
        
        return task_id
    
    async def get_task_result(self, task_id: str, timeout: Optional[int] = None) -> Optional[Any]:
        """获取任务结果"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        if task.status == TaskStatus.COMPLETED:
            return task.result
        
        if task.status == TaskStatus.FAILED:
            return None
        
        # 等待任务完成
        start_time = time.time()
        while task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            await asyncio.sleep(0.1)
            
            if timeout and (time.time() - start_time) > timeout:
                task.status = TaskStatus.FAILED
                task.error = "超时"
                return None
        
        if task.status == TaskStatus.COMPLETED:
            return task.result
        else:
            return None
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": len([n for n in self.nodes.values() if n.current_tasks > 0]),
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "nodes": {node_id: capacity.to_dict() for node_id, capacity in self.nodes.items()}
        }
    
    async def _scheduler_loop(self):
        """调度循环"""
        while self.running:
            try:
                # 从队列获取任务
                _, _, task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    if task.status == TaskStatus.PENDING:
                        # 任务分配
                        await self._schedule_task(task)
                        
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"🔄 调度循环错误: {e}")
    
    async def _schedule_task(self, task: ComputeTask):
        """调度任务到节点"""
        # 查找合适的节点
        suitable_nodes = await self._find_suitable_nodes(task)
        
        if not suitable_nodes:
            task.status = TaskStatus.FAILED
            task.error = "无可用计算节点"
            self.logger.error(f"❌ 任务 {task_id} 无法调度：无可用节点")
            if self.on_task_fail:
                await self.on_task_fail(task)
            return
        
        # 分配任务到节点
        self.logger.info(f"🎯 任务 {task_id} 分配给节点: {suitable_nodes}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        task.assigned_nodes = suitable_nodes
        
        # 更新节点负载
        for node_id in suitable_nodes:
            if node_id in self.nodes:
                self.nodes[node_id].current_tasks += 1
        
        # 执行任务
        await self._execute_task(task)
    
    async def _find_suitable_nodes(self, task: ComputeTask) -> List[str]:
        """查找合适的计算节点"""
        suitable_nodes = []
        
        for node_id, capacity in self.nodes.items():
            # 检查节点容量
            if capacity.available_capacity() > 0:
                # 检查GPU需求
                if task.payload.get("requires_gpu", False) and capacity.gpu_count > 0:
                    suitable_nodes.append(node_id)
                elif task.payload.get("requires_gpu", False) == False:
                    suitable_nodes.append(node_id)
        
        # 按负载排序，选择负载最低的
        suitable_nodes.sort(key=lambda n: self.nodes[n].current_tasks)
        
        return suitable_nodes[:2]  # 选择2个节点
    
    async def _execute_task(self, task: ComputeTask):
        """执行任务"""
        try:
            # 模拟任务执行
            await asyncio.sleep(2)  # 模拟计算
            
            # 生成结果
            task.result = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": "completed",
                "execution_time": 2.0,
                "output": f"任务 {task.task_id} 执行完成"
            }
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # 更新节点负载
            for node_id in task.assigned_nodes:
                if node_id in self.nodes:
                    self.nodes[node_id].current_tasks -= 1
            
            self.logger.info(f"✅ 任务 {task.task_id} 执行完成")
            
            if self.on_task_complete:
                await self.on_task_complete(task)
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            # 更新节点负载
            for node_id in task.assigned_nodes:
                if node_id in self.nodes:
                    self.nodes[node_id].current_tasks -= 1
            
            self.logger.error(f"❌ 任务 {task.task_id} 执行失败: {e}")
            
            if self.on_task_fail:
                await self.on_task_fail(task)
    
    async def _reassign_node_tasks(self, node_id: str):
        """重新分配节点的任务"""
        # 找到该节点上的所有任务
        tasks_to_reassign = [
            task for task in self.tasks.values()
            if node_id in task.assigned_nodes and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
        ]
        
        for task in tasks_to_reassign:
            # 重新调度
            task.status = TaskStatus.PENDING
            task.assigned_nodes = []
            await self._schedule_task(task)
    
    async def _broadcast_node_event(self, event_type: str, data: Dict):
        """广播节点事件"""
        # 这里的实现应该发送事件到所有连接节点
        self.logger.debug(f"Broadcast node event: {event_type}")
    
class NodeManager:
    """节点管理器"""
    
    def __init__(self):
        self.nodes = {}
    
    def register_node(self, node_id: str, info: Dict):
        """注册节点"""
        self.nodes[node_id] = info
    
    def unregister_node(self, node_id: str):
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """获取节点信息"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> Dict[str, Dict]:
        """获取所有节点"""
        return self.nodes.copy()


# 需要导入
import time
