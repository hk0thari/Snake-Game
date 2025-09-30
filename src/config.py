# To handle game rules, assets etc
import pygame

# Initialise pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKEST_GREEN = (0, 25, 0)
DARKER_GREEN = (0, 30, 10)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (50, 205, 50)
LIME_GREEN = (0, 255, 0)
FOREST_GREEN = (34, 139, 34)
GREEN = (0, 128, 0)
GRAY = (200, 200, 200)
RED = (255, 10, 50)
YELLOW = (255, 190, 10)

BACKGROUND_COLOR = DARK_GREEN
board_bg_color = DARKER_GREEN
board_grid_color = DARK_GREEN
board_border_color = DARKEST_GREEN

# Font
title_font = pygame.font.SysFont("comicsansms", 60)
large_font = pygame.font.SysFont("comicsansms", 36)
medium_font = pygame.font.SysFont("comicsansms", 24)
small_font = pygame.font.SysFont("comicsansms", 18)

# Sounds
apple_eaten = pygame.mixer.Sound("Assets/apple_eaten.wav")
collision = pygame.mixer.Sound("Assets/collision.wav")
turn = pygame.mixer.Sound("Assets/turn.wav")

# Game modes and Graphs
graph_types = ["Score vs Player", "Score vs Attempts"]

speeds = ["Slow", "Medium", "Fast"]
speeds_val = {
    "Slow": 4,
    "Medium": 6,
    "Fast": 10
}
board_sizes = ["Small", "Medium", "Large"]
board_sizes_val = {
    "Small": 10,
    "Medium": 15,
    "Large": 20
}

# Rules
rules = {
    # Can take values E for End, T for Teleport (to the other end of the board),
    "on_wall_collision": "T"
}

# Sql queries
player_by_score_query = """SELECT id, player_name, score
FROM scores
WHERE snake_speed = 'Slow' AND board_size = 'Small'
AND (player_name, score) IN (
    SELECT player_name, MAX(score)
    FROM scores
    WHERE snake_speed = 'Slow' AND board_size = 'Small'
    GROUP BY player_name
    )
ORDER BY score DESC
LIMIT 100;"""
