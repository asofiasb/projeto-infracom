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

ackrecebido = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST,PORT))

def sendFile(filename):
    ## send filename to server
    file_name = filename.split("/")[-1]
    sock.sendto(file_name.encode(), (SERVER_HOST, SERVER_PORT))
    print(f"Sending file: {file_name} to server at {SERVER_HOST}:{SERVER_PORT}")

    seqnum = 0
    sock.settimeout(2.0)

    ## send file content to server
    with open(filename, "rb") as file:
        while True:
            data = file.read(BUFFER_SIZE-4)
            if not data:
                break
            
            packed_seqnum = struct.pack('>I', seqnum)
            datafull = packed_seqnum + data ## packs sequence number and data
            while True:
              if random.random() < 0.1: ## simulates packet loss 
                  continue
              sock.sendto(datafull, (SERVER_HOST, SERVER_PORT)) ## sends packet containing sequence number and data
              try:
                ackrcv, _ = sock.recvfrom(BUFFER_SIZE) ## receives ack
                if random.random() < 0.1: ## simulates ack loss
                  continue
                ack = ackrcv.decode()

                ## if expected ack is received, breaks loop and sends next packet, else resends same packet
                if ack == f"ACK{seqnum}": 
                  seqnum = 1 - seqnum
                  break 

              ## timeout restarts loop and resends packet
              except socket.timeout: 
                  print("Timeout") 
        
    sock.settimeout(4.0)
    ## send end signal to server
    packed_seqnum = struct.pack('>I', seqnum)
    dataend = packed_seqnum + b"END"
    sock.sendto(dataend, (SERVER_HOST, SERVER_PORT))
    print(f"File {filename} sent successfully.")

def waitForResponse():
    sock.settimeout(5.0)
    try:
        ## wait for response from server (filename)
        data, addr = sock.recvfrom(BUFFER_SIZE)
        if data:
            print(f"Response received from {addr}: {data.decode()}")
            
        data = data.decode()
        if data:
            return data
        else:
            print("No valid response received.")
            return None
            
    except socket.timeout:
        print("No response received from server.")
        return None

def receiveFile(filename):
    sock.settimeout(5.0)
    ## receive file content from server
    file = join(CLIENT_DIR, filename)
    with open(file, "wb") as file:
        while True:
            try:
              data, addr = sock.recvfrom(BUFFER_SIZE)
              if not data or data == b"END":
                  break
              file.write(data)
              file.flush()
            except socket.timeout:
                print("Timeout while receiving file packet. Closing connection.")
                break

    print(f"File {filename} received successfully.")

def closeConnection():
    sock.close()
    print("Connection closed.")

def listFiles():
    files = [f for f in listdir(FILES_DIR) if isfile(join(FILES_DIR, f))]
    files_ = zip([i for i in range(1, len(files) + 1)], files)
    for i, file in files_:
        print(f"    {i}. {file}")
    return files

# ---------------

makedirs(CLIENT_DIR, exist_ok=True)

while True:
    print("1. Send File")
    print("2. Close Connection")
    choice = input("Enter your choice: ")

    if choice == '1':
        files = listFiles()
        filename = input("Enter the filename to send: ")
        file = join(FILES_DIR,  files[int(filename) - 1])

        sendFile(file)
        returned_filename = waitForResponse()
        if (returned_filename):
            receiveFile(returned_filename)
    elif choice == '2':
        closeConnection()
        break
    else:
        print("Invalid choice. Please try again.")
    
    print("----------\n")

    