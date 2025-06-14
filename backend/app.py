from flask import Flask, request, jsonify, send_from_directory
import redis
import pickle
import time
import logging
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Redis configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'socket_timeout': 10,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}

def get_redis():
    """Create Redis connection with error handling"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        if not r.ping():
            raise redis.ConnectionError("Redis ping failed")
        logger.info("Connected to Redis")
        return r
    except redis.RedisError as e:
        logger.error(f"Redis connection failed: {e}")
        raise

r = get_redis()

@app.route('/')
def serve_index():
    return send_from_directory('../frontend/templates', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend/static', filename)

@app.route('/add_task', methods=['POST'])
def add_task():
    """Add task to queue"""
    try:
        task = {
            'id': str(time.time_ns()),
            'data': request.json.get('data'),
            'timestamp': time.time()
        }
        r.lpush('task_queue', pickle.dumps(task))
        logger.info(f"Added task {task['id']}")
        return jsonify({
            "status": "success",
            "task_id": task['id'],
            "queue_length": r.llen('task_queue')
        })
    except Exception as e:
        logger.error(f"Error in add_task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """Check task status"""
    try:
        result = r.get(f"result:{task_id}")
        return jsonify({
            "status": "completed" if result else "processing",
            "result": pickle.loads(result) if result else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "redis_connected": r.ping(),
            "pending_tasks": r.llen('task_queue')
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)