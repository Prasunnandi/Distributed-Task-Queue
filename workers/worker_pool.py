import time
import threading
from typing import Callable, Dict, Any
from engine.task import TaskQueueBroker, TaskState

class WorkerPool:
    """
    Concurrent worker threads consuming tasks from the message broker.
    """
    def __init__(self, broker: TaskQueueBroker, concurrency: int = 4):
        self.broker = broker
        self.concurrency = concurrency
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self.workers = []
        self.running = False
        self.processed_count = 0
        self._lock = threading.Lock()

    def register_handler(self, task_name: str, handler: Callable[[Dict[str, Any]], Any]):
        self.handlers[task_name] = handler

    def start(self):
        self.running = True
        for i in range(self.concurrency):
            t = threading.Thread(target=self._worker_loop, args=(f"worker-{i+1}",), daemon=True)
            self.workers.append(t)
            t.start()

    def stop(self):
        self.running = False

    def _worker_loop(self, worker_id: str):
        while self.running:
            task = self.broker.dequeue()
            if not task:
                time.sleep(0.05)
                continue

            handler = self.handlers.get(task.name)
            if not handler:
                self.broker.fail(task.task_id, f"No handler registered for '{task.name}'")
                continue

            try:
                result = handler(task.payload)
                self.broker.complete(task.task_id, result)
                with self._lock:
                    self.processed_count += 1
            except Exception as e:
                self.broker.fail(task.task_id, str(e))
