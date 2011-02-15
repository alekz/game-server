#!/usr/bin/env python
from game.server import GameProtocol, GameFactory

port = 20000
interface = 'localhost'

factory = GameFactory()
from twisted.internet import reactor
port = reactor.listenTCP(port or 0, factory, interface=interface)
reactor.run()
