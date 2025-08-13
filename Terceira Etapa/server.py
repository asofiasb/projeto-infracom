import socket
import struct
import datetime

HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024
PACKET_FORMAT = "!BBH" # tipo da mensagem (ack, msg), seq, tamanho do payload

clientes = {}  # addr -> nome -- lista de clientes conectados
amigos_cliente = {}  # addr -> set de amigos -- lista de amigos de cada cliente
ban_votes = {}  # alvo -> set de votantes

def rdt_send(sock, addr, seq, data, tipo=0): # formato do rdt_send foi alterado com relação a segunda etapa para facilitar o uso
    header = struct.pack(PACKET_FORMAT, tipo, seq, len(data))
    sock.sendto(header + data, addr)

def rdt_recv(sock): # rdt_recv foi alterado para lidar com o novo formato de pacotes
    data, addr = sock.recvfrom(BUFFER_SIZE)
    tipo, seq, size = struct.unpack(PACKET_FORMAT, data[:4])
    payload = data[4:4+size]
    return tipo, seq, payload, addr

def broadcast(sock, remetente, mensagem): # envia a mensagem para todos os clientes conectados, exceto o remetente
    for cli in clientes:
        if cli != remetente:
            amigos = amigos_cliente.get(cli, set())
            tagged_msg = mensagem
            remetente_nome = mensagem.split('/~')[1].split(':')[0] if '/~' in mensagem else ''
            if remetente_nome in amigos:
                tagged_msg = mensagem.replace(remetente_nome, f"[ amigo ] {remetente_nome}") # checa se eh amigo e add a tag
            rdt_send(sock, cli, 0, tagged_msg.encode())

def servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[Server] Listening on {HOST}:{PORT}...")

    while True:
        tipo, seq, payload, addr = rdt_recv(sock)
        msg = payload.decode()

        if msg.startswith("hi, meu nome eh "): # conecta cliente a sala
            nome = msg.split("hi, meu nome eh ")[1].strip()
            if nome in clientes.values():
                rdt_send(sock, addr, seq, "Nome já usado.".encode())
            else:
                clientes[addr] = nome
                amigos_cliente[addr] = set()
                broadcast(sock, addr, f"{nome} entrou na sala")
            continue

        elif msg == "bye": # desconecta cliente da sala
            if addr in clientes:
                nome = clientes.pop(addr)
                amigos_cliente.pop(addr, None)
                broadcast(sock, addr, f"{nome} saiu da sala")
            continue

        elif msg == "list": # exibe lista de clientes conectados
            lista = "Usuários: " + ", ".join(clientes.values())
            rdt_send(sock, addr, seq, lista.encode())
            continue

        elif msg == "mylist": # exibe lista de amigos do cliente
            amigos = amigos_cliente.get(addr, set())
            lista_amigos = ", ".join(amigos) if amigos else "(nenhum)"
            rdt_send(sock, addr, seq, f"Meus amigos: {lista_amigos}".encode())
            continue

        elif msg.startswith("addtomylist "): # adiciona amigo à lista do cliente
            alvo = msg.split("addtomylist ")[1].strip()
            if alvo in clientes.values():
                amigos_cliente[addr].add(alvo)
                rdt_send(sock, addr, seq, f"{alvo} adicionado à sua lista de amigos".encode())
            else:
                rdt_send(sock, addr, seq, f"{alvo} não está na sala".encode())
            continue

        elif msg.startswith("rmvfrommylist "): # remove amigo da lista do cliente
            alvo = msg.split("rmvfrommylist ")[1].strip()
            amigos_cliente[addr].discard(alvo)
            rdt_send(sock, addr, seq, f"{alvo} removido da sua lista de amigos".encode())
            continue

        elif msg.startswith("ban "): # vota para banir um cliente
            alvo = msg.split("ban ")[1].strip()
            if alvo not in clientes.values():
                rdt_send(sock, addr, seq, f"{alvo} não está na sala".encode())
                continue
            if alvo not in ban_votes:
                ban_votes[alvo] = set()
            ban_votes[alvo].add(clientes[addr])
            votos = len(ban_votes[alvo])
            necessario = (len(clientes)//2)+1
            broadcast(sock, None, f"[ {alvo} ] ban {votos}/{necessario}")
            if votos >= necessario:
                alvo_addr = [k for k,v in clientes.items() if v==alvo][0]
                rdt_send(sock, alvo_addr, seq, "Você foi banido.".encode())
                clientes.pop(alvo_addr)
                amigos_cliente.pop(alvo_addr, None)
            continue

        elif addr in clientes: # mensagem de chat normal
            nome = clientes[addr]
            hora = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            ip, port = addr
            full_msg = f"{ip}:{port}/~{nome}: {msg} {hora}"
            broadcast(sock, addr, full_msg) # envia para todos os clientes, exceto o remetente

if __name__ == "__main__":
    servidor()