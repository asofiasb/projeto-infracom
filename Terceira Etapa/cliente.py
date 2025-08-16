
import struct
import threading
from rdt.rdt import RDT, Peer

HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024
PACKET_FORMAT = "!BBH" # tipo da mensagem (ack, msg), seq, tamanho do payload

def listen(rdt: RDT): # espera respostas do servidor
    while True:
        peer, payload = rdt.receive(timeout=0.01)
        msg = payload.decode()
        print(msg)

def main():
    rdt_client = RDT()
    rdt_client.connect(HOST, PORT)

    threading.Thread(target=listen, args=(rdt_client,), daemon=True).start()

    while True:
        msg = input()
        rdt_client.send(msg.encode(), Peer(HOST, PORT))

if __name__ == "__main__":
    main()