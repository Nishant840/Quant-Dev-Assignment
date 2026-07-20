
# Quant Developer Assignment

This repository contains my submission for the Quant Developer assignment.

The assignment consists of two independent tasks focused on distributed systems, inter-process communication, REST APIs, and concurrent programming in Python. Each task is implemented in its own directory with separate dependencies and detailed documentation.

---

## Project Structure

### Task 1 – ZeroMQ Distributed Trading System

Location: [`task1_zmq/`](./task1_zmq)

A distributed trading system consisting of a Strategy, Broker Adapter, and Mock Broker communicating over ZeroMQ.

**Technologies**

- Python
- ZeroMQ (pyzmq)
- Pydantic

**Highlights**

- REQ/REP based order routing
- PUB/SUB based market data distribution
- Broker Adapter architecture
- ZeroMQ Poller for concurrent message handling
- Portfolio tracking with realised PnL

**Documentation:** [`task1_zmq/README.md`](./task1_zmq/README.md)

---

### Task 2 – FastAPI Concurrency Demo

Location: [`task2_rest/`](./task2_rest)

A FastAPI application demonstrating two different concurrency models for handling multiple requests.

**Technologies**

- Python
- FastAPI
- Uvicorn
- Requests

**Highlights**

- Asyncio implementation using `async def`
- Threading implementation using synchronous endpoints
- Concurrent request load testing
- Portfolio state management through REST APIs

**Documentation:** [`task2_rest/README.md`](./task2_rest/README.md)

---

## Key Design Decisions

- **Task 1:** Utilizes ZMQ `REQ/REP` for synchronous, guaranteed order flow, and `PUB/SUB` for asynchronous market data updates. This topology keeps the strategy completely decoupled from broker-specific networking.
- **Task 2:** Built two distinct concurrency models side-by-side to directly compare threadpool offloading vs single-thread asyncio under FastAPI, complete with a concurrent load-testing client to prove the architecture.

---

## Repository Structure

```text
Quant-Dev-Assignment/
├── task1_zmq/
│   ├── README.md
│   └── ...
├── task2_rest/
│   ├── README.md
│   └── ...
└── README.md
```

---

## Getting Started

Each task is self-contained and includes its own `requirements.txt` and detailed setup instructions.

Install the dependencies for the task you want to run:

### Task 1

```bash
cd task1_zmq
pip install -r requirements.txt
```

Refer to the Task 1 README for execution instructions.

### Task 2

```bash
cd task2_rest
pip install -r requirements.txt
```

Refer to the Task 2 README for execution instructions.

---

## Notes

- Each task is independent and can be run separately.
- Detailed design decisions and architecture diagrams are included in the respective task documentation.