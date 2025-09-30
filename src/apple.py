import random
import pygame


class Apple:
    def __init__(self, board, grid_size):
        self.board = board
        self.grid_size = grid_size
        self.color = (255, 0, 0)  # Red apple
        self.position = (0, 0)  # Will be set by spawn method
        self.render_pending = True
        self.spawn(True)
    
    def spawn(self, init=False):
        """Respawn apple after it's been eaten"""

        if not init:
            # Clear old position in the board
            old_x, old_y = self.position
            self.board.squares_to_update.add(self.position)
            if 0 <= old_y < len(self.board.grid) and 0 <= old_x < len(self.board.grid[0]):
                # We set it as 1 and not 0 as if the apple has been eaten it means that there is a snake there
                self.board.grid.iloc[old_y, old_x] = 1

        # Find all empty spaces
        empty_spaces = []
        for y in range(self.board.height):
            for x in range(self.board.width):
                if self.board.grid.iloc[y, x] == 0:  # 0 = empty space
                    empty_spaces.append((x, y))

        # If there are no empty spaces, game should be over anyway
        if empty_spaces:
            self.position = random.choice(empty_spaces)
            x, y = self.position
            self.board.grid.iloc[y, x] = 2  # 2 represents apple

        self.render_pending = True

    def render(self, surface):
        """Draw the apple on the surface"""
        if not self.render_pending:
            return
        x, y = self.position

        # Draw the apple body
        apple_rect = pygame.Rect(
            (x+0.15) * self.grid_size,
            (y+0.3) * self.grid_size,
            self.grid_size*0.7,
            self.grid_size*0.7
        )
        pygame.draw.circle(surface, self.color, apple_rect.center, self.grid_size*0.7 // 2)

        y += 4/self.grid_size
        # Draw a small green stem
        stem_rect = pygame.Rect(
            x * self.grid_size + self.grid_size // 2 - 2,
            y * self.grid_size - 2,
            4,
            self.grid_size // 4
        )
        pygame.draw.rect(surface, (0, 100, 0), stem_rect)

        # Draw a small leaf
        leaf_points = [
            (x * self.grid_size + self.grid_size // 2, y * self.grid_size + 2),
            (x * self.grid_size + self.grid_size // 2 + 6, y * self.grid_size - 4),
            (x * self.grid_size + self.grid_size // 2 + 10, y * self.grid_size)
        ]
        pygame.draw.polygon(surface, (0, 180, 0), leaf_points)
