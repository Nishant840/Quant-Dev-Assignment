from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

app = FastAPI(title="Quant API - Asyncio Version")

# data validation 
class Order(BaseModel):
    symbol:     str
    side:       str
    quantity:   int
    price:      float

# in memory mock database
mock_database = {
    "cash_balance": 100000.0,
    "positions": {}
}

@app.post("/order")
async def place_order(order: Order):
    print(f"[Async Server] Received {order.side} order for {order.quantity} {order.symbol}")

    await asyncio.sleep(1.0)

    # Mock some basic logic
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
async def get_portfolio():
    return mock_database

if __name__ == "__main__":
    import uvicorn
    # Uvicorn is the lightning-fast web server that runs FastAPI
    print("Starting Async Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)