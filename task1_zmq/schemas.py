from pydantic import BaseModel
from typing import Dict

class Order(BaseModel):
    order_id:   str
    symbol:     str
    side:       str
    price:      float
    quantity:   int

class Execution(BaseModel):
    order_id:           str
    symbol:             str
    side:               str
    price:              float
    filled_quantity:    int
    status:             str

class OrderBook(BaseModel):
    symbol:     str
    bids:       Dict[float, int]
    asks:       Dict[float, int]
