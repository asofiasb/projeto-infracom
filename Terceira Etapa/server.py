
import datetime
from rdt.rdt import RDT, Peer

HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024
PACKET_FORMAT = "!BBH" # tipo da mensagem (ack, msg), seq, tamanho do payload

clientes = {}  # addr -> nome -- lista de clientes conectados
amigos_cliente = {}  # addr -> set de amigos -- lista de amigos de cada cliente
ban_votes = {}  # alvo -> set de votantes

# Inicializa o RDT server
rdt_server = RDT(host=HOST, port=PORT)

def servidor():
    print(f"[Server] Listening on {rdt_server.get_address()}...")

    while True:
        #tipo, seq, payload, addr = rdt_recv(sock)
        peer, msg = rdt_server.receive(timeout=0.01)
        msg = msg.decode()

        if msg.startswith("hi, meu nome eh "): # conecta cliente a sala
            nome = msg.split("hi, meu nome eh ")[1].strip()
            if nome in clientes.values():
                rdt_server.send("Nome já usado.", peer)
            else:
                clientes[peer] = nome
                amigos_cliente[peer] = set()
                rdt_server.broadcast(f"{nome} entrou na sala")
            continue

        elif msg == "bye": # desconecta cliente da sala
            if peer in clientes:
                nome = clientes.pop(peer)
                amigos_cliente.pop(peer, None)
                rdt_server.broadcast(f"{nome} saiu da sala")
            continue

        elif msg == "list": # exibe lista de clientes conectados
            lista = "Usuários: " + ", ".join(clientes.values())
            rdt_server.send(lista, peer)
            continue

        elif msg == "mylist": # exibe lista de amigos do cliente
            amigos = amigos_cliente.get(peer, set())
            lista_amigos = ", ".join(amigos) if amigos else "(nenhum)"
            rdt_server.send(f"Meus amigos: {lista_amigos}", peer)
            continue

        elif msg.startswith("addtomylist "): # adiciona amigo à lista do cliente
            alvo = msg.split("addtomylist ")[1].strip()
            if alvo in clientes.values():
                amigos_cliente[peer].add(alvo)
                rdt_server.send(f"[ {alvo} ] adicionado à lista de amigos")
            else:
                rdt_server.send(f"[ {alvo} ] não está na sala", peer)
            continue

        elif msg.startswith("rmvfrommylist "): # remove amigo da lista do cliente
            alvo = msg.split("rmvfrommylist ")[1].strip()
            amigos_cliente[peer].discard(alvo)
            rdt_server.send(f"[ {alvo} ] removido da sua lista de amigos", peer)
            continue

        elif msg.startswith("ban "): # vota para banir um cliente
            alvo = msg.split("ban ")[1].strip()
            if alvo not in clientes.values():
                rdt_server.send(f"[ {alvo} ] não está na sala", peer)
                continue
            if alvo not in ban_votes:
                ban_votes[alvo] = set()
            ban_votes[alvo].add(clientes[peer])
            votos = len(ban_votes[alvo])
            necessario = (len(clientes)//2)+1
            rdt_server.broadcast(f"[ {alvo} ] ban {votos}/{necessario}")

            if votos >= necessario:
                alvo_peer = [k for k,v in clientes.items() if v==alvo][0]
                rdt_server.send(f"Você foi banido por votação de {votos} clientes.", alvo_peer)
                clientes.pop(alvo_peer)
                amigos_cliente.pop(alvo_peer, None)
            continue

        elif peer in clientes: # mensagem de chat normal
            nome = clientes[peer]
            hora = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            ip, port = peer.get_address()
            full_msg = f"{ip}:{port}/~{nome}: {msg} {hora}"
            rdt_server.broadcast(full_msg) # envia para todos os clientes, exceto o remetente

if __name__ == "__main__":
    servidor()