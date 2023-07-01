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

from rpyc.utils.server import ThreadedServer

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
    def __init__(self, id, inscricoes, status, anunciosRecebidos):
        self.id = id
        self.inscricoes = inscricoes
        self.status = status
        self.anunciosRecebidos = anunciosRecebidos

    def __str__(self):
        return f'Usuario(id={self.id}, inscricoes = {self.inscricoes}, status = {self.status}, anunciosRecebidos = {self.anunciosRecebidos})'


# usuariomock = Usuario("admin", ["Cavalo"], False, ["Cavalo: Cavalo 2.0 lançado"])
usuarios = []

# anuncios = {"cavalo": [{"autor": "admin", "topic": "cavalo", "data": "oiiiiiiii"}]}
anuncios = {}
connected_users = {}
global_callback = {}


class BrokerService(rpyc.Service):
    def __init__(self):
        self.callbacks = {}

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: Topic) -> Topic:
        anuncios[topicname] = None
        return topicname

    # Handshake
    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        if len(id) == 0 or id == 0:
            return False
        if id in connected_users.values():
            print("usuario já está logado")
            return False
        else:
            for usuario in usuarios:
                if usuario.id == id:
                    callback(usuario.anunciosRecebidos)
                    usuario.anunciosRecebidos = []
            connected_users[self.connection] = id
            usuario = Usuario(id, [], True, [])
            usuarios.append(usuario)
            return True

    def exposed_list_topics(self) -> list[Topic]:
        topics_titles = []

        for content in anuncios:
            topics_titles.append(content)

        return topics_titles

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        if topic in anuncios:
            self.publicaAnuncio(id, topic, data)
            anuncios[topic].append(Content(id, topic, data))
            print(anuncios)
            return True
        else:
            if id == "admin":
                self.create_topic(id, topic)
                self.publicaAnuncio(id, topic, data)
                print(anuncios)
                return True
        return False
        # Função responde se Anúncio conseguiu ser publicado

    def publicaAnuncio(self, id, topic, data):
        novoAnuncio = Content(id, topic, data)
        if anuncios[topic] is None:
            anuncios[topic] = [novoAnuncio]
        else:
            anuncios[topic].append(novoAnuncio)
        # Notificar todos os usuarios
        self.notificaUsuarios(novoAnuncio)

    def notificaUsuarios(self, content: Content):
        for usuario in usuarios:
            if content.topic in usuario.inscricoes:
                usuario.anunciosRecebidos.append(content)

                if usuario.id in connected_users.values():
                    print('global_callback')
                    print(len(global_callback))
                    print('self callback')
                    print(self.callbacks)
                    c = global_callback[usuario.id]
                    c(usuario.anunciosRecebidos)
                    usuario.anunciosRecebidos = []

        return

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in anuncios:
            for usuario in usuarios:
                if usuario.id == id:
                    usuario.inscricoes.append(topic)
                    print(usuario)
                    return True
        return False

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in anuncios:
            for usuario in usuarios:
                if usuario.id == id:
                    usuario.inscricoes.remove(topic)
                    print(usuario)
        return True

    def on_connect(self, conx):
        print("Conexao estabelecida.")
        self.connection = conx

    def on_disconnect(self, conx):
        # Implemente a lógica que deseja executar quando um cliente se desconectar
        print("Conexao encerrada.")
        del connected_users[conx]


brokerService = ThreadedServer(BrokerService, port=10000)
brokerService.start()
