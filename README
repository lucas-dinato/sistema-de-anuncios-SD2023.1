# Aplicação Distribuída de um Sistema de Anúncios

O objetivo deste trabalho é projetar uma aplicação distribuída de `anúncios` para aplicar os conceitos estudados até aqui.

Uma aplicação de anúncios é uma aplicação distribuída que permite que usuários publiquem, registrem interesse e recebam notificações de anúncios.  

## Alunos

João Victor de Miranda Gadelha
Lenise Maria de Vasconcelos Rodrigues
Lucas Vieira Dinato

## Descrição dos requisitos gerais da aplicação

Um usuário poderá:
1. criar e publicar anúncios;
2. registrar interesse em anúncios e ser notificado quando eles ocorrerem, mesmo que não esteja ativo ao mesmo tempo;
3. cancelar o registro de interesse em anúncios e não receber novas notificações;
   

## Descrição da arquitetura de software da aplicação

Estilo arquitetural publish-subscribe.
Os anúncios serão identificados por **tópicos**, contendo um conjunto de atributos. 
Os componentes principais da aplicação são: 
1. **componente que publica anúncio** (cria um anúncio e o envia para o gerente de anúncios)
2. **componente que registra interesse em anúncio** (registra interesse em um anúncio no gerente de anúncios e recebe notificação de anúncio)
3. **componente de barramento ou gerente de anúncios** (informa lista de tópicos de anúncios, cria um novo tópico (permitida apenas para o administrador), recebe anúncio para publicação, recebe subscrição de interesse, notifica componente que registrou interesse, armazena os anúncios até sua expiração)

### Especificações: 
* **Registro de subscriber**: Login **não** permite mais de um usuário com o mesmo login;
* **Atributos de anúncio**: tópico, autor, string com o conteúdo do anúncio;
* **Forma de entrega**: Notifica já enviando o conteúdo;
* **Persistência e entrega a posteriori**: Se um subscriber não estiver conectado, os anúncios são armazenados em memória, de forma que, na próxima conexão, recebe todos os anúncios anteriores.


## Descrição da arquitetura de sistema da aplicação

Foi escolhida pela turma a arquitetura cliente-servidor:
- Os componentes de publicação e registro de interesse ficarão do lado cliente
- O componente gerente de anúncios ficará do lado servidor
- Há **um único servidor** capaz de atender **múltiplos clientes**

## Descrição do protocolo de camada de aplicação

Faz-se uso de camada de middleware RPC, de forma que para o contexto da solução, foi escolhido o uso do módulo [RPyC](https://rpyc.readthedocs.io/en/latest/) para possibilitar tal implementação.


## Principais decisões tomadas na implementação
* O armazenamento das estruturas de dados utilizados nesta implementação foram feitos na memória (em oposição a salvar esses dados em arquivos, por exemplo) do próprio servidor. Essa escolha foi feita pois,como consultado em aula, pudemos presumir que a conexão do servidor não seria interrompida durante os testes.
* O cargo de criação de tópicos foi, a princípio, delegado para um cliente que possuísse o id de `admin`, através da execução do `publish` de um `anúncio` em um `tópico` que não existia anteriormente (o servidor, ao verificar que este tópico não existia, o criaria, e geraria tal anúncio ); 
  * Para respeitar os acordos em sala, entretanto, fizemos uma alteração para contemplar a possibilidade de uma interface de administração. Para viabilizar isso fizemos uma implementação baseada em thread, de forma que há uma thread que chama uma função que inicia o servidor e a thread principal continua disponível e rodando com o menu de administração. 
* Para controlarmos o status de um usuário (se o usuário se encontra online ou não, o que interfere o que será feito na hora de notificação de publicações), optamos por uma espécie de "logout" efetuado ao nos desconectarmos do servidor (ou seja, ao digitarmos `fim` no terminal do cliente); o que resulta em apenas um único login por conexão do cliente
* Um último item em que nos demos liberdade artística foi o de, deliberadamente, não notificar o autor de um anúncio que estivesse inscrito nesse tópico. 


## Interface com o usuário
Ao inicializar o programa `cliente.py`, a pessoa usuária se depara com a funcionalidade de login, que é necessária para "começarmos os trabalhos".
Após realizar o login, o usuário entrará em um "menu" de funcionalidades, tendo como opções:
* `list`
  * Função que serve para listar os `tópicos` de anúncio disponíveis no servidor 
* `publish`
  * Função para publicar um anúncio no servidor; 
  * Para isso, o usuário deve entrar com o `tópico` desse anúncio, e depois seu conteúdo
* `subscribe`
  * Função que visa inscrever o usuário em certo `tópico`
  * Para isso, após o comando, deve-se entrar com o `tópico` em que deseja se inscrever
* `unsubscribe`
  * Função que desinscreve o usuário de devido `tópico` 
  * Após entrar com esta opção, é necessária a introdução do `tópico` em questão 
* `fim`
      * Função para encerrar a conexão deste usuário com o servidor

## Interface com o admin
Ao inicializar o programa `admin_interface.py`, a pessoa usuária se depara com o menu de administração, que é necessária para gerenciar o servidor.
* `criar`
  * Função que serve para criar um tópico e é utilizada **APENAS** por essa interface de administração
  * Após entrar com essa opção, é necessário introduzir um `tópico` a ser criado 
* `fim`
  * Função para encerrar o servidor
