import random
from collections import deque
from twisted.python import log
from twisted.internet import protocol
from twisted.application import service
from gameserver.network.protocol import JsonReceiver
from gameserver.game import Game, GameError

class GameProtocol(JsonReceiver):

    STATE_AWAITING_OPPONENT = 1
    STATE_MAKING_MOVE = 2
    STATE_AWAITING_MOVE = 3
    STATE_FINISHED = 4

    def __init__(self):
        self.state = GameProtocol.STATE_AWAITING_OPPONENT
        self.game = None
        self.opponent = None

    def connectionMade(self):
        peer = self.transport.getPeer()
        log.msg("Connection made from {0}:{1}".format(peer.host, peer.port))
        self.sendResponse('awaiting_opponent')

        # Find an opponent or add self to a queue
        self.factory.findOpponent(self)

    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        log.msg("Connection lost from {0}:{1}".format(peer.host, peer.port))
        self.factory.playerDisconnected(self)

    def objectReceived(self, data):
        """Decodes and runs a command from the received data"""

        log.msg('Data received: {0}'.format(data))

        if not data.has_key('command'):
            self.sendError("Empty command")
            return

        command = data['command']
        params = data.get('params', {})

        self.runCommand(command, **params)

    def invalidJsonReceived(self, data):
        log.msg("Invalid JSON data received:\n" + data)
        self.sendError("Invalid JSON data")

    def sendError(self, message):
        self.sendResponse('error', message=message)

    def sendResponse(self, command, **params):
        self.sendObject(command=command, params=params)
        log.msg("Data sent: {0}({1})".format(command, params))

    def runCommand(self, command, **params):
        """
        Executes a command.

        Possible commands:

        - move(x=<x>, y=<y>) - make move to a cell with coords x, y
            x (1..3) - Column number
            y (1..3) - Row number
        """

        commands = {
                    'move': self.runMakeMoveCommand,
                    }

        if not commands.has_key(command):
            self.sendError("Invalid command: \"{0}\"".format(command))
            return

        try:
            commands[command](**params)
        except (ValueError, TypeError, GameError), e:
            self.sendError("Error executing command \"{0}\": {1}".format(command, e))

    def startGame(self, game, opponent, side):
        self.game = game
        self.opponent = opponent
        if side == 'X':
            self.state = GameProtocol.STATE_MAKING_MOVE
        else:
            self.state = GameProtocol.STATE_AWAITING_MOVE
        self.sendResponse('started', side=side)

    def runMakeMoveCommand(self, x, y):
        if self.state == GameProtocol.STATE_MAKING_MOVE:
            self.game.makeMove(x, y)
            self._moveMade(x, y, GameProtocol.STATE_AWAITING_MOVE)
            self.opponent.makeMoveFromOpponent(x, y)
        else:
            self.sendError("Can't make a move right now")

    def makeMoveFromOpponent(self, x, y):
        if self.state == GameProtocol.STATE_AWAITING_MOVE:
            self._moveMade(x, y, GameProtocol.STATE_MAKING_MOVE)
        else:
            # TODO: Handle "Unexpected move from opponent" situation somehow
            raise Exception("Opponent sent us a move but we weren't expecting that")

    def _moveMade(self, x, y, new_state):
            self.sendResponse('move', x=x, y=y, winner=self.game.getWinner())
            if self.game.isFinished():
                self.state = GameProtocol.STATE_FINISHED
            else:
                self.state = new_state

class GameFactory(protocol.ServerFactory):

    protocol = GameProtocol
    queue = deque()

    def __init__(self, service):
        self.service = service

    def findOpponent(self, player):
        try:
            opponent = self.queue.popleft()
        except IndexError:
            self.queue.append(player)
        else:
            game = Game()
            side1, side2 = random.choice([('O', 'X'), ('X', 'O')])
            player.startGame(game, opponent, side1)
            opponent.startGame(game, player, side2)

    def playerDisconnected(self, player):
        try:
            self.queue.remove(player)
        except ValueError:
            pass

class GameService(service.Service):
    pass
