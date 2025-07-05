import socket
import os

HOST, PORT  = "127.0.0.1", 6001
BUFFER_SIZE = 1024
PARADA  = b"END"

def change_file_name(filename: str) -> str:
    base, ext = os.path.splitext(os.path.basename(filename))
    return f"{base}_enviado{ext}" if ext else f"{base}_enviado"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Servidor em {HOST}:{PORT}, aguardando…")

while True:

    data, client_addr = sock.recvfrom(BUFFER_SIZE)
    original_name = data.decode().strip()
    print(f"RECEIVED '{original_name}' from {client_addr}")

    new_name = change_file_name(original_name)
    with open(new_name, "wb") as f:
        while True:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            if chunk == PARADA:
                break
            f.write(chunk)
    print(f"File saved as '{new_name}'")

    sock.sendto(new_name.encode(), client_addr)

    with open(new_name, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, client_addr)

    sock.sendto(PARADA, client_addr)
    print(f"'{new_name}' sent back to {client_addr}\n")