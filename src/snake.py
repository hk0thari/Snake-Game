from src.config import *


class Snake:
    def __init__(self, x, y, grid_size, board, speed):
        # Initialize snake segments (head is at index 0)
        self.segments = [(x, y)]
        self.grid_size = grid_size
        self.board = board

        self.direction = (1, 0)  # Start moving right
        self.changed_direction_this_frame = False
        self.direction_change_pending = []

        self.head_color = LIGHT_GREEN
        self.color = LIME_GREEN
        self.growth_pending = 0  # Number of segments to grow

        # Set initial position in board
        self.board.grid.iloc[y, x] = 1  # 1 represents snake

        # This is used to optimise rendering
        # Only those squares are re-rendered which have been updated this frame
        self.segments_to_update = {(x, y)}

        self.SPEED = speed
        self.snake_update_timer = 60 // self.SPEED  # Updates once every 6 frames

        self.rules = rules

        self.score = 0
        self.score_updated_this_frame = True  # If this is true then we re-render the score in main.py
        self.TIME_BONUS = round((self.board.square_num ** 0.5) * 0.4, 1)
        self.time_bonus_factor = 0.9/self.board.square_num
        self.time_bonus = min(self.score*self.time_bonus_factor, self.TIME_BONUS)

    def change_direction(self, dx, dy):
        """Change the direction of the snake"""
        if not self.changed_direction_this_frame:
            if self.direction == (dx, dy):
                return
            self.direction = (dx, dy)
            self.changed_direction_this_frame = True

            # Play turn sound
            turn.play()
        elif len(self.direction_change_pending) < 3:
            self.direction_change_pending.append((dx, dy))

    def grow(self):
        """Make the snake longer by one segment"""
        self.growth_pending += 1

    def check_collision_with_apple(self, apple, head_x, head_y):
        """Check if snake's head collides with the apple"""
        apple_x, apple_y = apple.position

        return head_x == apple_x and head_y == apple_y

    def handle_event(self, event):
        # Handle direction change events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.change_direction(0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.change_direction(0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.change_direction(-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.change_direction(1, 0)

    def update(self, apple):
        """Move the snake based on its current direction
        Returns True if game over, False otherwise"""

        if self.snake_update_timer:
            self.snake_update_timer -= 1
            return "game"

        self.snake_update_timer = 60 // self.SPEED

        self.segments_to_update = set()
        respawn = False
        # Get current head position
        head_x, head_y = self.segments[0]

        if len(self.segments) > 1:
            self.segments_to_update.add((head_x, head_y))

        # Calculate new head position
        dx, dy = self.direction
        new_head_x = head_x + dx
        new_head_y = head_y + dy

        # Check if snake hits the wall
        if (new_head_x < 0 or new_head_x >= self.board.width or
                new_head_y < 0 or new_head_y >= self.board.height):
            if self.rules["on_wall_collision"] == "E":
                # Play collision sound
                collision.play()
                return "game_over"  # Game over

            elif self.rules["on_wall_collision"] == "T":
                if new_head_x < 0:
                    new_head_x = self.board.width - 1
                if new_head_x >= self.board.width:
                    new_head_x = 0
                if new_head_y < 0:
                    new_head_y = self.board.height - 1
                if new_head_y >= self.board.height:
                    new_head_y = 0

        # Check if snake ate the apple
        if self.check_collision_with_apple(apple, new_head_x, new_head_y):
            # Score stuff
            self.score += 10 + int(round(self.time_bonus)) * 5
            self.time_bonus = min(self.score*self.time_bonus_factor, self.TIME_BONUS)
            self.score_updated_this_frame = True
            self.grow()
            respawn = True

            # Play apple eaten sound
            apple_eaten.play()

        # Remove tail if not growing
        if self.growth_pending > 0:
            self.growth_pending -= 1
            self.segments_to_update.add((head_x, head_y))
        else:
            tail_x, tail_y = self.segments.pop()
            # Clear tail position in board
            self.board.grid.iloc[tail_y, tail_x] = 0
            self.board.squares_to_update.add((tail_x, tail_y))

        # Check if snake hits itself
        if (new_head_x, new_head_y) in self.segments:
            # Play collision sound
            collision.play()
            return "game_over"  # Game over

        # Add new head to segments
        self.segments.insert(0, (new_head_x, new_head_y))
        self.segments_to_update.add((new_head_x, new_head_y))

        # Update board with new head position
        self.board.grid.iloc[new_head_y, new_head_x] = 1

        # Check if the snake has filled up the board
        if len(self.segments) >= self.board.width * self.board.height:
            return "game_won"

        self.changed_direction_this_frame = False
        if self.direction_change_pending:
            self.change_direction(*self.direction_change_pending.pop(0))

        # If apple was eaten, spawn new apple
        if respawn:
            apple.spawn()

        if self.time_bonus >= 0:
            self.time_bonus -= 0.06
        return "game"  # Game continues

    def render(self, surface):
        """Draw the snake on the surface"""
        for segment in self.segments_to_update:
            x, y = segment
            # Draw the segment
            rect = pygame.Rect(
                x * self.grid_size,
                y * self.grid_size,
                self.grid_size,
                self.grid_size
            )

            # Make the head a slightly different color
            # We use segments for indexing and not segments_to_update as lists are ordered
            # but sets are unordered
            if segment == self.segments[0]:
                pygame.draw.rect(surface, self.head_color, rect)  # Darker green for head
                # Draw eyes
                eye_size = self.grid_size // 5
                dx, dy = self.direction

                # Position the eyes based on current direction
                if dx == 1:  # Right
                    left_eye = (x * self.grid_size + 3 * self.grid_size // 4,
                                y * self.grid_size + self.grid_size // 4)
                    right_eye = (x * self.grid_size + 3 * self.grid_size // 4,
                                 y * self.grid_size + 3 * self.grid_size // 4)
                elif dx == -1:  # Left
                    left_eye = (x * self.grid_size + self.grid_size // 4,
                                y * self.grid_size + self.grid_size // 4)
                    right_eye = (x * self.grid_size + self.grid_size // 4,
                                 y * self.grid_size + 3 * self.grid_size // 4)
                elif dy == 1:  # Down
                    left_eye = (x * self.grid_size + self.grid_size // 4,
                                y * self.grid_size + 3 * self.grid_size // 4)
                    right_eye = (x * self.grid_size + 3 * self.grid_size // 4,
                                 y * self.grid_size + 3 * self.grid_size // 4)
                else:  # Up
                    left_eye = (x * self.grid_size + self.grid_size // 4,
                                y * self.grid_size + self.grid_size // 4)
                    right_eye = (x * self.grid_size + 3 * self.grid_size // 4,
                                 y * self.grid_size + self.grid_size // 4)

                pygame.draw.circle(surface, WHITE, left_eye, eye_size)  # White eye
                pygame.draw.circle(surface, WHITE, right_eye, eye_size)  # White eye
                pygame.draw.circle(surface, BLACK, left_eye, eye_size // 2)  # Black pupil
                pygame.draw.circle(surface, BLACK, right_eye, eye_size // 2)  # Black pupil

            else:
                # Regular body segment
                pygame.draw.rect(surface, self.color, rect)

                # Draw a smaller rectangle inside for a better look
                inner_rect = pygame.Rect(
                    x * self.grid_size + 2,
                    y * self.grid_size + 2,
                    self.grid_size - 4,
                    self.grid_size - 4
                )
                pygame.draw.rect(surface, (0, 220, 0), inner_rect)  # Lighter green for inner part
