class GameError(Exception):
    pass

class Game(object):

    def __init__(self):
        self._game_started = False
        self._board = None
        self._current_player = None
        self.startGame()

    def _resetBoard(self):
        row = [None] * 3
        self._board = [row[:], row[:], row[:]]

    def _setCell(self, x, y, value):
        x, y = int(x), int(y)
        if (x < 1) or (3 < x):
            raise ValueError("X must be between 1 and 3, got {0} instead".format(x))
        if (y < 1) or (3 < y):
            raise ValueError("Y must be between 1 and 3, got {0} instead".format(y))
        if value not in ('X', 'O'):
            raise ValueError('Cell value must be whether "{0}" or "{1}"'.format('X', 'O'))
        if self._board[x - 1][y - 1] is not None:
            raise ValueError("Cell is not empty")

        self._board[x - 1][y - 1] = value

    def makeMove(self, x, y):
        """Make the move and switch to the next player."""

        if not self._game_started:
            raise GameError("Can't make a move: game is not started")

        self._setCell(x, y, self._current_player)

        if self._current_player == 'X':
            self._current_player = 'O'
        else:
            self._current_player = 'X'

    def startGame(self):
        """Start a new game"""

        self._resetBoard()
        self._current_player = 'X'
        self._game_started = True

    def isFinished(self):
        return False  # TODO: Implement Game.isFinished()

    def getBoard(self):
        return self._board
    board = property(getBoard)

class GameStrategy(object):

    def getMove(self, game):
        raise NotImplementedError

    def makeMove(self, game):
        cell = self.getMove(game)
        if cell:
            game.makeMove(*cell)
        return cell

class RandomGameStrategy(GameStrategy):

    def getMove(self, game):
        import random
        free_cells = [(x + 1, y + 1) for x, row in enumerate(game.board)
                             for y, cell in enumerate(row)
                             if cell is None]
        if free_cells:
            return random.choice(free_cells)
        else:
            return None
