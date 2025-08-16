
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

def broadcast(remetente, mensagem): # envia a mensagem para todos os clientes conectados, exceto o remetente
    for cli in clientes:
        if cli != remetente:
            amigos = amigos_cliente.get(cli, set())
            tagged_msg = mensagem
            remetente_nome = mensagem.split('/~')[1].split(':')[0] if '/~' in mensagem else ''
            if remetente_nome in amigos:
                tagged_msg = mensagem.replace(remetente_nome, f"[ amigo ] {remetente_nome}") # checa se eh amigo e add a tag
            rdt_server.send(tagged_msg.encode(), cli)

def servidor():
    print(f"[Server] Listening on {rdt_server.get_address()}...")

    while True:
        #tipo, seq, payload, addr = rdt_recv(sock)
        peer, msg = rdt_server.receive(timeout=0.01)
        msg = msg.decode()

        if msg.startswith("hi, meu nome eh "): # conecta cliente a sala
            nome = msg.split("hi, meu nome eh ")[1].strip()
            if nome in clientes.values():
                rdt_server.send("Nome já usado.".encode(), peer)
            else:
                clientes[peer] = nome
                amigos_cliente[peer] = set()
                broadcast(peer, f"{nome} entrou na sala")
            continue

        elif msg == "bye": # desconecta cliente da sala
            if peer in clientes:
                nome = clientes.pop(peer)
                amigos_cliente.pop(peer, None)
                broadcast(peer, f"{nome} entrou na sala")
            continue

        elif msg == "list": # exibe lista de clientes conectados
            lista = "Usuários: " + ", ".join(clientes.values())
            rdt_server.send(lista.encode(), peer)
            continue

        elif msg == "mylist": # exibe lista de amigos do cliente
            amigos = amigos_cliente.get(peer, set())
            lista_amigos = ", ".join(amigos) if amigos else "(nenhum)"
            rdt_server.send(f"Meus amigos: {lista_amigos}".encode(), peer)
            continue

        elif msg.startswith("addtomylist "): # adiciona amigo à lista do cliente
            alvo = msg.split("addtomylist ")[1].strip()
            if alvo in clientes.values():
                amigos_cliente[peer].add(alvo)
                rdt_server.send(f"[ {alvo} ] adicionado à lista de amigos".encode(), peer)
            else:
                rdt_server.send(f"[ {alvo} ] não está na sala".encode(), peer)
            continue

        elif msg.startswith("rmvfrommylist "): # remove amigo da lista do cliente
            alvo = msg.split("rmvfrommylist ")[1].strip()
            amigos_cliente[peer].discard(alvo)
            rdt_server.send(f"[ {alvo} ] removido da sua lista de amigos".encode(), peer)
            continue

        elif msg.startswith("ban "): # vota para banir um cliente
            alvo = msg.split("ban ")[1].strip()
            if alvo not in clientes.values():
                rdt_server.send(f"[ {alvo} ] não está na sala".encode(), peer)
                continue
            if alvo not in ban_votes:
                ban_votes[alvo] = set()
            ban_votes[alvo].add(clientes[peer])
            votos = len(ban_votes[alvo])
            necessario = (len(clientes)//2)+1
            broadcast(peer, f"[ {alvo} ] votou para banir {votos}/{necessario} votos")

            if votos >= necessario:
                alvo_peer = [k for k,v in clientes.items() if v==alvo][0]
                rdt_server.send(f"Você foi banido por votação de {votos} clientes.".encode(), alvo_peer)
                clientes.pop(alvo_peer)
                amigos_cliente.pop(alvo_peer, None)
            continue

        elif peer in clientes: # mensagem de chat normal
            nome = clientes[peer]
            hora = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            ip, port = peer.get_address()
            full_msg = f"{ip}:{port}/~{nome}: {msg} {hora}"
            broadcast(peer, full_msg) # envia para todos os clientes, exceto o remetente

if __name__ == "__main__":
    servidor()