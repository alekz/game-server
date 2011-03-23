class GameError(Exception):
    pass

class Game(object):

    def __init__(self):
        # "Board" is a 3x3 array of arrays, each value is whether 'X', 'O' or None
        self._board = None
        # Current player: 'X' or 'O'
        self._current_player = None
        self._game_started = False
        self.startGame()

    def startGame(self):
        """Start a new game"""
        self._resetBoard()
        self._current_player = 'X'
        self._game_started = True

    def _resetBoard(self):
        """Clear the board (reset all cells to None)"""
        row = [None] * 3
        self._board = [row[:], row[:], row[:]]

    def getCell(self, x, y):
        """Returns value of the cell with given coordinates: 'X', 'O' or None"""
        x, y = int(x), int(y)
        self._checkCoords(x, y)
        return self._board[x - 1][y - 1]

    def getBoard(self):
        return self._board
    board = property(getBoard)

    def getCurrentPlayer(self):
        return self._current_player
    current_player = property(getCurrentPlayer)

    def _setCell(self, x, y, value):
        x, y = int(x), int(y)
        self._checkCoords(x, y)
        if value not in ('X', 'O'):
            raise ValueError('Cell value must be whether "{0}" or "{1}"'.format('X', 'O'))
        if self._board[x - 1][y - 1] is not None:
            raise ValueError("Cell is not empty")

        self._board[x - 1][y - 1] = value

    def _checkCoords(self, x, y):
        if (x < 1) or (3 < x):
            raise ValueError("X must be between 1 and 3, got {0} instead".format(x))
        if (y < 1) or (3 < y):
            raise ValueError("Y must be between 1 and 3, got {0} instead".format(y))

    def makeMove(self, x, y):
        """Make a move and switch to the next player"""

        if not self.isStarted():
            raise GameError("Can't make a move: game is not started")

        if self.isFinished():
            raise GameError("Can't make a move: game is finished")

        self._setCell(x, y, self._current_player)

        if self._current_player == 'X':
            self._current_player = 'O'
        else:
            self._current_player = 'X'

    def getWinner(self):
        """Returns 'X', 'O' or None (if game is not finished yet)"""

        lines = []

        # Rows and cols
        for i in (1, 2, 3):
            lines.append([self.getCell(x, i) for x in (1, 2, 3)])
            lines.append([self.getCell(i, y) for y in (1, 2, 3)])

        # Diagonals
        lines.append([self.getCell(i, i) for i in (1, 2, 3)])
        lines.append([self.getCell(4 - i, i) for i in (1, 2, 3)])

        # Check each line
        for line in lines:
            if (line[0] == line[1] == line[2]) and (line[0] is not None):
                return line[0]

        return None

    def isStarted(self):
        return self._game_started

    def isFinished(self):
        return self.getWinner() is not None

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
        free_cells = [(x, y)
                      for x in (1, 2, 3)
                      for y in (1, 2, 3)
                      if game.getCell(x, y) is None]
        if free_cells:
            return random.choice(free_cells)
        else:
            return None
