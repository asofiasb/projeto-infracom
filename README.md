# projeto-infracom

Projeto da cadeira de Infraestrutura de Comunicação para implementação de um chat de sala única usando o protocolo de comunicação UDP. O projeto está dividido em três etapas:

- **Etapa 1**: Implementação do envio e recebimento de arquivos usando UDP.
- **Etapa 2**: Implementação do RDT 3.0 sobre UDP na camada de aplicação, utilizando o código de transferência de arquivos da primeira parte.
- **Etapa 3**: Criação de um chat em grupo utilizando o RDT 3.0 implementado na segunda parte.

## 📂 Estrutura do Repositório

```
IF678-ChatCIn
│
├── 📁 Primeira Etapa
│ ├── 📁 files # Armazena os arquivos do cliente e servidor
│ ├── client.py # Código principal do cliente
│ ├── server.py # Código principal do servidor
│ └── readme.md
│
├── 📁 Segunda Etapa
│ ├── 📁 files # Armazena os arquivos do cliente e servidor
│ ├── client.py # Cliente utilizando RDT 3.0
│ ├── server.py # Servidor utilizando RDT 3.0
│ └── readme.md
│
├── 📁 Terceira Etapa
│ ├── 📁 rdt # Implementação do RDT 3.0
│ ├── cliente.py # Cliente do chat em grupo
│ ├── server.py # Servidor do chat em grupo
│ ├── main_test.py # Script de teste do chat
│ └── readme.md
│
├── .gitignore
└── README.md
```


## 👨‍💻 Desenvolvimento do Projeto
A implementação foi feita de forma colaborativa, onde cada membro participou de sessões de desenvolvimento sem uma divisão rígida de tarefas específicas.


## 🔥 Como Rodar o Projeto

1. Certifique-se de ter o Python instalado.
2. Abra o arquivo `server` do projeto correspondente e inicie o servidor:
   ```sh
   python server.py
   ```
3. Em outra instância do terminal, abra o arquivo `client` e execute o cliente:
   ```sh
   python client.py
   ```

## 🛠️ Tecnologias Utilizadas
- **Python**
- **UDP Sockets** (via `socket`)
- **RDT 3.0**

---

## Equipe:
- Alvaro Brandao Neto - abn2
- Ana Maria Cunha Ribeiro - amcr
- Ana Sofia da Silva Barbosa - assb
- Gabriel Valenca Mayerhofer - gvm
- Heitor Riquelme Melo de Souza - hrms2
