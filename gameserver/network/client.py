#!/usr/bin/env python
import optparse
from twisted.protocols import basic
from twisted.internet import protocol, stdio
from gameserver.network.protocol import JsonReceiver
from gameserver.game import Game

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
        print "Connected!\n"
        self.printHelp()
        self.printBoard()

    def userInputReceived(self, string):
        """
        Supported commands:
        - start
        - move <x> <y>
        """
        commands = {
                    'start': self.sendStartGame,
                    '?': self.printHelp,
                    'h': self.printHelp,
                    'help': self.printHelp,
                    'p': self.printBoard,
                    'print': self.printBoard,
                    'm': self.sendMakeMove,
                    'move': self.sendMakeMove,
                    'q': self.exitGame,
                    'quit': self.exitGame,
                    'exit': self.exitGame,
                    }

        params = filter(len, string.split(' '))
        command, params = params[0], params[1:]

        if not command:
            return

        if command not in commands:
            print "Invalid command"
            return

        try:
            commands[command](*params)
        except TypeError, e:
            print "Invalid command parameters: {0}".format(e)

    def printHelp(self):
        print "Available commands:"
        print "  ?, h, help          - Print list of commands"
        print "  p, print            - Print the board"
        print "  m, move <row> <col> - Make a move to a cell located in given row/column"
        print "                        \"row\" and \"col\" should be values between 1 and 3"
        print "  q, quit, exit       - Exit the program"
        print

    def exitGame(self):
        print "Disconnecting..."
        self.transport.loseConnection()

    def sendCommand(self, command, **params):
        self.sendObject(command=command, params=params)

    def sendStartGame(self):
        self.sendCommand('start')

    def sendMakeMove(self, row, col):
        self.sendCommand('move', x=col, y=row)

    def objectReceived(self, obj):
        print "Data received: {0}".format(obj)
        if obj.has_key('command'):
            command = obj['command']
            params = obj.get('params', {})
            self.receiveCommand(command, **params)

    def invalidJsonReceived(self, data):
        print "Invalid JSON data received: {0}".format(data)

    def receiveCommand(self, command, **params):

        commands = {
                    'error': self.serverError,
                    'move': self.serverMove,
                    'started': self.serverStarted,
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

    def serverStarted(self, side):
        print "Game started, you're playing with {0}".format(side)

    def printBoard(self):
        board = [[cell or ' ' for cell in col] for col in self.game.board]
        lines = [
                 "     1   2   3",
                 "   +---+---+---+",
                 " 1 | {0[0]} | {1[0]} | {2[0]} |",
                 "   +---+---+---+",
                 " 2 | {0[1]} | {1[1]} | {2[1]} |",
                 "   +---+---+---+",
                 " 3 | {0[2]} | {1[2]} | {2[2]} |",
                 "   +---+---+---+",
                 "",
                 ]
        print "\n".join(lines).format(*board)

class GameClientFactory(protocol.ClientFactory):
    protocol = GameClientProtocol

    def startedConnecting(self, connector):
        destination = connector.getDestination()
        print "Connecting to server {0}:{1}, please wait...".format(destination.host, destination.port)

    def clientConnectionFailed(self, connector, reason):
        print reason.getErrorMessage()
        from twisted.internet import reactor
        reactor.stop()  #@UndefinedVariable

    def clientConnectionLost(self, connector, reason):
        print reason.getErrorMessage()
        from twisted.internet import reactor, error
        try:
            reactor.stop()  #@UndefinedVariable
        except error.ReactorNotRunning:
            pass

def parse_args():
    usage = "usage: %prog [options] [[hostname:]port]"

    parser = optparse.OptionParser(usage)

    _, args = parser.parse_args()

    if not args:
        address = "127.0.0.1:20000"
    else:
        address = args[0]

    if ':' not in address:
        host, port = '127.0.0.1', address
    else:
        host, port = address.split(':', 1)

    if not port.isdigit():
        parser.error("Ports must be integers.")

    return host, int(port)

def run_client():
    from twisted.internet import reactor
    host, port = parse_args()
    factory = GameClientFactory()
    reactor.connectTCP(host, port, factory)  #@UndefinedVariable
    reactor.run()  #@UndefinedVariable

if __name__ == '__main__':
    run_client()
