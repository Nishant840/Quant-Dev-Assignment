import zmq
import json
import time
import random
from pydantic import ValidationError
from schemas import Order, Execution, OrderBook

def main():
    context = zmq.Context()

    # rep socket to recieve orders
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5555")

    # PUB socket to broadcast updates to Adapter
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5556")

    print("[Broker] Started. Recieving orders on 5555, publishing updates on 5556...")

    while True:
        try:
            # check for incoming order (non-blocking so we can still push OB updates while idle)
            message = rep_socket.recv_string(flags=zmq.NOBLOCK)
            print(f"[Broker] Recieved order payload: {message}")

            try:
                # validating
                order_data = json.loads(message)
                order = Order(**order_data)

                # send immediate synchronous ACK
                rep_socket.send_string(json.dumps({
                    "status": "ACK",
                    "message": "Order accepted"
                }))

                time.sleep(0.5)

                # Generating Execution (Mocking a 100% full fill)
                execution = Execution(
                    order_id        = order.order_id,
                    symbol          = order.symbol,
                    side            = order.side,
                    price           = order.price,
                    filled_quantity = order.quantity,
                    status          = "FILLED"
                )

                # publish execution asynchronously
                topic = "EXEC"
                pub_message = f"{topic} {execution.model_dump_json()}"
                pub_socket.send_string(pub_message)
                print(f"[Broker] Published Execution: {pub_message}")

            except (json.JSONDecodeError, ValidationError) as e:
                # If validation fails, Reply with ERROR and keep broker alive
                error_msg = f"Invalid payload: {str(e)}"
                print(f"[Broker] {error_msg}")
                rep_socket.send_string(json.dumps({"status": "ERROR", "message": "Bad order format"}))

        except zmq.Again:
            pass

        time.sleep(0.5)
        if random.random() > 0.6:
            # Mock some random top-of-book prices around a base price of 150
            ob = OrderBook(
                symbol="AAPL",
                bids={150.0 - random.randint(1,2): random.randint(10,100)},
                asks={150.0 + random.randint(1,2): random.randint(10,100)}
            )
            # Publish orderbook
            topic = "OB"
            pub_message = f"{topic} {ob.model_dump_json()}"
            pub_socket.send_string(pub_message)
            print(f"[Broker] Published OrderBook update.")

if __name__ == "__main__":
    main()