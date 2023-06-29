import rpyc

global_id = 0


def exposed_get_id():
    return global_id


def callback(contents):
    print("\nConteúdos:")
    for content in contents:
        print(f"{content}\n")
    return


def login():
    id = input("Digite seu identificador: ")
    retorno = system.root.login(id, callback)
    if retorno:
        global_id = id
        print("Login realizado com sucesso.")
    else:
        print("Login inválido.")
        login()


system = rpyc.connect('localhost', 10000)
login()
print("\n")

while True:
    func = input("Digite uma funcionalidade (list, publish, subscribe, unsubscribe ou 'fim' para terminar): ")
    if func == 'fim':
        system.close()
        break

    if func == 'list':
        topics = system.root.list_topics()
        print(topics)
    elif func == 'publish':
        anuncio = system.root.publish()
        print(anuncio)
    elif func == 'subscribe':
        topic = system.root.subscribe_to()
        print(topic)
    elif func == 'unsubscribe':
        topic = system.root.unsubscribe_to()
        print(topic)
