import random
from twisted.python import log
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.protocol import ServerFactory
from twisted.application.service import Service

class GameError(Exception):
    pass

class GameProtocol(NetstringReceiver):

    def __init__(self):
        self.game_started = False
        self.board = None
        self.remote_player = None
        self.current_player = None

    def connectionMade(self):
        peer = self.transport.getPeer()
        log.msg('Connection made from {0}:{1}'.format(peer.host, peer.port))

    def stringReceived(self, line):
        """Decodes and runs a command from the received data"""
        log.msg('Data received: {0}'.format(line))
        args = line.split(',')
        if not args:
            self.sendError("Empty command")
            return
        command, args = args[0], args[1:]
        self.runCommand(command, *args)

    def sendError(self, message):
        self.sendResponse('error', message)

    def sendResponse(self, command, *args):
        string = ','.join([command] + [str(arg) for arg in args])
        self.sendString(string)
        log.msg('Data sent: {0}'.format(string))

    #def connectionLost(self, reason=connectionDone):
    #    log.msg('Connection lost')

    def runCommand(self, command, *args):
        """
        Executes a command.

        Possible commands:

        - start[,<x_or_o>] - (re)start game
                             x_or_o ("x", "X", "o" or "O") - which side the player chooses
                             can be empty, in this case sides will be assigned randomly

        - move,<x>,<y> - make move to a cell with coords x, y
                         x (1..3) - Column number
                         y (1..3) - Row number
        """
        commands = {
                    'start': self.startGame,
                    'move': self.makeMove,
                    }
        if not commands.has_key(command):
            self.sendError('Invalid command: "{0}"'.format(command))
            return
        try:
            commands[command](*args)
        except (ValueError, GameError), e:
            self.sendError('Error executing command "{0}": {1}'.format(command, e))

    def _resetBoard(self):
        row = (None,) * 3
        self.board = (row[:], row[:], row[:])

    def _setCell(self, x, y, value):

        if x < 1 or 3 < x:
            raise ValueError("X must be between 1 and 3")
        if y < 1 or 3 < y:
            raise ValueError("Y must be between 1 and 3")
        if value not in ('X', 'O'):
            raise ValueError('Cell value must be whether "{0}" or "{1}"'.format('X', 'O'))
        if self.board[x - 1][y - 1] is not None:
            raise ValueError("Cell is not empty")

        self.board[x - 1][y - 1] = value

    def makeMove(self, x, y):
        """Make the move and switch to the next player."""

        if not self.game_started:
            raise GameError("Can't make a move: game is not started")

        self._setCell(x, y, self.current_player)

        if self.current_player == 'X':
            self.current_player = 'O'
        else:
            self.current_player = 'X'

    def startGame(self, side=None):
        """Start a new game"""

        if side is None:
            side = random.choice(('X', 'O'))
        elif side.upper() not in ('X', 'O'):
            raise ValueError('Invalid side: "{0}"', side)

        self._resetBoard()
        self.remote_player = side.upper()
        self.current_player = 'X'
        self.game_started = True

class GameFactory(ServerFactory):

    protocol = GameProtocol

    def __init__(self, service):
        self.service = service

class GameService(Service):
    pass
