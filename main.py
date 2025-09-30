import sys
from src.config import *
from src.db_handler import connect_database, save_score, get_scores_data
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from src.main_menu import Button, Dropdown, ScrollableText, TextInput
from src.snake import Snake
from src.apple import Apple
from src.board import Board

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 90
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = int(SCREEN_HEIGHT * (3/4) // GRID_SIZE)
FPS = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

selected_graph_speed = speeds[0]
selected_graph_size = board_sizes[0]
selected_graph_type = graph_types[0]
graph_surface = None
current_screen = "main_menu"

# Graph stuff
graph_width = SCREEN_WIDTH * 0.8
graph_height = SCREEN_HEIGHT * 0.5

# Game Setup

selected_speed = speeds[0]  # Default to Medium
selected_board_size = board_sizes[0]
player_name = "Player"

# Initialize game objects

render_surface = None
snake = None
apple = None
board = None

# Create main menu buttons
new_game_button = Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, "New Game", LIGHT_GREEN, LIME_GREEN)
how_to_play_button = Button(SCREEN_WIDTH // 2 - 100, 280, 200, 50, "How to Play", LIGHT_GREEN, LIME_GREEN)
statistics_button = Button(SCREEN_WIDTH // 2 - 100, 360, 200, 50, "Statistics", LIGHT_GREEN, LIME_GREEN)

# Back button for other screens
back_button = Button(SCREEN_WIDTH // 2 - 100, 520, 200, 50, "Back to Menu", LIGHT_GREEN, LIME_GREEN)

# Create dropdown for game modes
graph_speed_dropdown = Dropdown(SCREEN_WIDTH * 0.14, SCREEN_HEIGHT * 0.16, SCREEN_WIDTH * 0.15, 25, speeds, LIGHT_GREEN,
                                LIME_GREEN)
graph_size_dropdown = Dropdown(SCREEN_WIDTH * 0.4, SCREEN_HEIGHT * 0.16, SCREEN_WIDTH * 0.15, 25, board_sizes,
                               LIGHT_GREEN, LIME_GREEN)

# Create dropdown for graph types
graph_type_dropdown = Dropdown(SCREEN_WIDTH * 0.75, SCREEN_HEIGHT * 0.154, SCREEN_WIDTH * 0.24, 32, graph_types,
                               LIGHT_GREEN, LIME_GREEN)

# Game Setup UI

# Text input for player name
player_name_input = TextInput(SCREEN_WIDTH * 0.45, SCREEN_HEIGHT * 0.2, SCREEN_WIDTH * 0.38, 40)

speed_dropdown = Dropdown(SCREEN_WIDTH * 0.45, SCREEN_HEIGHT * 0.3, SCREEN_WIDTH * 0.2, 35, speeds, LIGHT_GREEN,
                          LIME_GREEN)
board_size_dropdown = Dropdown(SCREEN_WIDTH * 0.45, SCREEN_HEIGHT * 0.6, SCREEN_WIDTH * 0.2, 35, board_sizes,
                               LIGHT_GREEN, LIME_GREEN)

start_game_button = Button(SCREEN_WIDTH // 2 + 50, 520, 200, 50, "Start Game", LIGHT_GREEN, LIME_GREEN)
back_to_menu_button = Button(SCREEN_WIDTH // 2 - 250, 520, 200, 50, "Back to Menu", LIGHT_GREEN, LIME_GREEN)

# How to play text
how_to_play_content = """\
Snake Game Rules:

1. Control your snake using the arrow keys (Up, Down, Left, Right).

2. Eat the food (apples) that appear on the screen to grow your snake and increase your score.

3. Each time you eat food, your snake will grow longer, making the game more challenging.

4. Avoid colliding with your own tail! If you do, the game is over.

5. The game has three snake speed levels:
   - Slow: For the casual players, having a nice relaxed game
   - Medium: Standard snake speed
   - Fast: Can you manoeuvre this turbo snake at the fastest speed?

6. The game has three board sizes:
   - Small: For a quick and easy game
   - Medium: Standard board size
   - Large: A truly rewarding challenge!

7. Your score is based on:
   - Food eaten (20 points each)
   - Time bonus (How quickly you can eat the apples)

8. The game will automatically save your high scores in the database.

9. Try to beat your personal best and compete with friends for the highest score!

10. Have fun and enjoy the classic Snake game experience!\
"""

how_to_play_text = ScrollableText(100, 100, 600, 400, how_to_play_content)


# Function to generate graph surface
def generate_graph(graph_type, snake_speed, board_size):
    try:
        player_names, scores, ids = get_scores_data(snake_speed, board_size, graph_type == "Score vs Player")

        # Create a fixed-size surface for the graph
        surf = pygame.Surface((graph_width, graph_height))
        surf.fill(WHITE)

        if not scores:
            # Display a message if no data
            no_data_text = medium_font.render(f"No Data Available for {snake_speed} Speed with {board_size} Size", True,
                                              BLACK)
            text_rect = no_data_text.get_rect(center=(graph_width // 2, graph_height // 2))
            surf.blit(no_data_text, text_rect)
            return surf

        # Create matplotlib figure without using plt.figure() as that scales the window down for some reason

        fig = Figure(figsize=(graph_width / 80, graph_height / 80), dpi=80)
        ax = fig.add_subplot(111)

        if graph_type == "Score vs Player":
            # Create a bar graph of scores by player
            ax.bar(range(len(player_names)), scores, color=pygame.Color(FOREST_GREEN).normalize())
            ax.set_xticks(range(len(player_names)))
            ax.set_xticklabels(player_names, rotation=45, ha='right')
            ax.set_ylabel('Score')
            ax.set_title(f'Top Scores for {snake_speed} Speed with {board_size} Board Size')
        else:  # Score vs Attempt Num
            # Create a line graph of scores over time
            ax.plot(ids, scores, "o-", color=pygame.Color(FOREST_GREEN).normalize())
            ax.set_ylabel('Score')
            ax.set_title(f'Score History for {snake_speed} Speed with {board_size} Board Size')

        fig.tight_layout()

        # Convert the Matplotlib figure to a pygame surface
        canvas = FigureCanvas(fig)
        canvas.draw()

        # Get the RGBA buffer from the figure canvas
        buf = canvas.buffer_rgba()

        # Create pygame surface from the buffer
        graph_surf = pygame.image.frombuffer(
            buf, (int(fig.bbox.width), int(fig.bbox.height)), "RGBA")

        # Blit the graph to our fixed size surface
        surf.blit(graph_surf, (0, 0))
        return surf

    except Exception as e:
        print(f"Error generating graph: {e}")
        # Return a blank surface with an error message
        surf = pygame.Surface((graph_width, graph_height))
        surf.fill(WHITE)
        error_text = medium_font.render("Error generating graph", True, BLACK)
        surf.blit(error_text, (200, 160))
        return surf


# Main menu elements
def draw_main_menu(surface):
    # Draw background
    surface.fill(DARK_GREEN)

    # Draw title
    title_text = title_font.render("Snake Game", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    surface.blit(title_text, title_rect)

    # Draw buttons
    new_game_button.draw(surface)
    how_to_play_button.draw(surface)
    statistics_button.draw(surface)


# Player setup screen elements
def draw_game_setup(surface):
    # Draw background
    surface.fill(DARK_GREEN)

    # Draw title
    title_text = large_font.render("Game Setup", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    surface.blit(title_text, title_rect)

    # Player name label
    name_label = medium_font.render("Player Name:", True, WHITE)
    surface.blit(name_label, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.2))

    # Speed label
    speed_label = medium_font.render("Snake Speed:", True, WHITE)
    surface.blit(speed_label, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.3))

    # Difficulty label
    board_size_label = medium_font.render("Board Size:", True, WHITE)
    surface.blit(board_size_label, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.6))

    # Draw text input
    player_name_input.draw(surface)

    # Draw dropdowns
    speed_dropdown.draw(surface)
    board_size_dropdown.draw(surface)

    # Draw buttons
    start_game_button.draw(surface)
    back_to_menu_button.draw(surface)  # TextInput class for player name input


def draw_game_over(surface, score):
    # Display game over screen with option to restart
    surface.fill(BACKGROUND_COLOR)
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render('GAME OVER', True, RED)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)

    surface.blit(game_over_text, (SCREEN_WIDTH * 0.5 - game_over_text.get_width() // 2, SCREEN_HEIGHT * 0.2))
    surface.blit(score_text, (SCREEN_WIDTH * 0.5 - score_text.get_width() // 2, SCREEN_HEIGHT * 0.4))
    surface.blit(restart_text, (SCREEN_WIDTH * 0.5 - restart_text.get_width() // 2, SCREEN_HEIGHT * 0.6))

    back_button.draw(surface)


def draw_game_won(surface, score):
    # Display game over screen with option to restart
    surface.fill(BACKGROUND_COLOR)
    font = pygame.font.SysFont(None, 72)
    game_won_text = font.render('GAME WON', True, YELLOW)
    score_text = font.render(f'Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)

    surface.blit(game_won_text, (SCREEN_WIDTH * 0.5 - game_won_text.get_width() // 2, SCREEN_HEIGHT * 0.2))
    surface.blit(score_text, (SCREEN_WIDTH * 0.5 - score_text.get_width() // 2, SCREEN_HEIGHT * 0.4))
    surface.blit(restart_text, (SCREEN_WIDTH * 0.5 - restart_text.get_width() // 2, SCREEN_HEIGHT * 0.6))

    back_button.draw(surface)


# How to Play screen elements
def draw_how_to_play(surface):
    # Draw background
    surface.fill(DARK_GREEN)

    # Draw title
    title_text = large_font.render("How to Play", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    surface.blit(title_text, title_rect)

    # Draw the scrollable text box
    how_to_play_text.draw(surface)

    # Draw back button
    back_button.draw(surface)


# Statistics screen elements
def draw_statistics(surface, graph_surf):
    # Draw background
    surface.fill(DARK_GREEN)

    # Draw title
    title_text = large_font.render("Game Statistics", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    surface.blit(title_text, title_rect)

    # Draw dropdowns
    graph_speed_dropdown.draw(surface)
    graph_size_dropdown.draw(surface)
    graph_type_dropdown.draw(surface)

    # Snake Speed label
    speed_label = medium_font.render("Speed:", True, WHITE)
    surface.blit(speed_label, (SCREEN_WIDTH * 0.03, SCREEN_HEIGHT * 0.15))

    # Snake Size label
    size_label = medium_font.render("Size:", True, WHITE)
    surface.blit(size_label, (SCREEN_WIDTH * 0.31, SCREEN_HEIGHT * 0.15))

    # Graph type label
    graph_label = medium_font.render("Graph Type:", True, WHITE)
    surface.blit(graph_label, (SCREEN_WIDTH * 0.57, SCREEN_HEIGHT * 0.15))

    # Generate and draw the current graph
    if not graph_surf:
        graph_surf = generate_graph(selected_graph_type, selected_graph_speed, selected_graph_size)
    # Create a white background for the graph area
    x = SCREEN_WIDTH * 0.12
    y = SCREEN_HEIGHT / 3
    graph_bg = pygame.Surface((graph_width, graph_height))
    graph_bg.fill(WHITE)
    surface.blit(graph_bg, (x, y))
    # Center the graph on the white background
    graph_x = x + (graph_width - graph_surf.get_width()) // 2
    graph_y = y + (graph_height - graph_surf.get_height()) // 2
    surface.blit(graph_surf, (graph_x, graph_y))

    # Draw back button
    back_button.draw(surface)
    return graph_surf


def handle_menu_events(event, mouse_pos):
    global selected_graph_speed, selected_graph_size, selected_graph_type, graph_surface, \
        selected_speed, selected_board_size, current_screen, player_name
    event_handled = False

    # Main menu event handling
    if current_screen == "main_menu":
        new_game_button.check_hover(mouse_pos)
        how_to_play_button.check_hover(mouse_pos)
        statistics_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if new_game_button.is_clicked(mouse_pos, event):
                current_screen = "game_setup"
            elif how_to_play_button.is_clicked(mouse_pos, event):
                current_screen = "how_to_play"
            elif statistics_button.is_clicked(mouse_pos, event):
                current_screen = "statistics"

    # Player setup screen event handling
    elif current_screen == "game_setup":
        # Handle dropdown events
        if speed_dropdown.handle_event(mouse_pos, event):
            selected_speed = speed_dropdown.selected_option

        if board_size_dropdown.handle_event(mouse_pos, event):
            selected_board_size = board_size_dropdown.selected_option

        # Handle Textinput events
        player_name_input.handle_event(event)

        # Handle button events
        start_game_button.check_hover(mouse_pos)
        back_to_menu_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_game_button.is_clicked(mouse_pos, event):
                player_name = player_name_input.text if player_name_input.text else "Player"
                current_screen = "game"
                initialize_game(screen)
            elif back_to_menu_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"

    # Restart game if game over and player presses 'r'
    elif current_screen == "game_over" or current_screen == "game_won":

        back_button.check_hover(mouse_pos)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            initialize_game(screen)
            current_screen = "game"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"

    # How to play screen event handling
    elif current_screen == "how_to_play":
        back_button.check_hover(mouse_pos)

        how_to_play_text.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"

    # Statistics screen event handling
    elif current_screen == "statistics":
        back_button.check_hover(mouse_pos)

        # Handle dropdown events
        if (graph_speed_dropdown.handle_event(mouse_pos, event) and
                selected_graph_speed != graph_speed_dropdown.selected_option):
            selected_graph_speed = graph_speed_dropdown.selected_option
            graph_surface = None

        if (graph_size_dropdown.handle_event(mouse_pos, event) and
                selected_graph_size != graph_size_dropdown.selected_option):
            selected_graph_size = graph_size_dropdown.selected_option
            graph_surface = None

        if (graph_type_dropdown.handle_event(mouse_pos, event) and
                selected_graph_type != graph_type_dropdown.selected_option):
            selected_graph_type = graph_type_dropdown.selected_option
            graph_surface = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"
                graph_surface = None

    return event_handled


# noinspection PyUnresolvedReferences
def draw_menus():
    global graph_surface
    # Drawing the current screen
    if current_screen == "main_menu":
        draw_main_menu(screen)
    elif current_screen == "game_setup":
        draw_game_setup(screen)
    elif current_screen == "game_over":
        draw_game_over(screen, snake.score)
    elif current_screen == "game_won":
        draw_game_won(screen, snake.score)
    elif current_screen == "how_to_play":
        draw_how_to_play(screen)
    elif current_screen == "statistics":
        graph_surface = draw_statistics(screen, graph_surface)

    pygame.display.flip()


# noinspection PyShadowingNames
def draw_objects(screen, render_surface, snake, apple, board, init=False):
    if init:
        screen.fill(BACKGROUND_COLOR)

    # Render the board (grid lines, borders, etc.)
    board.render(render_surface, init)

    # Render the apple
    apple.render(render_surface)

    # Render the snake
    snake.render(render_surface)
    board.render_border(render_surface)
    screen.blit(render_surface, (board.start_x, board.start_y))

    # Display score if score has updated
    if snake.score_updated_this_frame:
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)

        # Clear the previous score and redraw new score
        width, height = score_text.get_width()+15, score_text.get_height()+15
        rect = pygame.Rect(10, 10, width, height)
        screen.fill(BACKGROUND_COLOR, rect=rect)
        screen.blit(score_text, rect.topleft)

        snake.score_updated_this_frame = False

    # Update the display so that the rendered objects appear on the screen
    pygame.display.flip()


def initialize_game(surface):
    # Create a board
    global render_surface, board, snake, apple, GRID_WIDTH, GRID_HEIGHT, GRID_SIZE

    square_num = board_sizes_val[selected_board_size]
    GRID_SIZE = max(SCREEN_WIDTH // square_num, SCREEN_HEIGHT * (4 / 5) // square_num)
    GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
    GRID_HEIGHT = int(SCREEN_HEIGHT * (4 / 5) // GRID_SIZE)

    render_surface = pygame.Surface((GRID_WIDTH * GRID_SIZE + 5, GRID_HEIGHT * GRID_SIZE + 5))
    board = Board(GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, 0, int(SCREEN_HEIGHT-GRID_HEIGHT*GRID_SIZE))

    # Create a snake at the center of the board
    snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2, GRID_SIZE, board, speeds_val[selected_speed])

    # Create an apple at a random position
    apple = Apple(board, GRID_SIZE)

    draw_objects(surface, render_surface, snake, apple, board, True)


# noinspection PyTypeChecker,PyUnresolvedReferences
def game_loop():
    # Setup database
    global current_screen
    conn, cursor = connect_database("snake_game.db")

    # Main game loop
    running = True
    while running:

        # Control game speed
        delta = clock.tick(FPS)

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Main menu event handling
            handle_menu_events(event, mouse_pos)

            if current_screen == "game":
                snake.handle_event(event)

        draw_menus()

        if current_screen == "game":
            # Update snake position
            current_screen = snake.update(apple)

            # Render all objects
            draw_objects(screen, render_surface, snake, apple, board)

            if current_screen != "game":
                # Save the score to database
                save_score(cursor, conn, player_name, selected_speed, selected_board_size, snake.score)
                clock.tick(1)

        elif current_screen == "game_setup":
            player_name_input.update(delta)

    # Clean up and close
    conn.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
