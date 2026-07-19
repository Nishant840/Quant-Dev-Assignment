import time
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000"

def check_portfolio():
    response = requests.get(f"{BASE_URL}/portfolio")
    print(f"Portfolio State: {response.json()}")

def send_order(order_id: int):
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 10,
        "price": 150.0
    }
    print(f"--> [Thread] {order_id} Sending Order")

    response = requests.post(f"{BASE_URL}/order", json=payload)
    print(f"<-- [Thread {order_id} Reply: {response.json()['message']}]")

def main():
    print("1. Checking Intial Portfolio...")
    check_portfolio()

    print("\n2. Blasting 5 concurrent orders to test...")
    start_time = time.time()

    # Using Threadpool to fire 5 HTTP requests at exact same millisecond
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(1,6):
            executor.submit(send_order,i)

    end_time = time.time()
    print(f"\n All 5 orders processed in {end_time - start_time:.2f} seconds")

    print("\n3. checking final Portfolio...")
    check_portfolio()

if __name__ == "__main__":
    main()