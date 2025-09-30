from src.config import *


# Button class for easier button management
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK, font=medium_font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        # Draw the button rect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Black border

        # Draw the text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Dropdown class for game modes and graph types
class Dropdown:
    def __init__(self, x, y, width, height, options, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_option = options[0]
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_open = False
        self.is_hovered = False
        self.option_rects = []

        # Create option rects
        for i, option in enumerate(options):
            option_rect = pygame.Rect(x, y + (i + 1) * height, width, height)
            self.option_rects.append(option_rect)

    def draw(self, surface):
        # Draw the dropdown button
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Black border

        # Draw the selected option text
        rect = self.rect.copy()
        rect.width -= 22
        text_surf = small_font.render(self.selected_option, True, self.text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

        # Draw dropdown arrow
        pygame.draw.polygon(surface, BLACK,
                            [(self.rect.right - 20, self.rect.centery - 5),
                             (self.rect.right - 10, self.rect.centery + 5),
                             (self.rect.right - 30, self.rect.centery + 5)])

        # Draw the options if dropdown is open
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                pygame.draw.rect(surface, LIGHT_GREEN, option_rect)
                pygame.draw.rect(surface, BLACK, option_rect, 2)

                option_text = small_font.render(self.options[i], True, BLACK)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                surface.blit(option_text, option_text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                return True

            if self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(pos):
                        self.selected_option = self.options[i]
                        self.is_open = False
                        return True
        return False


# ScrollableText class for the how to play screen
class ScrollableText:
    def __init__(self, x, y, width, height, text, line_spacing=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.line_spacing = line_spacing
        self.scroll_y = 0
        self.scroll_speed = 15
        self.max_scroll = 0
        self.lines = self._wrap_text(text, width)
        self.padding = 10

        # Calculate max scroll based on content height
        total_height = len(self.lines) * self.line_spacing + self.padding
        self.max_scroll = max(0, total_height - height)

    def _wrap_text(self, text, width):
        # Split text into paragraphs based on double newlines
        paragraphs = text.split('\n\n')
        all_lines = []

        for paragraph in paragraphs:
            # If paragraph is just a newline, add an empty line
            if not paragraph.strip():
                all_lines.append("")
                continue

            # Process each line within a paragraph
            paragraph_lines = paragraph.split('\n')
            for line in paragraph_lines:
                # If the line is short enough, add it directly
                if medium_font.size(line)[0] < width - 20:
                    all_lines.append(line)
                    continue

                # Otherwise, wrap the line word by word
                words = line.split()
                current_line = ""

                for word in words:
                    test_line = current_line + word + " "
                    text_width = medium_font.size(test_line)[0]

                    if text_width < width - 20:
                        current_line = test_line
                    else:
                        all_lines.append(current_line)
                        current_line = word + " "

                if current_line:
                    all_lines.append(current_line)

        return all_lines

    def draw(self, surface):
        # Draw the background
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Create a clipping rectangle to prevent text from rendering outside the box
        surface.set_clip(self.rect)

        # Draw the text
        y_pos = self.rect.top - self.scroll_y
        for line in self.lines:
            text_surf = medium_font.render(line, True, BLACK)
            surface.blit(text_surf, (self.rect.left + 10, y_pos))
            y_pos += self.line_spacing

        # Reset clipping rectangle
        surface.set_clip(None)

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_height = max(50,
                                   int(self.rect.height * (self.rect.height / (self.rect.height + self.max_scroll))))
            scrollbar_pos = self.rect.top + (self.scroll_y / self.max_scroll) * (self.rect.height - scrollbar_height)

            scrollbar_rect = pygame.Rect(self.rect.right - 15, scrollbar_pos, 10, scrollbar_height)
            pygame.draw.rect(surface, DARK_GREEN, scrollbar_rect)
            pygame.draw.rect(surface, BLACK, scrollbar_rect, 1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN:  # Scroll down
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                return True
        return False


class TextInput:
    def __init__(self, x, y, width, height, font=medium_font, max_length=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = font
        self.color = WHITE
        self.active_color = LIGHT_GREEN
        self.inactive_color = GRAY
        self.border_color = BLACK
        self.text_color = BLACK
        self.cursor_color = BLACK
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds
        self.max_length = max_length

    def draw(self, surface):
        # Draw the input box
        border_color = self.active_color if self.active else self.inactive_color
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw the text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(topleft=(self.rect.x + 5,
                                                self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        surface.blit(text_surf, text_rect)

        # Draw the cursor
        if self.active and self.cursor_visible:
            # Cursor positions
            cur_x = text_rect.right
            cur_y1 = text_rect.top
            cur_y2 = text_rect.bottom
            pygame.draw.line(surface, self.cursor_color, (cur_x, cur_y1), (cur_x, cur_y2), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state
            self.active = self.rect.collidepoint(event.pos)
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif len(self.text) < self.max_length:
                # Only add printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode
                    return True
        return False

    def update(self, delta_time):
        # Update cursor blink
        if self.active:
            self.cursor_timer += delta_time
            if self.cursor_timer >= self.cursor_blink_speed:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
