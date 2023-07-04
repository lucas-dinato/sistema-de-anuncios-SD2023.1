import rpyc

global_id = 0


def exposed_get_id():
    return global_id


def callback(contents):
    if len(contents):
        print("\nNotificações:")
    for content in contents:
        print(f'Autor:{content.author}\nTópico:{content.topic}\nMensagem:{content.data}')

def login():
    global global_id
    id = input("Digite seu identificador: ")
    retorno = system.root.login(id, callback)
    if retorno:
        global_id = id
        print("Login realizado com sucesso.")
    else:
        print("Login inválido.")
        login()


system = rpyc.connect('localhost', 10000)
bg = rpyc.BgServingThread(system)
login()
print("\n")

while True:
    func = input("Digite uma funcionalidade (list, publish, subscribe, unsubscribe ou 'fim' para terminar): ")
    if func == 'fim':
        bg.stop()
        system.close()
        break
    elif func == 'list':
        topics = system.root.list_topics()
        print(topics)
    elif func == 'publish':
        topico = input("Entre com o tópico do anúncio: ")
        data = input("Agora entre com o conteúdo do anúncio: ")
        anuncio = system.root.publish(global_id, topico, data)
        if anuncio:
            print("Anuncio do tópico " + topico + " publicado com sucesso!")
        else:
            print("Tivemos problema ao publicar o seu anúncio! ")
    elif func == 'subscribe':
        topico = input("Entre com o tópico em que você quer se inscrever:  ")
        topic = system.root.subscribe_to(global_id, topico)
        if topic:
            print("Inscrição no tópico " + topico + " realizada com sucesso!")
        else:
            print("Falha ao se inscrever no tópico " + topico + ".")
    elif func == 'unsubscribe':
        topico = input("Entre com o tópico em que você quer se desinscrever:  ")
        topic = system.root.unsubscribe_to(global_id, topico)
        if topic:
            print("Inscrição cancelada no tópico " + topico + " .")
        else:
            print("Falha ao se desinscrever no tópico " + topico + ".")
    else:
        print(" Comando inválido, por favor entre com um comando de list, publish, subscribe, unsubscribe ou fim!")
