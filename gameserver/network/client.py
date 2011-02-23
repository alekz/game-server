#!/usr/bin/env python
import optparse
from twisted.protocols import basic
from twisted.internet import protocol, stdio
from gameserver.network.protocol import JsonReceiver
from gameserver.game import Game, GameError

class UserInputProtocol(basic.LineReceiver):

    from os import linesep as delimiter  #@UnusedImport

    def __init__(self, callback):
        self.callback = callback

    def lineReceived(self, line):
        self.callback(line)

class GameClientProtocol(JsonReceiver):

    def __init__(self):
        self.game = Game()

    def connectionMade(self):
        stdio.StandardIO(UserInputProtocol(self.userInputReceived))

    def userInputReceived(self, string):
        """
        Supported commands:
        - start
        - move <x> <y>
        """
        commands = {
                    'start': self.sendStartGame,
                    'move': self.sendMakeMove,
                    }

        params = string.split(' ')
        command, params = params[0], params[1:]

        if command not in commands:
            print "Invalid command"
            return

        try:
            commands[command](*params)
        except TypeError, e:
            print "Invalid command parameters: {0}".format(e)

    def sendCommand(self, command, **params):
        self.sendObject(command=command, params=params)

    def sendStartGame(self):
        self.sendCommand('start')

    def sendMakeMove(self, x, y):
        self.sendCommand('move', x=x, y=y)

    def objectReceived(self, obj):
        print "Data received: {0}".format(obj)
        if obj.has_key('command'):
            command = obj['command']
            params = obj.get('params', {})
            self.receiveCommand(command, **params)

    def receiveCommand(self, command, **params):

        commands = {
                    'error': self.serverError,
                    'move': self.serverMove,
                    }

        if command not in commands:
            print "Invalid command received: {0}".format(command)
            return

        try:
            commands[command](**params)
        except TypeError, e:
            print "Invalid command parameters received: {0}".format(e)

    def serverError(self, message):
        print "Server error: {0}".format(message)

    def serverMove(self, x, y):
        self.game.makeMove(x, y)
        self.printBoard()

    def printBoard(self):
        board = [[cell or ' ' for cell in col] for col in self.game.board]
        lines = [
                 " {0[0]} | {1[0]} | {2[0]} ",
                 "---+---+---",
                 " {0[1]} | {1[1]} | {2[1]} ",
                 "---+---+---",
                 " {0[2]} | {1[2]} | {2[2]} ",
                 ]
        print "\n".join(lines).format(*board)

class GameClientFactory(protocol.ClientFactory):
    protocol = GameClientProtocol

def parse_args():
    usage = "usage: %prog [options] [hostname]:port"

    parser = optparse.OptionParser(usage)

    _, args = parser.parse_args()

    if not args:
        print parser.format_help()
        parser.exit()

    address = args[0]

    if ':' not in address:
        host, port = '127.0.0.1', address
    else:
        host, port = address.split(':', 1)

    if not port.isdigit():
        parser.error('Ports must be integers.')

    return host, int(port)

def run_client():
    from twisted.internet import reactor
    host, port = parse_args()
    factory = GameClientFactory()
    reactor.connectTCP(host, port, factory)  #@UndefinedVariable
    reactor.run()  #@UndefinedVariable

if __name__ == '__main__':
    run_client()
