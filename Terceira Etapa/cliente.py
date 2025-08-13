import socket
import struct
import threading

HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024
PACKET_FORMAT = "!BBH" # tipo da mensagem (ack, msg), seq, tamanho do payload

def rdt_send(sock, addr, seq, data, tipo=0): # formato do rdt_send foi alterado com relação a segunda etapa para facilitar o uso
    header = struct.pack(PACKET_FORMAT, tipo, seq, len(data))
    sock.sendto(header + data, addr)

def rdt_recv(sock): # rdt_recv foi alterado para lidar com o novo formato de pacotes
    data, addr = sock.recvfrom(BUFFER_SIZE)
    tipo, seq, size = struct.unpack(PACKET_FORMAT, data[:4])
    payload = data[4:4+size]
    return tipo, seq, payload, addr

def listen(sock): # espera respostas do servidor
    while True:
        tipo, seq, payload, addr = rdt_recv(sock)
        msg = payload.decode()
        print(msg)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0)) # porta aleatória do cliente
    server_addr = (HOST, PORT)

    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    while True:
        msg = input()
        rdt_send(sock, server_addr, 0, msg.encode())

if __name__ == "__main__":
    main()