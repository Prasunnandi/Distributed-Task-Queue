# Distributed Task Queue System



A high-performance, Redis-backed distributed task queue with Flask web interface, designed to demonstrate core SDE-1 skills in distributed systems, concurrency, and full-stack development.

## 🌟 Key Features

- **Scalable Task Processing**: Asynchronous worker pool architecture
- **Fault Tolerance**: Redis persistence ensures task durability
- **Real-time Monitoring**: Web dashboard for task submission and tracking
- **Containerized Deployment**: Ready for cloud deployment (Docker + Kubernetes)

## 🛠️ Technology Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| Backend         | Python 3.9, Flask 2.3              |
| Task Broker     | Redis 7.0                          |
| Frontend        | HTML5, CSS3, JavaScript (ES6)      |
| Infrastructure  | Docker, Docker Compose              |
| Monitoring      | Prometheus (Optional)               |

## 🚀 Getting Started

### Prerequisites
- Docker 20.10+
- Docker Compose 2.12+

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/distributed-task-queue.git
cd distributed-task-queue

# Start services
docker-compose up --build -d
