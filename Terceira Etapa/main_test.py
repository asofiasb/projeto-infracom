import sys
from rdt import RDT, Peer

if len(sys.argv) != 2:
    print("Usage: python rdt.py <port>")
    sys.exit(1)

my_port = int(sys.argv[1])
rdt = RDT(port=my_port)
connected_peer = None

print("--- RDT Bidirectional Test ---")
print(f"This instance is listening on (receiver): {rdt.get_address()}")
print(f"Sender socket is on: {rdt.sender.get_address()}")
print("Commands:")
print("  connect <host> <port> - Connect to another RDT instance (their receiver port).")
print("  send <message>        - Send a message to the connected peer.")
print("  broadcast <message>   - Send a message to all connected peers.")
print("  receive               - Check for incoming messages.")
print("  exit                  - Close the application.")
print("---------------------------------")

while True:
    peer, content = rdt.receive(timeout=0.01)
    if peer:
        print(f"\n<-- Message received from {peer}: {content}")

    try:
        command_input = input(f"RDT@{my_port}> ").strip().split()
        if not command_input:
            continue

        command = command_input[0].lower()

        if command == "connect" and len(command_input) == 3:
            host, port = command_input[1], int(command_input[2])
            if rdt.connect(host, port):
                connected_peer = Peer(host, port)
            else:
                connected_peer = None
        
        elif command == "broadcast" and len(command_input) > 1:
            data = ' '.join(command_input[1:])
            rdt.broadcast(data)

        elif command == "send" and len(command_input) > 1:
            if not connected_peer:
                print("Error: Not connected to any peer. Use 'connect' first.")
                continue
            data = ' '.join(command_input[1:])
            rdt.send(data, connected_peer)

        elif command == "receive":
            peer, content = rdt.receive(timeout=1)
            if peer:
                print(f"\n<-- Message received from {peer}: {content}")
            else:
                print("No new messages.")

        elif command == "exit":
            print("Exiting RDT system.")
            break
        else:
            print("Invalid command. Please try again.")

    except (KeyboardInterrupt, EOFError):
        print("\nExiting RDT system.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
