import curses
import random
import time

# Shapes represented as rotations of 4x4 matrices
SHAPES = {
    'I': [
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,1,0,0]],
    ],
    'O': [
        [[0,0,0,0],
         [0,1,1,0],
         [0,1,1,0],
         [0,0,0,0]],
    ],
    'T': [
        [[0,0,0,0],
         [1,1,1,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [1,1,0,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,1,0],
         [0,1,0,0],
         [0,0,0,0]],
    ],
    'L': [
        [[0,0,0,0],
         [1,1,1,0],
         [1,0,0,0],
         [0,0,0,0]],
        [[1,1,0,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,0,0,0]],
        [[0,0,1,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [0,1,1,0],
         [0,0,0,0]],
    ],
    'J': [
        [[0,0,0,0],
         [1,1,1,0],
         [0,0,1,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [1,1,0,0],
         [0,0,0,0]],
        [[1,0,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,1,1,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,0,0,0]],
    ],
    'S': [
        [[0,0,0,0],
         [0,1,1,0],
         [1,1,0,0],
         [0,0,0,0]],
        [[1,0,0,0],
         [1,1,0,0],
         [0,1,0,0],
         [0,0,0,0]],
    ],
    'Z': [
        [[0,0,0,0],
         [1,1,0,0],
         [0,1,1,0],
         [0,0,0,0]],
        [[0,1,0,0],
         [1,1,0,0],
         [1,0,0,0],
         [0,0,0,0]],
    ],
}

COLORS = {
    'I': 1,
    'O': 2,
    'T': 3,
    'L': 4,
    'J': 5,
    'S': 6,
    'Z': 7,
}

HEIGHT = 20
WIDTH = 10

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rot = 0
        self.x = WIDTH // 2 - 2
        self.y = 0

    @property
    def matrix(self):
        return SHAPES[self.shape][self.rot % len(SHAPES[self.shape])]

    def rotate(self):
        self.rot = (self.rot + 1) % len(SHAPES[self.shape])


def create_board():
    return [[0]*WIDTH for _ in range(HEIGHT)]


def fits(board, piece, dx=0, dy=0, rot=None):
    rot = piece.rot if rot is None else rot
    matrix = SHAPES[piece.shape][rot % len(SHAPES[piece.shape])]
    for y in range(4):
        for x in range(4):
            if matrix[y][x]:
                nx = piece.x + x + dx
                ny = piece.y + y + dy
                if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
                    return False
                if board[ny][nx]:
                    return False
    return True


def place_piece(board, piece):
    for y in range(4):
        for x in range(4):
            if piece.matrix[y][x]:
                board[piece.y+y][piece.x+x] = COLORS[piece.shape]


def clear_lines(board):
    new_board = [row for row in board if any(v == 0 for v in row)]
    lines_cleared = HEIGHT - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [0]*WIDTH)
    return new_board, lines_cleared


def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            val = board[y][x]
            char = '[]' if val else '  '
            if val:
                stdscr.addstr(y, x*2, char, curses.color_pair(val))
            else:
                stdscr.addstr(y, x*2, char)
    for y in range(4):
        for x in range(4):
            if piece.matrix[y][x]:
                px = piece.x + x
                py = piece.y + y
                if 0 <= py < HEIGHT:
                    stdscr.addstr(py, px*2, '[]', curses.color_pair(COLORS[piece.shape]))
    stdscr.addstr(0, WIDTH*2 + 2, f'Score: {score}')
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    for i in range(1,8):
        curses.init_pair(i, i, 0)
    board = create_board()
    current = Piece(random.choice(list(SHAPES.keys())))
    next_drop = time.time() + 0.5
    score = 0
    while True:
        draw_board(stdscr, board, current, score)
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_LEFT and fits(board, current, dx=-1):
            current.x -= 1
        elif key == curses.KEY_RIGHT and fits(board, current, dx=1):
            current.x += 1
        elif key == curses.KEY_DOWN and fits(board, current, dy=1):
            current.y += 1
        elif key == curses.KEY_UP:
            if fits(board, current, rot=(current.rot+1)):
                current.rotate()
        if time.time() >= next_drop:
            if fits(board, current, dy=1):
                current.y += 1
            else:
                place_piece(board, current)
                board, cleared = clear_lines(board)
                score += cleared
                current = Piece(random.choice(list(SHAPES.keys())))
                if not fits(board, current):
                    draw_board(stdscr, board, current, score)
                    stdscr.addstr(HEIGHT//2, WIDTH, 'GAME OVER')
                    stdscr.refresh()
                    stdscr.getch()
                    break
            next_drop = time.time() + 0.5
        time.sleep(0.02)

if __name__ == '__main__':
    curses.wrapper(main)
