from fastapi import FastAPI
from pydantic import BaseModel
import time
import threading

app = FastAPI(title="Quant API - Threading Version")

class Order(BaseModel):
    symbol:     str
    side:       str
    quantity:   int
    price:      float

mock_database = {
    "cash_balance": 100000.0,
    "positions": {}
}

@app.post("/order")
def place_order(order: Order):
    # This will print exactly which OS Thread is handling the request!
    current_thread = threading.get_ident()
    print(f"[Thread {current_thread}] Received {order.side} order for {order.symbol}")
    time.sleep(1.0)

    cost = order.quantity * order.price
    if order.side == "BUY":
        mock_database["cash_balance"] -= cost
        mock_database["positions"][order.symbol] = mock_database["positions"].get(order.symbol,0) + order.quantity

    return {
        "status": "FILLED",
        "message": f"Successfully executed {order.side} for {order.symbol}",
        "remaining_cash": mock_database["cash_balance"]
    }

@app.get("/portfolio")
def get_portfolio():
    return mock_database

if __name__ == "__main__":
    import uvicorn
    print("Starting Threading Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)