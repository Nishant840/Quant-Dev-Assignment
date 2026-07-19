import zmq
import json
import time
import threading
from schemas import Order, Execution, OrderBook

class Portfolio:
    
    def __init__(self):
        self.position           = 0
        self.avg_price          = 0.0
        self.realised_pnl       = 0.0
        self.current_orderbook  = {}
    
    def on_fill(self, execution:Execution):
        qty     = execution.filled_quantity
        price   = execution.price
        
        if execution.side == "BUY":
            if self.position >= 0:
                # Increasing a long position and calculating new average price
                total_value = (self.position*self.avg_price) + (qty*price)
                self.position += qty
                self.avg_price = total_value / self.position
            else:
                # Buying to cover a short position: It generates realised PnL
                cover_qty = min(abs(self.position), qty)
                self.realised_pnl += cover_qty * (self.avg_price - price) # Short PnL
                self.position += qty
                if self.position > 0:
                    self.avg_price = price # Flipped from short to long
                elif self.position == 0:
                    self.avg_price = 0.0
        elif execution.side == "SELL":
            if self.position <= 0:
                # Increasing a short position
                total_value = (abs(self.position) * self.avg_price)+(qty*price)
                self.position -= qty
                self.avg_price = total_value / abs(self.position)
            else:
                # Selling a long position: This generates Realised PnL!
                sell_qty = min(self.position, qty)
                self.realised_pnl += sell_qty*(price - self.avg_price) # Long PnL
                self.position -= qty
                if self.position < 0:
                    self.avg_price = price # Flipped from long to short
                elif self.position == 0:
                    self.avg_price = 0.0

    def print_dashboard(self):
        print("\n" + "="*40)
        print("STRATEGY DASHBOARD")
        print(f"Open Position : {self.position} AAPL")
        print(f"Average Price : ${self.avg_price:.2f}")
        print(f"Realised PnL  : ${self.realised_pnl:.2f}")
        print("-" * 40)
        if self.current_orderbook:
            print("ORDER BOOK (AAPL):")
            print(f"  Bids: {self.current_orderbook.get('bids')}")
            print(f"  Asks: {self.current_orderbook.get('asks')}")
        print("="*40 + "\n")

# Global portfolio instance
portfolio = Portfolio()

def market_data_thread():
    """Background thread to listen to the SUB socket continuously."""
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect("tcp://localhost:5558")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE,"") # Listen to all topics

    while True:
        message = sub_socket.recv_string()

        topic, payload = message.split(" ", 1)
        data = json.loads(payload)

        if topic == "EXEC":
            exec_obj = Execution(**data)
            portfolio.on_fill(exec_obj)
            portfolio.print_dashboard()

        elif topic == "OB":
            ob_obj = OrderBook(**data)
            portfolio.current_orderbook = ob_obj.model_dump()

def main():
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    req_socket.connect("tcp://localhost:5557")

    # Start the market data listener in background
    listener = threading.Thread(target=market_data_thread, daemon=True)
    listener.start()

    # for reconnecting
    time.sleep(1)
    
    orders_to_send = [
        Order(order_id="O1", symbol="AAPL", side="BUY", price=150.0, quantity=100),
        Order(order_id="O2", symbol="AAPL", side="SELL", price=155.0, quantity=50),  # Closes 50 long, triggers PnL
        Order(order_id="O3", symbol="AAPL", side="SELL", price=152.0, quantity=100), # Closes remaining 50 long, goes 50 short
        Order(order_id="O4", symbol="AAPL", side="BUY", price=148.0, quantity=50),   # Covers 50 short, triggers PnL
        Order(order_id="O5", symbol="AAPL", side="BUY", price=151.0, quantity=20)    # Opens 20 long
    ]

    print("[Strategy] Starting automated order sequence...")

    for order in orders_to_send:
        # send order
        req_socket.send_string(order.model_dump_json())

        # wait for broker ACK
        reply = req_socket.recv_string()
        print(f"[Strategy] Received ACK for {order.order_id}: {reply}")

        # Wait 3 second to watch update
        time.sleep(3)

    print("[Strategy] All orders completed. Keeping dashboard alive for 5 seconds...")
    time.sleep(5)

if __name__ == "__main__":
    main()