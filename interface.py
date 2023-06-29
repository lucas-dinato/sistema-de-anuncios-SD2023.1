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


usuarios = []

usuariomock = Usuario("123", ["Cavalo"], False, ["Cavalo: Cavalo 2.0 lançado"])
usuarios.append(usuariomock)

# anuncios = {"123": [{"topic": "cavalo", "autor": "admin", "mensagem": "oi oi oi oi"}]}
anuncios = {}
# inscritos = {"Cavalo": ["123"]}
inscritos = {}
connected_users = {}


# connected_users = {}

class BrokerService(rpyc.Service):  # type: ignore

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: Topic) -> Topic:
        if id == "admin":
            anuncios[topicname] = None
            return topicname
        assert False, "TO BE IMPLEMENTED"

    # Handshake

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        if len(id) == 0:
            return False
        if id in connected_users.values():
            return False
        else:
            for usuario in usuarios:
                if usuario.id == id:
                    callback(usuario.anunciosRecebidos)
        connected_users[self.connection] = id
        usuario = Usuario(id, [], True, [])
        usuarios.append(usuario)
        return True
        # for usuario in usuarios:
        #     if usuario.id == id:
        #         if usuario.status:
        #             return False
        #         else:
        #             callback(usuario.anunciosRecebidos)
        #             usuario.status = True
        #             return True

        # usuario = Usuario(id, [], True)
        # usuarios.append(usuario)

        # return True

    # Query operations

    def exposed_list_topics(self) -> list[Topic]:
        topics_titles = []

        for content in anuncios:
            topics_titles.append(content)

        return topics_titles

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        if topic in anuncios:
            anuncios[topic].append(Content(id, topic, data))
            return True
        else:
            if id == "admin":
                self.create_topic(id, topic)
                anuncios[topic].append(Content(id, topic, data))
                return True
        return False
        """
        Função responde se Anúncio conseguiu ser publicado
        assert False, "TO BE IMPLEMENTED"
        """

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in anuncios:
            for usuario in usuarios:
                if usuario.id == id:
                    usuario.inscricoes.append(topic)
                    return True
        return False
        """
        Função responde se `id` está inscrito no `topic`
       
        assert False, "TO BE IMPLEMENTED"
         """

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        if topic in anuncios:
            for usuario in usuarios:
                if usuario.id == id:
                    usuario.inscricoes.remove(topic)
                    return True
        # ToDo Checar boolean retornado
        return False
        """
        Função responde se `id` não está inscrito no `topic`
        assert False, "TO BE IMPLEMENTED"
        """

    def on_connect(self, conx):
        print("Conexao estabelecida.")
        self.connection = conx

    def on_disconnect(self, conx):
        # Implemente a lógica que deseja executar quando um cliente se desconectar
        print("Conexao encerrada.")
        del connected_users[conx]


brokerService = ThreadedServer(BrokerService, port=10000)
brokerService.start()
