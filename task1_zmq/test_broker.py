import zmq
import json

def test_broker():
    context = zmq.Context()
    
    # Connect a REQ socket to Broker's REP (Port 5555)
    req_socket = context.socket(zmq.REQ)
    req_socket.connect("tcp://localhost:5555")
    
    print("--- Test 1: Sending Bad Data (Missing 'price' field) ---")
    bad_order = {
        "order_id": "T1",
        "symbol": "AAPL",
        "side": "BUY",
        # "price" is missing intentionally to trigger Pydantic error
        "quantity": 100
    }
    req_socket.send_string(json.dumps(bad_order))
    reply = req_socket.recv_string()
    print(f"Broker Reply: {reply}\n")
    
    print("--- Test 2: Sending Good Data ---")
    good_order = {
        "order_id": "T2",
        "symbol": "AAPL",
        "side": "BUY",
        "price": 150.50,
        "quantity": 100
    }
    req_socket.send_string(json.dumps(good_order))
    reply = req_socket.recv_string()
    print(f"Broker Reply: {reply}\n")

if __name__ == "__main__":
    test_broker()
