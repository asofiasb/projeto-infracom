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
print(f"[Server] Listening on {HOST}:{PORT}...")

os.makedirs(SERVER_DIR, exist_ok=True)

while True:
    expected_seqnum = 0

    # Receive filename
    data, client_addr = sock.recvfrom(BUFFER_SIZE)
    seq = struct.unpack('>I', data[:4])[0]
    original_name = data[4:].decode().strip()
    print(f"[Server] Received filename '{original_name}' from {client_addr}")

    if seq == expected_seqnum:
        sock.sendto(f"ACK{seq}".encode(), client_addr)
        expected_seqnum = 1 - expected_seqnum
    else:
        sock.sendto(f"ACK{1 - expected_seqnum}".encode(), client_addr)

    # Receive file content
    save_path = os.path.join(SERVER_DIR, original_name)
    with open(save_path, "wb") as f:
        while True:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            if random.random() < 0.1:
                continue
            seq = struct.unpack('>I', chunk[:4])[0]
            data = chunk[4:]

            if data == PARADA:
                sock.sendto(f"ACK{seq}".encode(), client_addr)
                break

            if seq == expected_seqnum:
                f.write(data)
                f.flush()
                print(f"[Server] Packet seq={seq} received and written")
                sock.sendto(f"ACK{seq}".encode(), client_addr)
                expected_seqnum = 1 - expected_seqnum
            else:
                print(f"[Server] Duplicate packet seq={seq}, ignored")
                sock.sendto(f"ACK{1 - expected_seqnum}".encode(), client_addr)

    print(f"[Server] File saved as '{original_name}'")

    # Rename and send back the file
    new_name = change_file_name(original_name)
    sock.sendto(new_name.encode(), client_addr)

    with open(save_path, "rb") as f:
        seqnum = 0
        sock.settimeout(2.0)

        while True:
            data = f.read(BUFFER_SIZE - 4)
            if not data:
                break

            packed_data = struct.pack(">I", seqnum) + data

            while True:
                if random.random() < 0.1:
                    print(f"[Server] Simulated packet loss seq={seqnum}")
                    continue
                sock.sendto(packed_data, client_addr)
                print(f"[Server] Sent packet seq={seqnum}")

                try:
                    ack_data, _ = sock.recvfrom(BUFFER_SIZE)
                    if random.random() < 0.1:
                        print(f"[Server] Simulated ACK loss for seq={seqnum}")
                        continue
                    ack = ack_data.decode()
                    if ack == f"ACK{seqnum}":
                        print(f"[Server] ACK received seq={seqnum}")
                        seqnum = 1 - seqnum
                        break
                except socket.timeout:
                    print(f"[Server] Timeout waiting for ACK seq={seqnum}, resending...")

        # Send end signal
        end_packet = struct.pack(">I", seqnum) + PARADA
        while True:
            if random.random() < 0.1:
                print("[Server] Simulated loss of end packet")
                continue
            sock.sendto(end_packet, client_addr)
            print("[Server] Sending end packet")

            try:
                ack_data, _ = sock.recvfrom(BUFFER_SIZE)
                ack = ack_data.decode()
                if ack == f"ACK{seqnum}":
                    print("[Server] Final ACK received. Transfer complete.\n")
                    break
            except socket.timeout:
                print("[Server] Timeout waiting for final ACK, resending...")

    sock.settimeout(None)
