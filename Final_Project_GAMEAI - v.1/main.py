# main.py
import pygame
from config import *
from object import *
import sys

# Game Class to encapsulate all game logic
class Game:
    def __init__(self):
        pygame.init()
        
        # Set up the screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Game")
        
        # Clock to control the frame rate
        self.clock = pygame.time.Clock()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()

        self.pellet_count = 0

    def count_total_pellets(self):
        total_pellets = 0
        for row in tilemap:
            total_pellets += row.count('.')  # Count pellets represented by '.'
        return total_pellets

    # Initialize game elements
    def init_game(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.blocks.empty()
        self.pellets.empty()

        self.pellet_count = self.count_total_pellets()  # Get the total pellet count
        print(f"Total pellets: {self.pellet_count}")  # Print total for verification

        for row_index, row in enumerate(tilemap):
            for col_index, tile in enumerate(row):
                if tile == 'W':
                    Block(self, col_index, row_index)  # Walls/Blocks
                elif tile == 'P':
                    self.player = Player(self, col_index, row_index)  # Pac-Man Player
                elif tile == 'R':
                    self.blinky = Blinky(self, col_index, row_index)  # Ghost Enemy
                    self.enemies.add(self.blinky)
                elif tile == 'L':
                    self.pinky = Pinky(self, col_index, row_index)  # Ghost Enemy
                    self.enemies.add(self.pinky)
                elif tile == '.':
                    Pellet(self, col_index, row_index)  # Pellets
                elif tile == ' ':
                    Ground(self, col_index, row_index)  # Ground

        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)
        self.all_sprites.add(self.blocks)
        self.all_sprites.add(self.pellets)

    def draw_text(self, text, font, color, surface, x, y):
        """Helper function to draw text on screen."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        surface.blit(text_obj, text_rect)

    # Intro Screen
    def intro_screen(self):
        font = pygame.font.Font(None, 74)
        while True:
            self.screen.fill(BLACK)
            self.draw_text("PAC-MAN", font, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            self.draw_text("Press ENTER to Start", font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return  # Exit the intro screen and start the game

            pygame.display.flip()
            self.clock.tick(60)

    # Game Over Screen
    def game_over_screen(self, status):
        font = pygame.font.Font(None, 74)
        button_font = pygame.font.Font(None, 50)

        # Define the retry button rectangle
        retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)

        while True:
            self.screen.fill(BLACK)
            
            if status == 'win':
                self.draw_text("YOU WIN!", font, GREEN, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            elif status == 'lose':
                self.draw_text("GAME OVER", font, RED, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

            pygame.draw.rect(self.screen, WHITE, retry_button)
            self.draw_text("Restart?", button_font, BLACK, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 125)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and retry_button.collidepoint(event.pos):
                        return 'retry'

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return 'retry'

            pygame.display.flip()
            self.clock.tick(60)

    # Main game loop
    def game_loop(self):
        self.init_game()
        goal_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if self.player and not self.player.moving:
                if keys[pygame.K_LEFT]:
                    self.player.move(-1, 0)
                if keys[pygame.K_RIGHT]:
                    self.player.move(1, 0)
                if keys[pygame.K_UP]:
                    self.player.move(0, -1)
                if keys[pygame.K_DOWN]:
                    self.player.move(0, 1)

            # Move Blinky using its specific logic (for now, using BFS as a placeholder)
            if not self.blinky.path:
                goal_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)
                self.blinky.path = self.blinky.bfs((self.blinky.rect.x // TILESIZE, self.blinky.rect.y // TILESIZE), goal_tile, tilemap)
            self.blinky.move()

            if not self.pinky.path:
                print("Calculating path for Pinky...")
                player_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)
                radius = 4
                offset_x = radius if self.player.direction[0] >= 0 else -radius
                offset_y = radius if self.player.direction[1] >= 0 else -radius
                pinky_goal_tile = (player_tile[0] + offset_x, player_tile[1] + offset_y)
                pinky_goal_tile = (
                    max(0, min(len(tilemap[0]) - 1, pinky_goal_tile[0])), 
                    max(0, min(len(tilemap) - 1, pinky_goal_tile[1]))
                )

                # Print the goal tile to verify it's being calculated correctly
                print(f"Pinky's goal tile: {pinky_goal_tile}")

                # Calculate the path using Pinky's goal tile
                self.pinky.path = self.pinky.bfs((self.pinky.rect.x // TILESIZE, self.pinky.rect.y // TILESIZE), pinky_goal_tile, tilemap)
                print(f"Pinky's path: {self.pinky.path}")
            self.pinky.move()




            self.all_sprites.update()
            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)

            collected_pellets = pygame.sprite.spritecollide(self.player, self.pellets, True)
            if collected_pellets:
                self.pellet_count -= len(collected_pellets)
                print(f"Collected pellets: {len(collected_pellets)}, Remaining pellets: {self.pellet_count}")

            if self.pellet_count <= 0:
                result = self.game_over_screen('win')
                return result == 'retry'

            if pygame.sprite.spritecollideany(self.player, self.enemies):
                result = self.game_over_screen('lose')
                return result == 'retry'

            pygame.display.flip()
            self.clock.tick(FPS)


# Start the game loop
if __name__ == '__main__':
    game = Game()
    game.intro_screen()
    while True:
        result = game.game_loop()
        if not result:
            pygame.quit()
            sys.exit()
