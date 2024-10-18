import pygame
import random
import numpy as np


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

GRID_SIZE = 25

PLAY_FIELD_GRID_WIDTH = 15
PLAY_FIELD_GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE - 2

PF_X_POS = round((SCREEN_WIDTH - PLAY_FIELD_GRID_WIDTH * GRID_SIZE) / 2)
PF_Y_POS = round((SCREEN_HEIGHT - PLAY_FIELD_GRID_HEIGHT * GRID_SIZE) / 2)

colors = [
    (205, 26, 26),
    (233, 128, 22),
    (243, 250, 28),
    (35, 137, 14),
    (26, 246, 209),
    (26, 33, 246),
    (129, 26, 246),
]
colors_dict = {i+2: color for i, color in enumerate(colors)}  # reserve 1 for black

shapes = [
    [(0, 1), (1, 1), (1, 0), (2, 0)],  # S-shape
    [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-shape
    [(0, 0), (0, 1), (0, 2), (1, 2)],  # L-shape
    [(0, 2), (1, 2), (1, 1), (1, 0)],  # J-shape
    [(0, 1), (1, 1), (1, 0), (0, 0)],  # O-shape
    [(0, 0), (0, 1), (0, 2), (0, 3)],  # I-shape
    [(0, 1), (1, 1), (2, 1), (1, 2)],  # T-shape
]

ccw_rotation_matrix = np.array([[0, -1], [1, 0]])
cw_rotation_matrix = np.array([[0, 1], [-1, 0]])

all_scores = []


class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color_ind = random.randint(2, len(colors)+1)
        self.color = colors_dict[self.color_ind]
        self.points = shapes[random.randint(0, len(shapes)-1)]


class Tetris:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.shape: Figure | None = None
        self.next_shape = None
        self.score = 0
        self.game_over = False
        self.new_shape()
        self.level = 1

    def new_shape(self):
        if not self.next_shape:
            self.shape = self._new_shape()
        else:
            self.shape = self.next_shape
        self.next_shape = self._new_shape()
        if not self.is_valid_vertical_move():
            self.game_over = True

    def _new_shape(self):
        return Figure(self.width // 2, 1)

    def draw_grid(self, screen):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell != 1:
                    cell = colors_dict[cell]

                pygame.draw.rect(screen, cell, (x * GRID_SIZE + PF_X_POS, y * GRID_SIZE + PF_Y_POS,
                                                    GRID_SIZE - 1, GRID_SIZE - 1))

    def draw_shape(self, screen):
        for x, y in self.shape.points:
            pygame.draw.rect(screen, self.shape.color, ((x+self.shape.x) * GRID_SIZE + PF_X_POS,
                                                        (y+self.shape.y) * GRID_SIZE + PF_Y_POS,
                                                        GRID_SIZE - 1, GRID_SIZE - 1))

    def freeze_shape(self):
        for x_, y_ in self.shape.points:
            x = x_ + self.shape.x
            y = y_ + self.shape.y
            self.grid[y][x] = self.shape.color_ind

    def move(self, key):
        potential_x = self.shape.x
        if key in [pygame.K_LEFT, pygame.K_a]:
            potential_x = self.shape.x - 1
        if key in [pygame.K_RIGHT, pygame.K_d]:
            potential_x = self.shape.x + 1
        if key in [pygame.K_DOWN, pygame.K_s]:
            self.move_down()

        if self.is_valid_horizontal_move(potential_x):
            self.shape.x = potential_x

    def move_down(self):
        if self.is_valid_vertical_move():
            self.shape.y += 1
        else:
            self.freeze_shape()
            if not self.game_over:
                self.new_shape()

    def is_valid_horizontal_move(self, potential_x):
        left = min(self.shape.points, key=lambda x: x[0])[0]
        right = max(self.shape.points, key=lambda x: x[0])[0]
        if potential_x + left < 0:
            return False
        if potential_x + right >= self.width:
            return False

        for x_, y_ in self.shape.points:
            x = x_ + potential_x
            y = y_ + self.shape.y
            if x-1 >= 0 and self.grid[y][x-1] != 1:
                return False
            if x+1 < self.width and self.grid[y][x+1] != 1:
                return False
        return True

    def is_valid_vertical_move(self):
        bottom_y = max(self.shape.points, key=lambda x: x[1])[1]
        if self.shape.y + bottom_y + 1 >= self.height:
            return False

        for x_, y_ in self.shape.points:
            x = x_ + self.shape.x
            y = y_ + self.shape.y+1

            if self.grid[y][x] != 1:
                return False
        return True

    def check_and_remove_full_row(self):
        as_numpy = np.array(self.grid)
        full_rows = np.where(np.all(as_numpy != 1, axis=1))[0]
        diff = np.diff(full_rows)
        bonus = len(np.where(diff == 1)[0])
        score = len(full_rows) * self.level + bonus
        self.score += score
        rows_with_ones = as_numpy[np.any(as_numpy == 1, axis=1)]
        missing_rows = np.ones((len(full_rows), self.width))
        update_grid = np.concatenate((missing_rows, rows_with_ones), axis=0)
        update_grid = update_grid.astype(int).tolist()
        self.grid = update_grid

    def rotate(self, clockwise=True):
        original_shape = self.shape.points
        shape = np.array(self.shape.points)
        center = shape.mean(axis=0)
        centered_points = shape - center
        if clockwise:
            rotated = centered_points @ cw_rotation_matrix
        else:
            rotated = centered_points @ ccw_rotation_matrix
        rotated += center
        self.shape.points = np.floor(rotated).astype(int).tolist()
        if not self.is_valid_horizontal_move(self.shape.x):
            self.shape.points = original_shape

    def draw_game_over_screen(self, screen, font):
        screen.fill((0, 153, 153))
        rect = pygame.Rect((50, 140, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 350))
        pygame.draw.rect(screen, "black", rect)
        pygame.draw.rect(screen, "red", rect, 2)

        over = font.render('Game Over', True, "white")
        score_msg = font.render(f'This Game Score: {self.score}', True, "red")
        max_msg = font.render(f'Max Game Score: {max(all_scores)}', True, "red")
        level_msg = font.render(f'Level: {self.level}', True, "red")
        new_game = font.render('Press R to start new game', True, "red")

        screen.blit(over, (rect.centerx - over.get_width() / 2, rect.y + 20))
        screen.blit(level_msg, (rect.centerx - level_msg.get_width() / 2, rect.y + 80))
        screen.blit(score_msg, (rect.centerx - score_msg.get_width() / 2, rect.y + 110))
        screen.blit(max_msg, (rect.centerx - max_msg.get_width() / 2, rect.y + 140))
        screen.blit(new_game, (rect.centerx - new_game.get_width() / 2, rect.y + 170))

    def draw_next_shape(self, screen):
        for x, y in self.next_shape.points:
            pygame.draw.rect(screen, self.next_shape.color,
                             (x * GRID_SIZE + SCREEN_WIDTH-PF_X_POS + 50,
                              y * GRID_SIZE + SCREEN_HEIGHT // 2-50,
                              GRID_SIZE - 1, GRID_SIZE - 1))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    font = pygame.font.SysFont('cursive', 50)

    LEVEL_UP = pygame.USEREVENT + 1
    pygame.time.set_timer(LEVEL_UP, 15000)

    game = Tetris(PLAY_FIELD_GRID_WIDTH, PLAY_FIELD_GRID_HEIGHT)
    level_up_threshold = 700
    last_move_time = pygame.time.get_ticks()

    while running:
        screen.fill((0, 153, 153))

        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > level_up_threshold:
            game.move_down()
            last_move_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    all_scores.append(game.score)
                    game = Tetris(PLAY_FIELD_GRID_WIDTH, PLAY_FIELD_GRID_HEIGHT)
                game.move(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.rotate(clockwise=False)
                else:
                    game.rotate()
            elif event.type == LEVEL_UP and level_up_threshold > 100:
                level_up_threshold -= 100
                game.level += 1

        game.draw_grid(screen)
        game.draw_shape(screen)
        game.draw_next_shape(screen)
        game.check_and_remove_full_row()

        score = font.render(f'SCORE: {game.score}', True, "white")
        screen.blit(score, (250 - score.get_width() // 2, SCREEN_HEIGHT - 210))

        level = font.render(f'LEVEL: {game.level}', True, "white")
        screen.blit(level, (250 - score.get_width() // 2, SCREEN_HEIGHT - 110))

        if game.game_over:
            game.draw_game_over_screen(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()