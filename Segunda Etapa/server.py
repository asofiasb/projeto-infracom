import socket
import os
import struct
import random

HOST, PORT = "127.0.0.1", 6001
BUFFER_SIZE = 1024
PARADA = b"END"

SERVER_DIR = os.path.join(os.path.dirname(__file__), "server")

def change_file_name(filename: str) -> str:
    base, ext = os.path.splitext(os.path.basename(filename))
    return f"{base}_enviado{ext}" if ext else f"{base}_enviado"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Servidor em {HOST}:{PORT}, aguardando…")

os.makedirs(SERVER_DIR, exist_ok=True)

while True:

    ## receive the filename from the client
    data, client_addr = sock.recvfrom(BUFFER_SIZE)
    original_name = data.decode().strip()
    print(f"RECEIVED '{original_name}' from {client_addr}")

    ## receive the file content from the client
    save_original_path = os.path.join(SERVER_DIR, original_name)
    with open(save_original_path, "wb") as f:
        expected_seqnum = 0
        while True:
            chunk, _ = sock.recvfrom(BUFFER_SIZE) ## receive packet containing sequence number and data
            if random.random() < 0.1: ## simulates packet loss
              continue
            seq = struct.unpack('>I', chunk[:4])[0] ## unpack sequence number and data
            data = chunk[4:]

            if data == PARADA: ## wait for the end signal
                break

            ## if sequence number received is the expected, send ack and update it, else resend last ack (client sent a duplicate)
            if seq == expected_seqnum:
                f.write(data)
                f.flush()
                ack = f"ACK{seq}".encode()
                sock.sendto(ack, client_addr) 
                expected_seqnum = 1 - expected_seqnum
            else:
                ack = f"ACK{1-expected_seqnum}".encode()
                sock.sendto(ack, client_addr)

            
    print(f"File saved as '{original_name}'")

    ## change the file name and send it back to the client
    new_name = change_file_name(original_name)

    sock.sendto(new_name.encode(), client_addr)

    with open(save_original_path, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, client_addr)

    ## send the end signal to the client
    sock.sendto(PARADA, client_addr)
    print(f"'{new_name}' sent back to {client_addr}\n")