# Task 1: ZeroMQ Distributed Trading System

This directory contains a mock distributed trading system built using ZeroMQ, simulating the communication flow between a Trading Strategy, a Broker Adapter, and an Exchange Broker.

## 🏗️ Architecture

The system is decoupled into three independent processes communicating over two distinct ZMQ network topologies:

1. **Order Routing (Synchronous `REQ/REP`)**
   - **Flow:** Strategy (A) ➡️ Adapter (B) ➡️ Broker (C)
   - Used for guaranteed, point-to-point order placement and acknowledgment.
2. **Market Data & Executions (Asynchronous `PUB/SUB`)**
   - **Flow:** Broker (C) ➡️ Adapter (B) ➡️ Strategy (A)
   - Used for high-throughput, non-blocking broadcasting of execution fills and order book updates.

```text
+----------------+          REQ/REP (5557)         +---------------+          REQ/REP (5555)         +---------------+
|                |  ---------------------------->  |               |  ---------------------------->  |               |
|  Script A      |                                 |  Script B     |                                 |  Script C     |
|  (Strategy)    |                                 |  (Adapter)    |                                 |  (Broker)     |
|                |  <----------------------------  |               |  <----------------------------  |               |
+----------------+          PUB/SUB (5558)         +---------------+          PUB/SUB (5556)         +---------------+
```

## 🛠️ Key Design Decisions

1. **Strict Data Validation (`Pydantic`)**
   - All network payloads are serialized/deserialized using Pydantic models (`schemas.py`). This guarantees type safety across the network boundary, ensuring that malformed JSON or missing fields (e.g., missing price) are caught immediately, preventing catastrophic downstream crashes.
2. **ZMQ Poller (`Script B`)**
   - The Adapter must simultaneously listen for incoming orders from the Strategy and incoming market data from the Broker. Instead of busy-waiting with a CPU-intensive non-blocking loop, it uses a C-level `zmq.Poller` to multiplex the sockets, achieving near-zero CPU usage while idle.
3. **Rigorous PnL Accounting (`Script A`)**
   - The Strategy features a robust `Portfolio` class that accurately calculates **Realised PnL** using Volume Weighted Average Price (VWAP). It correctly handles complex state transitions, such as flipping from a net-long position directly into a net-short position on a single fill, ensuring accounting is accurate down to the penny.
4. **PUB/SUB Topic Filtering**
   - Market data is blasted using specific topics (`EXEC` and `OB`). This allows downstream subscribers to filter out high-frequency order book noise at the network layer if they only care about execution reports.

## 🚀 How to Run

To run the full demonstration, you will need 3 terminal windows. Start the services in reverse order (Broker first) to establish the network binds cleanly.

1. **Terminal 1 (Start Broker):**
   ```bash
   python script_c_broker.py
   ```
2. **Terminal 2 (Start Adapter):**
   ```bash
   python script_b_adapter.py
   ```
3. **Terminal 3 (Start Strategy):**
   ```bash
   python script_a_strategy.py
   ```

*Watch Terminal 3 to see the Strategy execute 5 automated orders (both Buy and Sell) while maintaining a live dashboard of Open Positions, Realised PnL, and a dynamic Order Book.*
