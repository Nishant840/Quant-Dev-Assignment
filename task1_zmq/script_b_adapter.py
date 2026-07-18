import zmq

def main():
    context = zmq.Context()
    
    #     ----- Order Routing (A->B->C) ------
    # REP socket: listen for orders from strategy (script A)
    strategy_rep = context.socket(zmq.REP)
    strategy_rep.bind("tcp://*:5557")

    # REQ socket: forward those orders to Broker (script C)
    broker_req = context.socket(zmq.REQ)
    broker_req.connect("tcp://localhost:5555")

    #      ----- Market Data & Execution (C->B->A) -----
    # SUB socket: Listen to updates from broker (script C)
    broker_sub = context.socket(zmq.SUB)
    broker_sub.connect("tcp://localhost:5556")

    # subscribe to all topics
    broker_sub.setsockopt_string(zmq.SUBSCRIBE,"")

    # PUB socket: Broadcast those updates down to strategy (script A)
    strategy_pub = context.socket(zmq.PUB)
    strategy_pub.bind("tcp://*:5558")


    # --- ZMQ Poller ---
    # we must listen to strategy_rep and broker_sub simultaneously
    poller = zmq.Poller()
    poller.register(strategy_rep, zmq.POLLIN) # watch for incoming orders
    poller.register(broker_sub, zmq.POLLIN)   # watch for incoming market data

    print("[Adapter] Started. Acting as proxy between Strategy and Broker...")

    while True:
        sockets = dict(poller.poll())   # dictionary of which sockets are ready

        # Scenario 1: An order just arrived from script A
        if strategy_rep in sockets:
            msg_from_strategy = strategy_rep.recv_string()
            print(f"[Adapter] Forwarding Order to Broker: {msg_from_strategy}")

            broker_req.send_string(msg_from_strategy)

            ack_from_broker = broker_req.recv_string()

            strategy_rep.send_string(ack_from_broker)
            print(f"[Adapter] Forwarded ACK to strategy: {ack_from_broker}")

        # Scenario 2: Market data or an Execution arrived from script C
        if broker_sub in sockets:
            msg_from_broker = broker_sub.recv_string()
            strategy_pub.send_string(msg_from_broker)

if __name__ == "__main__":
    main()