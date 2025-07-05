# Primeira Etapa
Está é a primeira etapa do projeto de Infraestrutura de Computação, onde implementamos uma comunicação cliente-servidor usando o protocolo UDP. O cliente envia um arquivo para o servidor, que o salva e envia de volta com um nome modificado.

# Instruções de Uso

- O servidor e o cliente devem ser executados em terminais separados. A ordem de execução não importa, mas o servidor deve estar ativo antes do cliente tentar enviar um arquivo, caso contrário, o cliente não conseguirá enviar o arquivo e irá dar um aviso de timeout.
- O cliente envia o nome do arquivo para o servidor, que o salva e envia de volta com um nome modificado. Os arquivos disponíveis para envio devem estar na pasta `files`. O servidor salva o arquivo na pasta `server` e o cliente salva na pasta `client`.
  - Os arquivos disponíveis são: `image1.jpeg` e `enviar.txt`. No entanto, qualquer arquivo pode que esteja na pasta `files` será listado como opção de envio.
- Arquivos são enviados em blocos de 1024 bytes. O final do envio é sinalizado com a mensagem "END".

# Equipe:
- Alvaro Brandao Neto - abn2
- Ana Maria Cunha Ribeiro - amcr
- Ana Sofia da Silva Barbosa - assb
- Gabriel Valenca Mayerhofer - gvm
- Heitor Riquelme Melo de Souza - hrms2