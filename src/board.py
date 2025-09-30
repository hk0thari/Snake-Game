import pygame
from src.config import board_bg_color, board_grid_color, board_border_color
import pandas as pd


class Board:
    def __init__(self, width, height, grid_size, start_x=0, start_y=0):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.square_num = self.width * self.height

        # Create 2D grid to track game state
        # 0 = empty, 1 = snake, 2 = apple
        grid = [[0 for _ in range(width)] for _ in range(height)]
        self.grid = pd.DataFrame(grid)

        self.squares_to_update = set()

    def render(self, surface, init=False):
        """Draw the game board on the surface"""

        if init:
            # Draw background
            surface.fill(board_bg_color)

            # Draw grid lines
            for x in range(0, (self.width+1) * self.grid_size, self.grid_size):
                pygame.draw.line(surface, board_grid_color, (x, 0), (x, self.height * self.grid_size))

            for y in range(0, (self.height+1) * self.grid_size, self.grid_size):
                pygame.draw.line(surface, board_grid_color, (0, y), (self.width * self.grid_size, y))

        else:
            for x, y in self.squares_to_update:
                rect = pygame.Rect(x * self.grid_size, y * self.grid_size, self.grid_size+1, self.grid_size+1)
                pygame.draw.rect(surface, board_bg_color, rect)
                pygame.draw.rect(surface, board_grid_color, rect, 1)
            self.squares_to_update = set()

        self.render_border(surface)

    def render_border(self, surface):

        # Draw border
        border_rect = pygame.Rect(0, 0, self.width * self.grid_size + 4, self.height * self.grid_size + 4)
        pygame.draw.rect(surface, board_border_color, border_rect, 3)  # 3px border width
