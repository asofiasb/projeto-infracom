# Terceira Etapa
Está é a terceira etapa do projeto de Infraestrutura de Computação, onde implementamos um chat de sala única  utilizando o protocolo RDT3.0 adaptado para conexão bidirecional. O cliente pode se conectar, enviar mensagens, desconectar e outras funções relacionadas ao chat. O servidor gerencia as conexões e mensagens entre os clientes.

Adaptação do RDT3.0:
- O protocolo RDT3.0 foi adaptado para permitir conexões bidirecionais, onde o cliente pode enviar mensagens e receber respostas do servidor.
- A classe `RDT` é responsável por gerenciar o RDTSender e RDTReceiver, garantindo a entrega confiável de mensagens entre o cliente e o servidor.
- Cada RDT possui dois sockets: um para envio e outro para recebimento, permitindo comunicação bidirecional, visto que o protocolo RDT3.0 original é unidirecional.

# Instruções de Uso
O cliente e o servidor devem ser executados em terminais separados. A ordem de execução não importa, mas o servidor deve estar ativo antes do cliente tentar se conectar.

Os comandos disponíveis no chat são:
- `hi, meu nome eh <nome>`: Conecta o cliente ao chat com o nome especificado.
- `bye`: Desconecta o cliente do chat.
- `list`: Exibe a lista de clientes conectados.
- `mylist`: Exibe a lista de amigos do cliente.
- `addtomylist <nome>`: Adiciona um cliente à lista de amigos.
- `rmvfrommylist <nome>`: Remove um cliente da lista de amigos.
- `ban <nome>`: Inicia um processo de banimento de um cliente, onde os outros clientes podem votar para banir o cliente alvo.


# Equipe:
- Alvaro Brandao Neto - abn2
- Ana Maria Cunha Ribeiro - amcr
- Ana Sofia da Silva Barbosa - assb
- Gabriel Valenca Mayerhofer - gvm
- Heitor Riquelme Melo de Souza - hrms2
