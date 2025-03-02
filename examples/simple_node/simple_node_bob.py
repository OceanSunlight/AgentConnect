import asyncio
import json
import os
import logging

from agent_connect.simple_node import SimpleNode
from agent_connect.utils.log_base import set_log_color_level

def generate_did_info(bob_node: SimpleNode):
    # Check if bob.json exists
    if os.path.exists("bob.json"):
        print("Loading existing Bob DID information")
        with open("bob.json", "r") as f:
            bob_info = json.load(f)
        bob_node.set_did_info(bob_info["private_key_pem"], bob_info["did"], bob_info["did_document_json"])
    else:
        print("Generating new Bob DID information")
        private_key_pem, did, did_document_json = bob_node.generate_did_document()
        bob_node.set_did_info(private_key_pem, did, did_document_json)
        
        # Save Bob's DID information
        with open("bob.json", "w") as f:
            json.dump({
                "private_key_pem": private_key_pem,
                "did": did,
                "did_document_json": did_document_json
            }, f)

async def main():
    # 使用新的接口创建节点，只指定ws路径
    bob_node = SimpleNode(
        host_domain="localhost", 
        host_port="8001",
        host_ws_path="/ws"
    )
    
    generate_did_info(bob_node)

    print(f"Bob's DID: {bob_node.did}")

    # Start the node
    bob_node.run()
    
    # Read Alice's DID
    with open("alice.json", "r") as f:
        alice_info = json.load(f)
    alice_did = alice_info["did"]
    
    try:
        # Send message to Alice
        message = "Hello Alice, I'm Bob!"
        success = await bob_node.send_message(message, alice_did)
        if success:
            print(f"Successfully sent message to {alice_did}")
        else:
            print(f"Failed to send message to {alice_did}")
        
        # Wait for Alice's reply
        while True:
            sender_did, reply = await bob_node.receive_message()
            print(f"Received reply from {sender_did}: {reply}")

    except asyncio.CancelledError:
        print("Bob node is shutting down...")
    finally:
        await bob_node.stop()

if __name__ == "__main__":
    set_log_color_level(logging.INFO)
    asyncio.run(main())
