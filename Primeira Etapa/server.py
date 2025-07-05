import socket
import os

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

    data, client_addr = sock.recvfrom(BUFFER_SIZE)
    original_name = data.decode().strip()
    print(f"RECEIVED '{original_name}' from {client_addr}")

    save_original_path = os.path.join(SERVER_DIR, original_name)
    with open(save_original_path, "wb") as f:
        while True:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            if chunk == PARADA:
                break
            f.write(chunk)
    print(f"File saved as '{original_name}'")

    new_name = change_file_name(original_name)

    sock.sendto(new_name.encode(), client_addr)

    with open(save_original_path, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, client_addr)

    sock.sendto(PARADA, client_addr)
    print(f"'{new_name}' sent back to {client_addr}\n")