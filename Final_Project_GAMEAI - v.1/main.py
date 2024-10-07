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

# Initialize game elements
def init_game():
    global player, pellet_count

    pellet_count = 0

    for row_index, row in enumerate(tilemap):
        for col_index, tile in enumerate(row):
            if tile == 'W':
                Block(game, col_index, row_index)  # Walls/Blocks
            elif tile == 'P':
                player = Player(game, col_index, row_index)  # Pac-Man Player
            elif tile == 'E':
                enemy = Enemy(game, col_index, row_index)  # Ghost Enemy
            elif tile == '.':
                Pellet(game, col_index, row_index)  # Pellets
                pellet_count += 1
            elif tile == ' ':
                Ground(game, col_index, row_index) # ground

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

        # Teleportation logic
        tile_x = player.rect.x // TILESIZE
        tile_y = player.rect.y // TILESIZE

        # Update sprites
        all_sprites.update()

        # Drawing
        screen.fill(BLACK)  # Clear screen
        all_sprites.draw(screen)  # Draw all sprites

        # Check for collisions between player and pellets
        collected_pellets = pygame.sprite.spritecollide(player, pellets, True)
        if collected_pellets:
            pellet_count -= len(collected_pellets)  # Decrease pellet count

        # Check if all pellets have been collected
        if pellet_count == 0:
            print("You collected all the pellets! You win!")
            pygame.quit()
            sys.exit()

        # Check for collisions between player and enemies
        if pygame.sprite.spritecollideany(player, enemies):
            # Handle Pac-Man being caught by a ghost
            print("Caught by a ghost!")
            pygame.quit()
            sys.exit()

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
    game_loop()
