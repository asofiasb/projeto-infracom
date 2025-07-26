import socket
from os import listdir, makedirs
from os.path import isfile, join, dirname
import struct
import random

HOST, PORT = "127.0.0.1", 6000
SERVER_HOST, SERVER_PORT = "127.0.0.1", 6001
BUFFER_SIZE = 1024

FILES_DIR = join(dirname(__file__), "files")
CLIENT_DIR = join(dirname(__file__), "client")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

def sendFile(filename):
    # Send filename to server
    sock.settimeout(2.0)
    seqnum = 0
    file_name = filename.split("/")[-1]
    packed_seqnum = struct.pack('>I', seqnum)
    file_name_packet = packed_seqnum + file_name.encode()

    while True:
        sock.sendto(file_name_packet, (SERVER_HOST, SERVER_PORT))
        try:
            ackrcv, _ = sock.recvfrom(BUFFER_SIZE)
            if random.random() < 0.1:
                continue
            ack = ackrcv.decode()
            if ack == f"ACK{seqnum}":
                print(f"[Client] Sending file: {file_name}")
                seqnum = 1 - seqnum
                break
        except socket.timeout:
            print("[Client] Timeout on filename send")

    # Send file content to server
    with open(filename, "rb") as file:
        while True:
            data = file.read(BUFFER_SIZE - 4)
            if not data:
                break

            packed_seqnum = struct.pack('>I', seqnum)
            datafull = packed_seqnum + data

            while True:
                if random.random() < 0.1:
                    print(f"[Client] Simulated packet loss seq={seqnum}")
                    continue
                sock.sendto(datafull, (SERVER_HOST, SERVER_PORT))
                print(f"[Client] Sent packet seq={seqnum}")
                try:
                    ackrcv, _ = sock.recvfrom(BUFFER_SIZE)
                    if random.random() < 0.1:
                        print(f"[Client] Simulated ACK loss for seq={seqnum}")
                        continue
                    ack = ackrcv.decode()
                    if ack == f"ACK{seqnum}":
                        print(f"[Client] ACK received seq={seqnum}")
                        seqnum = 1 - seqnum
                        break
                except socket.timeout:
                    print(f"[Client] Timeout waiting for ACK seq={seqnum}, resending...")

    # Send end signal
    packed_seqnum = struct.pack('>I', seqnum)
    dataend = packed_seqnum + b"END"
    while True:
        if random.random() < 0.1:
            print("[Client] Simulated loss of end packet")
            continue
        sock.sendto(dataend, (SERVER_HOST, SERVER_PORT))
        print("[Client] Sending end packet")
        try:
            ackrcv, _ = sock.recvfrom(BUFFER_SIZE)
            ack = ackrcv.decode()
            if ack == f"ACK{seqnum}":
                print("[Client] File sent successfully.\n")
                break
        except socket.timeout:
            print("[Client] Timeout on end packet, resending...")

def waitForResponse():
    sock.settimeout(5.0)
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        if data:
            print(f"[Client] Response from server: {data.decode()}")
            return data.decode()
        else:
            return None
    except socket.timeout:
        print("[Client] No response received from server.")
        return None

def receiveFile(filename):
    sock.settimeout(5.0)
    seqnum = 0
    file_path = join(CLIENT_DIR, filename)

    with open(file_path, "wb") as file:
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                if random.random() < 0.1:
                    print("[Client] Simulated incoming packet loss")
                    continue

                recv_seq = struct.unpack(">I", data[:4])[0]
                content = data[4:]

                if content == b"END":
                    print("[Client] End packet received")
                    sock.sendto(f"ACK{recv_seq}".encode(), (SERVER_HOST, SERVER_PORT))
                    break

                if recv_seq == seqnum:
                    file.write(content)
                    file.flush()
                    print(f"[Client] Packet seq={recv_seq} received and written")
                    sock.sendto(f"ACK{recv_seq}".encode(), (SERVER_HOST, SERVER_PORT))
                    seqnum = 1 - seqnum
                else:
                    print(f"[Client] Duplicate packet seq={recv_seq}, ignored")
                    sock.sendto(f"ACK{1 - seqnum}".encode(), (SERVER_HOST, SERVER_PORT))

            except socket.timeout:
                print("[Client] Timeout waiting for packet. Closing reception.")
                break

    print(f"[Client] File '{filename}' received successfully.")

def closeConnection():
    sock.close()
    print("[Client] Connection closed.")

def listFiles():
    files = [f for f in listdir(FILES_DIR) if isfile(join(FILES_DIR, f))]
    files_ = zip([i for i in range(1, len(files) + 1)], files)
    for i, file in files_:
        print(f"    {i}. {file}")
    return files

makedirs(CLIENT_DIR, exist_ok=True)

while True:
    print("1. Send File")
    print("2. Close Connection")
    choice = input("Enter your choice: ")

    if choice == '1':
        files = listFiles()
        filename = input("Enter the filename number: ")
        file = join(FILES_DIR, files[int(filename) - 1])

        sendFile(file)
        returned_filename = waitForResponse()
        if returned_filename:
            receiveFile(returned_filename)

    elif choice == '2':
        closeConnection()
        break
    else:
        print("Invalid choice. Try again.")

    print("----------\n")
