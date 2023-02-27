from __future__ import annotations
import os
import pickle
import pygame
import random
import datetime

pygame.init()

# region variables
FPS = 60
WIN_WIDTH = 800
WIN_HEIGHT = 1000
GAME_WIDTH = 800
GAME_HEIGHT = 800
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
LINE_WIDTH = 15
GRID_WIDTH = (GAME_WIDTH - 6 * LINE_WIDTH) / 5
GRID_HEIGHT = (GAME_HEIGHT - 6 * LINE_WIDTH) / 5

BACK_GROUND_COLOR = (242, 233, 228)
LINE_COLOR = (74, 78, 105)
CIRCLE_COLOR = (107, 171, 144)
CROSS_COLOR = (188, 44, 26)
UNDERLINE_COLOR = (74, 78, 105)
TEXT_COLOR = (163, 144, 228)
LAST_MOVE_COLOR = (235, 213, 201)
MENU_BUTTON_COLOR = (188, 44, 26)
MENU_BUTTON_HOVER_COLOR = (107, 171, 144)
HOME_BUTTON_COLOR = (235, 213, 201)
HOME_BUTTON_HOVER_COLOR = (74, 78, 105)
BUTTON_TEXT_COLOR = (235, 213, 201)
MENU_TITLE_COLOR = (0, 0, 0)

circle_image = pygame.transform.scale(pygame.image.load('circle.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7)).convert_alpha()
cross_image = pygame.transform.scale(pygame.image.load('cross.png'), (GRID_WIDTH * 0.7, GRID_HEIGHT * 0.7)).convert_alpha()
home_image = pygame.image.load('home_icon.png').convert_alpha()
loggo_image = pygame.transform.scale(pygame.image.load('logo.png'), (442, 172)).convert_alpha()

minimax_memory = dict()
save_memory = dict()
if os.path.exists("minimax_memory.pickle"):
    minimax_memory = pickle.load(open("minimax_memory.pickle", "rb"))
    save_memory = pickle.load(open("minimax_memory.pickle", "rb"))
# endregion variables

class Game():
    def __init__(self, grid: str = "0000000000000000000000000", turn: int = 1, circle_score: int = 0, cross_score: int = 0):
        self.grid = grid # 1->circle, 2->cross
        self.turn = turn # 1->circle, -1->cross
        self.circle_score = circle_score
        self.cross_score = cross_score
        self.last_move = None

    def draw(self):
        # draw line
        for i in range(6):
            x_coord = ((GAME_WIDTH - LINE_WIDTH) / 5) * i
            y_coord = ((GAME_WIDTH - LINE_WIDTH) / 5) * i
            pygame.draw.rect(WIN, LINE_COLOR, pygame.Rect((x_coord, 0 + WIN_HEIGHT - GAME_HEIGHT), (LINE_WIDTH, GAME_WIDTH)))
            pygame.draw.rect(WIN, LINE_COLOR, pygame.Rect((0, y_coord + WIN_HEIGHT - GAME_HEIGHT), (GAME_WIDTH, LINE_WIDTH)))
        
        # draw last move
        if self.last_move:
            pygame.draw.rect(WIN, LAST_MOVE_COLOR, pygame.Rect((self.last_move[1] * (GRID_WIDTH + LINE_WIDTH) + LINE_WIDTH, self.last_move[0] * (GRID_HEIGHT + LINE_WIDTH) + LINE_WIDTH + WIN_HEIGHT - GAME_HEIGHT), (GRID_WIDTH, GRID_HEIGHT)))

        # draw circle and cross
        for i, grid in enumerate(self.grid):
            row_idx = int(i / 5)
            col_idx = i % 5
            x_coord = (GRID_WIDTH + LINE_WIDTH) * col_idx + LINE_WIDTH + 0.15 * GRID_WIDTH
            y_coord = (GRID_WIDTH + LINE_WIDTH) * row_idx + LINE_WIDTH + WIN_HEIGHT - GAME_HEIGHT + 0.15 * GRID_HEIGHT
            if grid == "1":
                WIN.blit(circle_image, (x_coord, y_coord))
            elif grid == "2":
                WIN.blit(cross_image, (x_coord, y_coord))

    def calculate_score(self, new_row: int, new_col: int):
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

    def move(self, pos: tuple[float, float],):
        row = int((pos[1] - WIN_HEIGHT + GAME_HEIGHT) / (GRID_HEIGHT + LINE_WIDTH))
        col = int(pos[0] / (GRID_WIDTH + LINE_WIDTH))
        if row >= 0 and row < 5 and col >= 0 and col < 5:
            if self.grid[row * 5 + col] == "0":
                self.last_move = (row, col)
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

class UI():
    def __init__(self, game: Game, player_side: int):
        self.game = game
        self.player_side = player_side
        if os.path.exists("Tourney-SemiBold.ttf"):
            self.score_font = pygame.font.Font("Tourney-SemiBold.ttf", 70)
        else:
            self.score_font  = pygame.font.SysFont('arial', 70)
        if os.path.exists("Tourney-ExtraBold.ttf"):
            self.text_font = pygame.font.Font("Tourney-ExtraBold.ttf", 40)
        else:
            self.text_font  = pygame.font.SysFont('arial', 40)
        self.circle_text = self.score_font.render(f"circle", True, CIRCLE_COLOR)
        self.cross_text = self.score_font.render(f"cross", True, CROSS_COLOR)
        self.circle_score = self.score_font.render(f"{self.game.circle_score:02d}", True, CIRCLE_COLOR)
        self.cross_score = self.score_font.render(f"{self.game.cross_score:02d}", True, CROSS_COLOR)
        self.text = self.text_font.render("circle's turn", True, TEXT_COLOR)
    
    def darw(self):
        self.circle_text = self.score_font.render(f"circle", True, CIRCLE_COLOR)
        self.cross_text = self.score_font.render(f"cross", True, CROSS_COLOR)
        self.circle_score = self.score_font.render(f"{self.game.circle_score:02d}", True, CIRCLE_COLOR)
        self.cross_score = self.score_font.render(f"{self.game.cross_score:02d}", True, CROSS_COLOR)
        WIN.blit(self.circle_text, (70, 20))
        WIN.blit(self.cross_text, (510, 20))
        WIN.blit(self.circle_score, (70, 100))
        WIN.blit(self.cross_score, (640, 100))

        if self.game.turn == 1:
            self.text = self.text_font.render("circle's turn", True, TEXT_COLOR)
            WIN.blit(self.text, (270, 120))
        elif self.game.turn == -1:
            self.text = self.text_font.render("cross's turn", True, TEXT_COLOR)
            WIN.blit(self.text, (275, 120))
        elif self.game.turn == 0:
            if self.game.circle_score > self.game.cross_score:
                self.text = self.text_font.render("circle win", True, TEXT_COLOR)
                WIN.blit(self.text, (290, 120))
            elif self.game.circle_score < self.game.cross_score:
                self.text = self.text_font.render("cross win", True, TEXT_COLOR)
                WIN.blit(self.text, (295, 120))
            elif self.game.circle_score == self.game.cross_score:
                self.text = self.text_font.render("tie", True, TEXT_COLOR)
                WIN.blit(self.text, (365, 120))

        if self.player_side == 1:
            pygame.draw.line(WIN, UNDERLINE_COLOR, (65, 93), (310, 93), 3)
        elif self.player_side == 2:
            pygame.draw.line(WIN, UNDERLINE_COLOR, (505, 93), (725, 93), 3)

class AI():
    def __init__(self, play_circle_cross: int):
        self.play_circle_cross = play_circle_cross

    def move(self, game: Game) -> Game:
        ai_start_time = datetime.datetime.now()
        depths = 7
        max_eval = [-10000 for _ in range(depths)]
        best_moves = [[] for _ in range(depths)]
        best_move = (-1, -1)
        for idx, grid in enumerate(game.grid):
            if grid == "0":
                new_game: Game = game.copy()
                new_game.grid = new_game.grid[:idx] + ("1" if self.play_circle_cross == 1 else "2") + new_game.grid[idx+1:]
                new_game.turn *= -1
                new_game.calculate_score(idx // 5, idx % 5)
                for depth in range(depths):
                    eval = minimax(new_game, depth, -10000, 10000, False, self.play_circle_cross)
                    save_memory[(new_game.grid, new_game.turn, depth, False, self.play_circle_cross)] = eval
                    if eval > max_eval[depth]:
                        best_moves[depth] = [idx]
                        max_eval[depth] = eval
                    elif eval == max_eval[depth]:
                        best_moves[depth].append(idx)
        
        all_best_move = []
        best_move_appear_times = -100000
        for idx in range(25):
            appear_times = sum(i.count(idx) for i in best_moves)
            if appear_times > best_move_appear_times:
                all_best_move = [idx]
                best_move_appear_times = appear_times
            elif appear_times == best_move_appear_times:
                all_best_move.append(idx)
        
        best_move = random.choice(all_best_move)
        game.move(((best_move % 5) * (LINE_WIDTH + GRID_WIDTH) + GRID_WIDTH /2, (best_move // 5) * (LINE_WIDTH + GRID_HEIGHT) + GRID_HEIGHT /2 + WIN_HEIGHT - GAME_HEIGHT))
        print(f"ai think time: {datetime.datetime.now() - ai_start_time}")
        return game

def minimax(game: Game, depth: int, alpha: int, beta: int, maximizing_player: bool, play_circle_cross: int):
    # end case
    if depth == 0 or "0" not in game.grid:
        if play_circle_cross == 1:
            return game.circle_score - game.cross_score
        if play_circle_cross == 2:
            return game.cross_score - game.circle_score
    
    # search in memory
    if (game.grid, game.turn, depth, maximizing_player, play_circle_cross) in minimax_memory:
        return minimax_memory[(game.grid, game.turn, depth, maximizing_player, play_circle_cross)]

    # reecursion
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
        minimax_memory[(game.grid, game.turn, depth, maximizing_player, play_circle_cross)] = max_eval
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
        minimax_memory[(game.grid, game.turn, depth, maximizing_player, play_circle_cross)] = min_eval
        return min_eval

class Button():
    def __init__(self, text: str, rect: pygame.Rect, color: tuple[int, int, int], hover_color: tuple[int, int, int], image: pygame.Surface | None = None, border_radius: int = -1, border_top_left_radius: int = -1, border_top_right_radius: int = -1, border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1):
        self.text = text
        self.rect = rect
        self.color = color
        self.hover_color = hover_color
        if image != None:
            self.image = pygame.transform.scale(image, (self.rect.width, self.rect.height))
        else:
            self.image = image
        if os.path.exists("Tourney-SemiBold.ttf"):
            self.font = pygame.font.Font("Tourney-SemiBold.ttf", 55)
        else:
            self.font  = pygame.font.SysFont('arial', 55)
        self.hover = False
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius
    
    def draw(self):
        pygame.draw.rect(WIN, self.hover_color if self.hover else self.color, self.rect, border_radius = self.border_radius, border_top_left_radius = self.border_top_left_radius, border_top_right_radius = self.border_top_right_radius, border_bottom_left_radius = self.border_bottom_left_radius, border_bottom_right_radius = self.border_bottom_right_radius)
        WIN.blit(self.font.render(self.text, True, BUTTON_TEXT_COLOR), (self.rect.x + 20, self.rect.y + 15))
        if self.image != None:
            WIN.blit(self.image, self.rect)
    
    def clicked(self, pos) -> bool:
        if self.rect.collidepoint(pos):
            return True
        return False
    
    def hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.hover = True
        else:
            self.hover = False

class Menu():
    def __init__(self):
        if os.path.exists("Tourney-SemiBold.ttf"):
            self.font = pygame.font.Font("Tourney-SemiBold.ttf", 120)
        else:
            self.font  = pygame.font.SysFont('arial', 120)
        self.title = loggo_image
        self.button_pvp = Button("Player vs. Player", pygame.Rect(135, 385, 535, 90), MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR, None, -1, 30, 10, 10, 30)
        self.button_pve = Button("Player vs.     AI", pygame.Rect(135, 555, 535, 90), MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR, None, -1, 30, 10, 10, 30)
        self.button_eve = Button("    AI      vs.     AI", pygame.Rect(135, 725, 535, 90), MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR, None, -1, 30, 10, 10, 30)
    
    def draw(self):
        WIN.fill(BACK_GROUND_COLOR)
        WIN.blit(self.title, (195, 110))
        self.button_pvp.draw()
        self.button_pve.draw()
        self.button_eve.draw()

    def check_hover(self, pos):
        self.button_pvp.hovered(pos)
        self.button_pve.hovered(pos)
        self.button_eve.hovered(pos)
    
    def select_mode(self, pos) -> int | None:
        if self.button_pvp.clicked(pos):
            return 2
        if self.button_pve.clicked(pos):
            return 1
        if self.button_eve.clicked(pos):
            return 0

def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        state = "menu"
        menu = Menu()
        game_mode = None # 0->ai1 vs. ai2, 1->player vs. ai1, 2->player vs. player
        if state == "menu":
            menu.check_hover(pygame.mouse.get_pos())
            menu.draw()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game_mode = menu.select_mode(event.pos)
                    print(game_mode)
                    if game_mode != None:
                        state = "game"
        
        if state == "game":
            game_run = True
            game = Game()
            ai1 = AI(random.choice([1, 2]))
            ai2 = AI(1 if ai1.play_circle_cross == 2 else 2)
            ui = UI(game, 1 if ai1.play_circle_cross == 2 else 2)
            home_button = Button("", pygame.Rect(367, 25, 66, 66), HOME_BUTTON_COLOR, HOME_BUTTON_HOVER_COLOR, home_image, 5)

            while game_run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_run = False
                        run = False
                    # player move
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if game_mode == 1:
                            if (game.turn == -1 and ai1.play_circle_cross == 1) or (game.turn == 1 and ai1.play_circle_cross == 2):
                                game.move(event.pos)
                        if game_mode == 2:
                            game.move(event.pos)
                        if game.turn == 0 and home_button.clicked(event.pos):
                            game_run = False

                WIN.fill(BACK_GROUND_COLOR)
                
                game.draw()
                ui.darw()
                if game.turn == 0:
                    home_button.hovered(pygame.mouse.get_pos())
                    home_button.draw()
                pygame.display.update()

                if game.turn != 0:
                    ai2_can_move = True
                    # ai1 move
                    if game_mode != 2 and ((game.turn == 1 and ai1.play_circle_cross == 1) or (game.turn == -1 and ai1.play_circle_cross == 2)):
                        game = ai1.move(game)
                        ai2_can_move = False
                    
                    # ai2 move
                    if ai2_can_move and game_mode == 0 and ((game.turn == 1 and ai2.play_circle_cross == 1) or (game.turn == -1 and ai2.play_circle_cross == 2)):
                        game = ai2.move(game)

                    game.draw()
                    clock.tick(FPS)
                    pygame.display.update()

            # save minimax_memory
            pickle.dump(save_memory, open("minimax_memory.pickle", "wb"))
            state = "menu"
        
        clock.tick(FPS)

if __name__ == '__main__':
    main()