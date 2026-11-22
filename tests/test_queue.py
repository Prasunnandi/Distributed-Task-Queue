import unittest
import time
from engine.task import TaskQueueBroker, TaskState
from workers.worker_pool import WorkerPool

class TestTaskQueue(unittest.TestCase):
    def test_priority_scheduling(self):
        broker = TaskQueueBroker()
        # Enqueue low priority task first, then high priority
        t_low = broker.enqueue("email.send", {"to": "user1@example.com"}, priority=10)
        t_high = broker.enqueue("payment.process", {"amount": 500}, priority=1)

        # Dequeue must return high priority task first
        d1 = broker.dequeue()
        d2 = broker.dequeue()

        self.assertEqual(d1.task_id, t_high.task_id)
        self.assertEqual(d2.task_id, t_low.task_id)

    def test_worker_processing_success(self):
        broker = TaskQueueBroker()
        pool = WorkerPool(broker, concurrency=2)

        def resize_img(payload):
            return f"resized_{payload['width']}x{payload['height']}"

        pool.register_handler("image.resize", resize_img)
        pool.start()

        task = broker.enqueue("image.resize", {"width": 800, "height": 600})
        time.sleep(0.2)
        pool.stop()

        completed = broker.get_task(task.task_id)
        self.assertEqual(completed.status, TaskState.SUCCESS)
        self.assertEqual(completed.result, "resized_800x600")

    def test_retry_and_dead_letter_queue(self):
        broker = TaskQueueBroker()
        pool = WorkerPool(broker, concurrency=1)

        attempts = 0
        def flaky_task(payload):
            nonlocal attempts
            attempts += 1
            raise ValueError("Upstream DB timeout")

        pool.register_handler("db.sync", flaky_task)
        pool.start()

        task = broker.enqueue("db.sync", {"data": "test"}, max_retries=2)
        time.sleep(0.4)
        pool.stop()

        dlq_task = broker.get_task(task.task_id)
        self.assertEqual(dlq_task.status, TaskState.DEAD_LETTER)
        self.assertEqual(dlq_task.retry_count, 2)
        self.assertIn("Upstream DB timeout", dlq_task.error)

if __name__ == "__main__":
    unittest.main()
