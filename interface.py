from __future__ import annotations

# Se não funcionar no lab rode:
# $ pip install --user typing_extensions
import sys

IS_NEW_PYTHON: bool = sys.version_info > (3, 9)
if IS_NEW_PYTHON:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

# from rpyc.utils.server import ThreadedServer

import rpyc  # type: ignore

UserId: TypeAlias = str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
if IS_NEW_PYTHON:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Content:
        author: UserId
        topic: Topic
        data: str

elif not TYPE_CHECKING:
    @dataclass(frozen=True)
    class Content:
        author: UserId
        topic: Topic
        data: str

if IS_NEW_PYTHON:
    FnNotify: TypeAlias = Callable[[list[Content]], None]
elif not TYPE_CHECKING:
    FnNotify: TypeAlias = Callable


class Usuario:
    def __init__(self, id:UserId, inscricoes, status, anunciosRecebidos, callback:FnNotify):
        self.id = id
        self.inscricoes = inscricoes
        self.status = status
        self.anunciosRecebidos = anunciosRecebidos
        self.callback = callback

    def __str__(self):
        return f'Usuario(id={self.id}, inscricoes = {self.inscricoes}, status = {self.status}, anunciosRecebidos = {self.anunciosRecebidos})'


# usuariomock = Usuario("admin", ["Cavalo"], False, ["Cavalo: Cavalo 2.0 lançado"])
# usuarios = []

# anuncios = {"cavalo": [{"autor": "admin", "topic": "cavalo", "data": "oiiiiiiii"}]}
# anuncios = {}
# connected_users = {}

class BrokerService(rpyc.Service):
    anuncios = {}
    usuarios = []
    connected_users = {}

    print("Servidor iniciado com sucesso")

    def on_connect(self, conx):
        print("Conexao estabelecida.")
        self.current_connection = conx

    def on_disconnect(self, conx):
        print("Conexao encerrada.")
        del BrokerService.connected_users[conx]

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(topicname: Topic) -> Topic:
        BrokerService.anuncios[topicname] = None
        return topicname

    # Handshake
    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        if len(id) == 0 or id == 0:
            return False
        if id in BrokerService.connected_users.values():
            print("usuario já está logado")
            return False
        else:
            novo_usuario = True

            for usuario in BrokerService.usuarios:
                if usuario.id == id:
                    novo_usuario = False
                    usuario.callback = rpyc.async_(callback)
                    usuario.callback(usuario.anunciosRecebidos)
                    usuario.anunciosRecebidos = []
                    break

            if novo_usuario:
                usuario = Usuario(id, [], True, [], rpyc.async_(callback))
                BrokerService.usuarios.append(usuario)

            BrokerService.connected_users[self.current_connection] = id
            return True

    def exposed_list_topics(self) -> list[Topic]:
        topics_titles = []

        for content in BrokerService.anuncios:
            topics_titles.append(content)

        return topics_titles

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        if topic in BrokerService.anuncios:
            self.publicaAnuncio(id=id, topic=topic, data=data)
            return True
        return False

    def publicaAnuncio(self, id, topic, data):
        novoAnuncio = Content(id, topic, data)
        if BrokerService.anuncios[topic] is None:
            BrokerService.anuncios[topic] = [novoAnuncio]
        else:
            BrokerService.anuncios[topic].append(novoAnuncio)
        # Notificar todos os usuarios
        self.notificaUsuarios(novoAnuncio)

    def notificaUsuarios(self, content: Content):
        for usuario in BrokerService.usuarios:
            # print('usuario')
            # print(usuario)
            if content.topic in usuario.inscricoes:
                if usuario.id in BrokerService.connected_users.values():
                    usuario.callback([content])
                else:
                    usuario.anunciosRecebidos.append(content)
        return

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in BrokerService.anuncios.keys():
            for usuario in BrokerService.usuarios:
                if usuario.id == id:
                    if topic not in usuario.inscricoes:
                        usuario.inscricoes.append(topic)
                        if BrokerService.anuncios[topic]:
                            call = usuario.callback
                            call(BrokerService.anuncios[topic])
                        return True
                    break
        return False

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in BrokerService.anuncios:
            for usuario in BrokerService.usuarios:
                if usuario.id == id and topic in usuario.inscricoes:
                    usuario.inscricoes.remove(topic)
                    print(usuario)
        return True

# brokerService = ThreadedServer(BrokerService, port=10000, protocol_config={'allow_public_attrs': True})
# brokerService.start()
