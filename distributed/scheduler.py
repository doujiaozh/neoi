#!/usr/bin/env python3
"""
任务调度器
分布式任务调度与优先级管理
"""

import asyncio
import logging
import time
import heapq
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field


@dataclass(order=True)
class PriorityTask:
    """优先级任务"""
    priority: int
    created_at: float
    task_id: str
    task_data: Any = field(compare=False)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 任务队列 (最小堆)
        self.task_queue: List[PriorityTask] = []
        
        # 任务状态
        self.tasks: Dict[str, Any] = {}
        
        # 调度状态
        self.running = False
        self.worker_count = 4
        
        # 回调
        self.on_task_started: Optional[Callable] = None
        self.on_task_completed: Optional[Callable] = None
        
        self.logger.info("Task scheduler initialized")
    
    async def initialize(self):
        """初始化调度器"""
        self.running = True
        
        # 启动工作线程
        for i in range(self.worker_count):
            task = asyncio.create_task(self._task_worker(f"worker-{i}"))
            setattr(self, f"worker_{i}", task)
        
        self.logger.info(f"✅ 任务调度器运行中 (工作线程: {self.worker_count})")
    
    async def shutdown(self):
        """关闭调度器"""
        self.running = False
        
        # 等待所有工作线程完成
        await asyncio.gather(*[getattr(self, f"worker_{i}") for i in range(self.worker_count)], return_exceptions=True)
        
        self.logger.info("🔴 任务调度器已关闭")
    
    async def submit_task(self, task_id: str, task_data: Any, priority: int = 2):
        """提交任务"""
        task = PriorityTask(
            priority=priority,
            created_at=time.time(),
            task_id=task_id,
            task_data=task_data
        )
        
        # 添加到优先级队列
        heapq.heappush(self.task_queue, task)
        self.tasks[task_id] = task_data
        
        self.logger.debug(f"📝 任务 {task_id} 已提交 (优先级: {priority})")
    
    async def _task_worker(self, worker_name: str):
        """任务工作线程"""
        self.logger.info(f"👷 {worker_name} 启动")
        
        while self.running:
            try:
                # 从队列获取任务
                if self.task_queue:
                    task = heapq.heappop(self.task_queue)
                    
                    self.logger.info(f"🚀 {worker_name} 处理任务: {task.task_id}")
                    
                    # 执行任务
                    result = await self._execute_task(task.task_id, task.task_data)
                    
                    # 任务完成处理
                    await self.on_task_completed(task) if self.on_task_completed else None
                    
                else:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"❌ {worker_name} 任务执行错误: {e}")
    
    async def _execute_task(self, task_id: str, task_data: Any) -> Any:
        """执行单个任务"""
        try:
            # 模拟任务执行
            await asyncio.sleep(0.5)
            
            # 返回结果
            return {
                "task_id": task_id,
                "status": "completed",
                "result": f"Task {task_id} executed successfully"
            }
            
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "queue_size": len(self.task_queue),
            "total_tasks": len(self.tasks),
            "running": self.running,
            "workers": self.worker_count
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.logger.info(f"🗑️ 任务 {task_id} 已取消")
            return True
        return False


# 需要导入
import time
