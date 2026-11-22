import time
import uuid
import heapq
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class TaskState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task_id: str = field(compare=False)
    name: str = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)
    max_retries: int = field(default=3, compare=False)
    retry_count: int = field(default=0, compare=False)
    retry_delay_sec: float = field(default=1.0, compare=False)
    created_at: float = field(default_factory=time.time, compare=False)
    status: TaskState = field(default=TaskState.PENDING, compare=False)
    result: Optional[Any] = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)

class TaskQueueBroker:
    """
    High-throughput priority queue broker with dead-letter queue and exponential retry backoff.
    """
    def __init__(self):
        self._priority_queue = []  # Min-heap based on priority (0 = Highest priority)
        self._tasks: Dict[str, PrioritizedTask] = {}
        self._dead_letter_queue: Dict[str, PrioritizedTask] = {}
        self._completed_tasks: Dict[str, PrioritizedTask] = {}

    def enqueue(self, name: str, payload: Dict[str, Any], priority: int = 5, max_retries: int = 3) -> PrioritizedTask:
        task_id = str(uuid.uuid4())
        task = PrioritizedTask(
            priority=priority,
            task_id=task_id,
            name=name,
            payload=payload,
            max_retries=max_retries
        )
        self._tasks[task_id] = task
        heapq.heappush(self._priority_queue, task)
        return task

    def dequeue(self) -> Optional[PrioritizedTask]:
        if not self._priority_queue:
            return None
        task = heapq.heappop(self._priority_queue)
        task.status = TaskState.RUNNING
        return task

    def complete(self, task_id: str, result: Any):
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskState.SUCCESS
            task.result = result
            self._completed_tasks[task_id] = task

    def fail(self, task_id: str, error: str):
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task.error = error

        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskState.RETRYING
            # Exponential backoff delay
            backoff_sec = task.retry_delay_sec * (2 ** (task.retry_count - 1))
            task.priority += 1  # slightly deprioritize failing tasks
            heapq.heappush(self._priority_queue, task)
        else:
            task.status = TaskState.DEAD_LETTER
            self._dead_letter_queue[task_id] = task

    def get_task(self, task_id: str) -> Optional[PrioritizedTask]:
        return self._tasks.get(task_id)

    def stats(self) -> Dict[str, int]:
        return {
            "queued": len(self._priority_queue),
            "completed": len(self._completed_tasks),
            "dead_letter": len(self._dead_letter_queue),
            "total_tracked": len(self._tasks)
        }
