import rpyc

system = rpyc.connect('localhost', 10000)

while True:
    op = input("Digite uma funcionalidade (login, list, publish, subscribe, unsubscribe ou 'fim' para terminar): ")
    if op == 'fim':
        system.close()
        break

    if op == 'login':
        div = system.root.login()
        print(div)
    elif op == 'list':
        div = system.root.list_topics()
        print(div)
    elif op == 'publish':
        div = system.root.publish()
        print(div)
    elif op == 'subscribe':
        div = system.root.subscribe_to()
        print(div)
    elif op == 'unsubscribe':
        div = system.root.unsubscribe_to()
        print(div)
