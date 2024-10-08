import pygame
from config import *
from object import *
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Game")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
blocks = pygame.sprite.Group()
pellets = pygame.sprite.Group()

pellet_count = 0

def count_total_pellets():
    total_pellets = 0
    for row in tilemap:
        total_pellets += row.count('.')  # Count pellets represented by '.'
    return total_pellets

# Initialize game elements
def init_game():
    global player, pellet_count

    # Clear previous sprite groups to avoid overlap on retry
    all_sprites.empty()
    enemies.empty()
    blocks.empty()
    pellets.empty()

    pellet_count = count_total_pellets()  # Get the total pellet count
    print(f"Total pellets: {pellet_count}")  # Print total for verification

    for row_index, row in enumerate(tilemap):
        for col_index, tile in enumerate(row):
            if tile == 'W':
                Block(game, col_index, row_index)  # Walls/Blocks
            elif tile == 'P':
                player = Player(game, col_index, row_index)  # Pac-Man Player
            elif tile == 'E':
                enemy = Enemy(game, col_index, row_index)  # Ghost Enemy
            elif tile == '.':
                pellet = Pellet(game, col_index, row_index)  # Pellets
                pellets.add
                # No need to increment pellet_count here
            elif tile == ' ':
                Ground(game, col_index, row_index)  # Ground

    # Add sprites to the all_sprites group for drawing and updating
    all_sprites.add(player)
    all_sprites.add(enemies)
    all_sprites.add(blocks)
    all_sprites.add(pellets)


def draw_text(text, font, color, surface, x, y):
    """Helper function to draw text on screen."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Intro Screen
def intro_screen():
    font = pygame.font.Font(None, 74)
    while True:
        screen.fill(BLACK)
        draw_text("PAC-MAN", font, YELLOW, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text("Press ENTER to Start", font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Exit the intro screen and start the game

        pygame.display.flip()
        clock.tick(60)

# Game Over Screen
def game_over_screen():
    font = pygame.font.Font(None, 74)
    button_font = pygame.font.Font(None, 50)

    # Define the retry button rectangle
    retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)

    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        pygame.draw.rect(screen, WHITE, retry_button)  # Draw the retry button
        draw_text("Retry", button_font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 125)

        # Check events for quitting or button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check for mouse button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    if retry_button.collidepoint(event.pos):
                        return 'retry' # Exit the game over screen and retry

            # Allow retry using keyboard "Enter" key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'retry' # Restart the game when "Enter" is pressed

        pygame.display.flip()
        clock.tick(60)

# Main game loop
def game_loop():
    global pellet_count  # Declare pellet_count as global

    init_game()  # Initialize game elements

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle player movement
        keys = pygame.key.get_pressed()
        player = next((sprite for sprite in all_sprites if isinstance(sprite, Player)), None)  # Get player instance

        if player and not player.moving:  # Only allow new movement if player is not already moving
            if keys[pygame.K_LEFT]:
                player.move(-1, 0)  # Move left by one tile
            if keys[pygame.K_RIGHT]:
                player.move(1, 0)  # Move right by one tile
            if keys[pygame.K_UP]:
                player.move(0, -1)  # Move up by one tile
            if keys[pygame.K_DOWN]:
                player.move(0, 1)  # Move down by one tile

        # Update sprites
        all_sprites.update()

        # Drawing
        screen.fill(BLACK)  # Clear screen
        all_sprites.draw(screen)  # Draw all sprites

        # Check for collisions between player and pellets
        collected_pellets = pygame.sprite.spritecollide(player, pellets, True)
        if collected_pellets:
            pellet_count -= len(collected_pellets)  # Decrease pellet count
            print(f"Collected pellets: {len(collected_pellets)}, Remaining pellets: {pellet_count}")

        # Check if all pellets have been collected
        if pellet_count <= 0:
            print("You collected all the pellets! You win!")
            result = game_over_screen()
            draw_text("GAME OVER", font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            if result == 'retry':
                return True  # Indicate to retry the game loop
            else:
                return False  # Exit the game loop

        # Check for collisions between player and enemies
        if pygame.sprite.spritecollideany(player, enemies):
            # Handle Pac-Man being caught by a ghost
            print("Caught by a ghost!")
            result = game_over_screen()
            if result == 'retry':
                return True  # Indicate to retry the game loop
            else:
                return False  # Exit the game loop

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)


# Start the game loop
if __name__ == '__main__':
    game = type('Game', (object,), {})()  # Create a game instance to pass to objects
    game.all_sprites = all_sprites
    game.enemies = enemies
    game.blocks = blocks
    game.pellets = pellets
    game.tilemap = tilemap
    intro_screen()
    # Main game loop with retry logic
    while True:
        result = game_loop()  # Run the main game loop
        if not result:
            pygame.quit()
            sys.exit()  # Exit the game if the player doesn't want to retry
