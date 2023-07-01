import threading
from rpyc.utils.server import ThreadedServer
from interface import BrokerService
def menu():
    print("comandos disponíveis para o servidor:\n"
          "criar -- comando para criar um tópico\n"
          "fim -- comando para encerrar o servidor\n"
          "Por favor, informe um comando dentre os listados acima")

s = None
def initServer():
    global s
    s = ThreadedServer(BrokerService(), port=10000, protocol_config={'allow_public_attrs': True})
    s.start()
def closeServer():
    global s
    s.close()

if __name__ == '__main__':
    menu()
    thread = threading.Thread(target=initServer)
    thread.start()
    while True:
        print()
        ipt = input()
        if ipt == "criar":
            topic = input("Insira o nome do topico que deseja criar\n")
            t = s.service.create_topic(id="", topicname=topic)
            if t:
                print("Tópico criado com sucesso")
        elif ipt == 'fim':
            break
        else:
            print("Comando inválido. Favor verificar o menu...")
    closeServer()
    thread.join()
    print("Servidor encerrado com sucesso")


