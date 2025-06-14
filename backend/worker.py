import redis
import pickle
import time
import signal
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GracefulExiter:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info("Shutting down gracefully...")
        self.shutdown = True

def get_redis():
    """Create Redis connection with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host='localhost',
                port=6379,
                socket_timeout=10,
                socket_connect_timeout=5
            )
            if r.ping():
                logger.info("Connected to Redis")
                return r
        except redis.RedisError as e:
            logger.warning(f"Redis connection attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    raise redis.ConnectionError("Could not connect to Redis")

def process_task(task):
    """Process a single task"""
    logger.info(f"Processing task {task['id']}")
    time.sleep(1)  # Simulate work
    return {
        'original_data': task['data'],
        'processed_at': time.time(),
        'status': 'completed'
    }

def main():
    exiter = GracefulExiter()
    r = get_redis()
    logger.info("Worker started. Waiting for tasks...")

    while not exiter.shutdown:
        try:
            # Get task with 5 second timeout
            task_data = r.brpop('task_queue', timeout=5)
            
            if task_data is None:
                continue  # Normal timeout, no tasks
                
            # Unpack task (key, value)
            _, task_bytes = task_data
            task = pickle.loads(task_bytes)
            
            # Process and store result
            result = process_task(task)
            r.setex(
                f"result:{task['id']}",
                3600,  # 1 hour TTL
                pickle.dumps(result)
            )
            logger.info(f"Completed task {task['id']}")
            
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Processing error: {e}")
            time.sleep(1)

    logger.info("Worker shutdown complete")

if __name__ == '__main__':
    main()