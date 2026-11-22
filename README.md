# Distributed Asynchronous Task Queue & Message Broker

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Priority Queue](https://img.shields.io/badge/Queue-Priority%20Min--Heap-purple.svg)]()
[![Reliability](https://img.shields.io/badge/Fault%20Tolerance-Exponential%20Backoff%20%7C%20DLQ-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Unit%20Tests-100%25%20Passed-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

A high-performance distributed task queue and worker coordination engine inspired by Celery and BullMQ. Features a min-heap priority scheduler, thread-pool worker concurrency, automatic exponential backoff retry policies, and an isolated Dead-Letter Queue (DLQ) for permanently failed tasks.

---

## 🏛️ Architecture Overview

```
                          CLIENT APPLICATION
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │        Task Producer          │
                   │ (Priority, Max Retries, UUID) │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    Priority Queue Broker      │
                   │   (Min-Heap Priority Order)   │
                   └───────────────┬───────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
       ┌─────────────────┐┌─────────────────┐┌─────────────────┐
       │ Worker Thread 1 ││ Worker Thread 2 ││ Worker Thread N │
       └────────┬────────┘└────────┬────────┘└────────┬────────┘
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                        Task Execution Outcome
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌─────────────────────┐       ┌─────────────────────┐
         │     SUCCESS (200)   │       │   TRANSIENT ERROR   │
         │ (Result Store Cache)│       │ (Exponential Retry) │
         └─────────────────────┘       └──────────┬──────────┘
                                                  │ Exceeded Max Retries
                                                  ▼
                                       ┌─────────────────────┐
                                       │  Dead-Letter Queue  │
                                       │ (DLQ for Inspection)│
                                       └─────────────────────┘
```

---

## ⚡ Core Reliability Features

1. **Priority Min-Heap Scheduling:**
   - Urgent tasks ($P_1$) leapfrog batch background jobs ($P_{10}$) with $O(\log N)$ enqueue/dequeue complexity.
2. **Exponential Backoff Retries:**
   - Failed tasks retry at increasing intervals: $t_{\text{delay}} = t_{\text{base}} \times 2^{(\text{retry} - 1)}$ to protect downstream databases from cascading thundering herds.
3. **Dead-Letter Queue (DLQ):**
   - Poison pills and fatal exceptions are moved to an isolated DLQ preserving error stack traces for engineer inspection without blocking valid tasks.
4. **Interactive Real-Time Dashboard:**
   - Live queue depth, throughput, active worker status, and task injection interface.

---

## 🚀 Quickstart

### 1. Run Unit Tests
```bash
python -m unittest tests/test_queue.py
```

Output:
```
Ran 3 tests in 0.603s
OK
```

### 2. Open Live Task Queue Monitor
Open `web/index.html` in your web browser to test real-time task enqueueing, priority dispatching, and DLQ tracking.

---

## 📁 Repository Directory Structure

```
├── engine/
│   └── task.py                  # Priority min-heap, TaskState, and DLQ broker
├── workers/
│   └── worker_pool.py           # Multi-threaded worker daemon
├── tests/
│   └── test_queue.py            # Unit test suite
├── web/
│   └── index.html               # Live visual queue dashboard
└── README.md                    # Technical documentation
```

---

## 📜 License
MIT License. Created by [Prasun Nandi](https://github.com/Prasunnandi).
