from __future__ import annotations
import pygame
import random
import pickle
import os

pygame.init()

FPS = 60
WIN_WIDTH = 800
WIN_HEIGHT = 900
GAME_WIDTH = 800
GAME_HEIGHT = 800
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
LINE_WIDTH = 15
GRID_WIDTH = (GAME_WIDTH - 6 * LINE_WIDTH) / 5
GRID_HEIGHT = (GAME_HEIGHT - 6 * LINE_WIDTH) / 5

BACK_GROUND_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
SCORE_COLOR = (0, 0, 0)
TURN_COLOR = (255, 0, 0)

circle_image = pygame.transform.scale(pygame.image.load('circle.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7))
cross_image = pygame.transform.scale(pygame.image.load('cross.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7))

memory = dict()
if os.path.isfile("memory.pickle"):
    with open('memory.pickle', 'rb') as f:
        memory = pickle.load(f)

class Game():
    def __init__(self, grid = "0000000000000000000000000", turn = 1, circle_score = 0, cross_score = 0):
        self.grid = grid # 1->circle, 2->cross
        self.turn = turn # 1->circle, -1->cross
        self.circle_score = circle_score
        self.cross_score = cross_score

    def draw(self):
        # draw line
        for i in range(6):
            x_coord = ((GAME_WIDTH - LINE_WIDTH) / 5) * i
            y_coord = ((GAME_WIDTH - LINE_WIDTH) / 5) * i
            pygame.draw.rect(WIN, LINE_COLOR, pygame.Rect((x_coord, 0 + WIN_HEIGHT - GAME_HEIGHT), (LINE_WIDTH, GAME_WIDTH)))
            pygame.draw.rect(WIN, LINE_COLOR, pygame.Rect((0, y_coord + WIN_HEIGHT - GAME_HEIGHT), (GAME_WIDTH, LINE_WIDTH)))
        
        for i, grid in enumerate(self.grid):
            row_idx = int(i / 5)
            col_idx = i % 5
            x_coord = (GRID_WIDTH + LINE_WIDTH) * col_idx + LINE_WIDTH + 0.15 * GRID_WIDTH
            y_coord = (GRID_WIDTH + LINE_WIDTH) * row_idx + LINE_WIDTH + WIN_HEIGHT - GAME_HEIGHT + 0.15 * GRID_HEIGHT
            if grid == "1":
                WIN.blit(circle_image, (x_coord, y_coord))
            elif grid == "2":
                WIN.blit(cross_image, (x_coord, y_coord))

        font = pygame.font.SysFont('arial', 70)
        WIN.blit(font.render(f"circle:{self.circle_score}", True, TURN_COLOR if self.turn == 1 else SCORE_COLOR), (150, 10))
        WIN.blit(font.render(f"cross:{self.cross_score}", True, TURN_COLOR if self.turn == -1 else SCORE_COLOR), (460, 10))

    def calculate_score(self, new_row, new_col):
        if self.grid in memory:
            self.circle = memory[self.grid][0]
            self.cross = memory[self.grid][1]
        new = self.grid[new_row * 5 + new_col] 
        # right-top diagonal
        if new_row + new_col != 0 and new_row + new_col != 8:
            start = (max(0, new_row + new_col - 4), new_row + new_col - max(0, new_row + new_col - 4))
            score = 0
            while start[0] < 5 and start[1] >= 0:
                if self.grid[start[0] * 5 + start[1]] != new:
                    score = 0
                    break
                else:
                    score += 1
                    start = (start[0] + 1, start[1] - 1)
            if self.turn == 1:
                self.circle_score += score
            elif self.turn == -1:
                self.cross_score += score
        
        # left-top diagonal
        if new_row - new_col != 4 and new_row - new_col != -4:
            if new_row - new_col >= 0:
                start = (new_row - new_col, 0)
            else:
                start = (0, new_col - new_row)

            score = 0
            while start[0] < 5 and start[1] < 5:
                if self.grid[start[0] * 5 + start[1]] != new:
                    score = 0
                    break
                else:
                    score += 1
                    start = (start[0] + 1, start[1] + 1)
            if self.turn == 1:
                self.circle_score += score
            elif self.turn == -1:
                self.cross_score += score

        # vertical
        line = True
        for row in range(5):
            if self.grid[row * 5 + new_col] != new:
                line = False
                break
        if line:
            if self.turn == 1:
                self.circle_score += 5
            elif self.turn == -1:
                self.cross_score += 5

        # horizontal
        line = True
        for col in range(5):
            if self.grid[new_row * 5 + col] != new:
                line = False
                break
        if line:
            if self.turn == 1:
                self.circle_score += 5
            elif self.turn == -1:
                self.cross_score += 5

        # four grid
        top_left, top, top_right, right, down_right, down, down_left, left = False, False, False, False, False, False, False, False
        if new_row - 1 >= 0:
            if new_col - 1 >= 0:
                if self.grid[new_row * 5 + new_col - 6] == new:
                    top_left = True
            if self.grid[new_row * 5 + new_col - 5] == new:
                    top = True
            if new_col + 1 < 5:
                if self.grid[new_row * 5 + new_col - 4] == new:
                    top_right = True
        if new_row + 1 < 5:
            if new_col - 1 >= 0:
                if self.grid[new_row * 5 + new_col + 4] == new:
                    down_left = True
            if self.grid[new_row * 5 + new_col + 5] == new:
                    down = True
            if new_col + 1 < 5:
                if self.grid[new_row * 5 + new_col + 6] == new:
                    down_right = True
        if new_col - 1 >= 0:
            if self.grid[new_row * 5 + new_col - 1] == new:
                left = True
        if new_col + 1 < 5:
            if self.grid[new_row * 5 + new_col + 1] == new:
                right = True
        score = 0
        if top_left and top and left:
            score += 1
        if top_right and top and right:
            score += 1
        if down_left and down and left:
            score += 1
        if down_right and down and right:
            score += 1
        if self.turn == 1:
            self.circle_score += score
        elif self.turn == -1:
            self.cross_score += score
        memory[self.grid] = (self.circle_score, self.cross_score)

    def move(self, pos: tuple[float, float],):
        row = int((pos[1] - WIN_HEIGHT + GAME_HEIGHT) / (GRID_HEIGHT + LINE_WIDTH))
        col = int(pos[0] / (GRID_WIDTH + LINE_WIDTH))
        if self.grid[row * 5 + col] == "0":
            if self.turn == 1:
                self.grid = self.grid[:row * 5 + col] + "1" + self.grid[row * 5 + col + 1:]
                self.calculate_score(row, col)
            elif self.turn == -1:
                self.grid = self.grid[:row * 5 + col] + "2" + self.grid[row * 5 + col + 1:]
                self.calculate_score(row, col)
            self.turn *= -1
        
        if "0" not in self.grid:
            self.turn = 0
    
    def reset(self):
        self.grid = "0000000000000000000000000" # 1->circle, 2->cross
        self.turn = 1 # 1->circle, -1->cross
        self.circle_score = 0
        self.cross_score = 0

    def copy(self) ->  Game:
        return Game(self.grid, self.turn, self.circle_score, self.cross_score)

def minimax(game: Game, depth: int, alpha: int, beta: int, maximizing_player: bool, play_circle_cross: int):
    if depth == 0 or "0" not in game.grid:
        if play_circle_cross == 1:
            return game.circle_score - game.cross_score
        if play_circle_cross == 2:
            return game.cross_score - game.circle_score
        
    if maximizing_player:
        max_eval = -10000
        for idx, grid in enumerate(game.grid):
            if grid == "0":
                new_game: Game = game.copy()
                new_game.grid = new_game.grid[:idx] + ("1" if new_game.turn == 1 else "2") + new_game.grid[idx+1:]
                new_game.calculate_score(idx // 5, idx % 5)
                new_game.turn *= -1
                eval = minimax(new_game, depth - 1, alpha, beta, False, play_circle_cross)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = 10000
        for idx, grid in enumerate(game.grid):
            if grid == "0":
                new_game: Game = game.copy()
                new_game.grid = new_game.grid[:idx] + ("1" if new_game.turn == 1 else "2") + new_game.grid[idx+1:]
                new_game.calculate_score(idx // 5, idx % 5)
                new_game.turn *= -1
                eval = minimax(new_game, depth - 1, alpha, beta, True, play_circle_cross)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game()
    ai = random.choice([1, 2])
    saved = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.move(event.pos)

        WIN.fill(BACK_GROUND_COLOR)
        
        game.draw()
        pygame.display.update()

        if (game.turn == 1 and ai == 1) or (game.turn == -1 and ai == 2):
            depths = 7
            max_eval = [-10000 for _ in range(depths)]
            best_moves = [[] for _ in range(depths)]
            best_move = (-1, -1)
            for idx, grid in enumerate(game.grid):
                if grid == "0":
                    new_game: Game = game.copy()
                    new_game.grid = new_game.grid[:idx] + ("1" if ai == 1 else "2") + new_game.grid[idx+1:]
                    new_game.turn *= -1
                    new_game.calculate_score(idx // 5, idx % 5)
                    for depth in range(depths):
                        eval = minimax(new_game, depth, -10000, 10000, False, ai)
                        if eval > max_eval[depth]:
                            best_moves[depth] = [idx]
                            max_eval[depth] = eval
                        elif eval == max_eval[depth]:
                            best_moves[depth].append(idx)
            for idx in range(25):
                best_move = max(best_move, (sum(i.count(idx) for i in best_moves), idx), key = lambda x : x[0])
            # best_move = random.choice(best_moves)
            best_move = best_move[1]
            game.move(((best_move % 5) * (LINE_WIDTH + GRID_WIDTH) + GRID_WIDTH /2, (best_move // 5) * (LINE_WIDTH + GRID_HEIGHT) + GRID_HEIGHT /2 + WIN_HEIGHT - GAME_HEIGHT))


        game.draw()
        clock.tick(FPS)
        pygame.display.update()

        if game.turn == 0 and not saved:
            saved = True
            with open('memory.pickle', 'wb') as f:
                pickle.dump(memory, f, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()