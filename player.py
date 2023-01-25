from board import Direction, Rotation, Shape, Block
from random import Random


# metrics

def heights(board):
    for x in range(board.width):
        r = 0

        for y in range(board.height):
            if (x, y) in board.cells: r += 1

        yield r


def aheight(board):
    return sum(heights(board))


def mheight(board):
    return max(heights(board))


def var(board):
    v = 0
    h = list(heights(board))

    for y1, y2 in zip(h[:-1], h[1:]):
        v += abs(y1 - y2)

    return v


def holes(board):
    n = 0

    for x in range(board.width):
        roof = 0
        for y in range(board.height):
            cell = (x, y) in board.cells

            if cell:
                roof = 1

            elif roof and not cell:
                n += 1

    return n


def ncells(board):
    return len(board.cells)


def dlines(board, clone):
    dscore = clone.score - board.score

    if dscore >= 100: return 1
    if dscore >= 400: return 2
    if dscore >= 800: return 3
    if dscore >= 1600: return 4
    return 0


def stable(board):
    h = [*heights(board)]
    return h[0] + h[-1]


class Player:
    def choose_action(self, board):
        raise NotImplementedError


def rule1(board):
    hs = list(heights(board))

    for x in range(board.width):
        for y in range(board.height):
            if (x, y) in board: continue
            if x >= board.width - 2: continue

            right_col_height = hs[x + 1]
            hole_height = board.height - y

            if right_col_height >= hole_height:
                yield (x, y)

                
def rule2(board):
    for x in range(board.width):
        roof = 0
        for y in range(board.height):
            cell = (x, y) in board.cells

            if cell:
                roof = 1

            elif roof and not cell:
                yield (x, y)

                
def rule3(board):
    hs = list(heights(board))

    for x in range(1, board.width):
        for y in range(board.height):
            if (x, y) in board: continue

            left_col_height = hs[x - 1]
            hole_height = board.height - y

            if left_col_height >= hole_height:
                yield (x, y)

                
def gaps(board):
    cells = list(rule1(board)) + list(rule3(board))
    s = 0

    for (x, y) in cells:
        s += (board.height - y)**2

    for (x, y) in rule2(board):
        s += (board.height - y)**3

    return s


class autoplayer:
    def __init__(self):
        self.lines = 0

    def moveTo(self, x, rot, clone):
        moves = [Rotation('CLOCKWISE')] * rot
        dx = x - clone.falling.left
        moves += [Direction('LEFT' if dx < 0 else 'RIGHT')] * abs(dx)
        moves.append(Direction('DROP'))

        while 1:
            move = moves.pop(0)
            yield move


            if (clone.move(move) if type(move) is Direction else clone.rotate(move)):
                return

    def rate(self, board, clone):
        m = mheight(clone)

        if m < 17:
            return .57 * ncells(clone) - aheight(clone) - 200 * holes(clone) - 8 * var(clone) + 4 * stable(clone)

        return 10 * dlines(board, clone) - gaps(clone) - aheight(clone)

    def bestMove(self, board):
        best = None
        bestRating = None

        for x in range(board.width):
            for rot in range(4):
                clone = board.clone()
                moves = [*self.moveTo(x, rot, clone)]
                rating = self.rate(board, clone)

                if (bestRating is None) or (rating > bestRating):
                    best = moves
                    bestRating = rating

        return best

    def choose_action(self, board):
        return self.bestMove(board)


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        return self.random.choice([
            Direction.Left,
            Direction.Right,
            Direction.Down,
            Rotation.Anticlockwise,
            Rotation.Clockwise,
        ])


SelectedPlayer = autoplayer
