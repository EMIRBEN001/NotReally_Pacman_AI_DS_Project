# main.py
import pygame
from config import *
from object import *
import sys
import time

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
        self.score = 0
        self.start_time = time.time()
        self.collision_cooldown_duration = 1.0  # 1 second cooldown
        self.last_collision_time = 0  # Last time a collision occurred

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
        self.score = 0
        self.start_time = time.time()

        self.pellet_count = self.count_total_pellets()  # Get the total pellet count
        print(f"Total pellets: {self.pellet_count}")  # Print total for verification

        for row_index, row in enumerate(tilemap):
            for col_index, tile in enumerate(row):
                if tile == 'W':
                    Block(self, col_index, row_index)  # Walls/Blocks
                elif tile == 'P':
                    self.player = Player(self, col_index, row_index)  # Pac-Man Player
                elif tile == 'R':
                    self.blinky = Blinky(self, col_index, row_index)  # Red Ghost Enemy
                    self.enemies.add(self.blinky)
                elif tile == 'L':
                    self.pinky = Pinky(self, col_index, row_index)  # Pink Ghost Enemy
                    self.enemies.add(self.pinky)
                elif tile == 'I':
                    self.inky = Inky(self, col_index, row_index)  # Pink Ghost Enemy
                    self.enemies.add(self.inky)
                elif tile == 'C':
                    self.clyde = Clyde(self, col_index, row_index)  # Orange Ghost Enemy
                    self.enemies.add(self.clyde)
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
    def game_over_screen(self, status, final_score, elapsed_time):
        font = pygame.font.Font(None, 74)
        score_font = pygame.font.Font(None, 36)
        button_font = pygame.font.Font(None, 50)

        # Define the retry button rectangle
        retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)

        while True:
            self.screen.fill(BLACK)
            
            # Display the win or game over text
            if status == 'win':
                self.draw_text("YOU WIN!", font, GREEN, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
                self.draw_text(f"Final Score: {final_score}", score_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                # Display the final time in seconds
                minutes, seconds = divmod(int(elapsed_time), 60)
                time_text = f"Time: {minutes}m {seconds}s"
                self.draw_text(time_text, score_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            
            elif status == 'lose':
                self.draw_text("GAME OVER", font, RED, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
                self.draw_text(f"Final Score: {final_score}", score_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                minutes, seconds = divmod(int(elapsed_time), 60)
                time_text = f"Time: {minutes}m {seconds}s"
                self.draw_text(time_text, score_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            
            # Draw retry button
            pygame.draw.rect(self.screen, WHITE, retry_button)
            self.draw_text("Restart?", button_font, BLACK, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 125)

            # Event handling
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
        self.start_time = time.time()  # Record the start time
        goal_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)

        collision_delay = 1

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

            # Blinky (Red Ghost) Move Logic
            if not self.blinky.path:
                goal_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)
                self.blinky.path = self.blinky.bfs((self.blinky.rect.x // TILESIZE, self.blinky.rect.y // TILESIZE), goal_tile, tilemap)
            self.blinky.move()

            # Pinky (Pink Ghost) Move Logic
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
                self.pinky.path = self.pinky.bfs((self.pinky.rect.x // TILESIZE, self.pinky.rect.y // TILESIZE), pinky_goal_tile, tilemap)
            self.pinky.move()

            # Inky (Cyan Ghost) Move Logic
            if not self.inky.path:
                print("Calculating path for Pinky...")
                player_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)
                radius = 2
                offset_x = radius if self.player.direction[0] >= 0 else -radius
                offset_y = radius if self.player.direction[1] >= 0 else -radius
                inky_goal_tile = (player_tile[0] + offset_x, player_tile[1] + offset_y)
                inky_goal_tile = (
                    max(0, min(len(tilemap[0]) - 1, inky_goal_tile[0])), 
                    max(0, min(len(tilemap) - 1, inky_goal_tile[1]))
                )
                self.inky.path = self.inky.dfs((self.inky.rect.x // TILESIZE, self.inky.rect.y // TILESIZE), inky_goal_tile, tilemap)
            self.inky.move()

            # Clyde (Orange Ghost) Move Logic
            if not self.clyde.path:
                goal_tile = (self.player.rect.x // TILESIZE, self.player.rect.y // TILESIZE)
                start_tile = (self.clyde.rect.x // TILESIZE, self.clyde.rect.y // TILESIZE)
                self.clyde.path = self.clyde.dfs(start_tile, goal_tile, tilemap)
            self.clyde.move()

            # If Clyde encounters a wall during movement, clear his path to trigger a recalculation
            current_tile = (self.clyde.rect.x // TILESIZE, self.clyde.rect.y // TILESIZE)
            if tilemap[current_tile[1]][current_tile[0]] == 'W':
                self.clyde.path = []

             # Calculate elapsed time for the timer
            elapsed_time = int(time.time() - self.start_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            timer_text = f"Time: {hours:02}:{minutes:02}:{seconds:02}"

            self.all_sprites.update()
            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)

            # Update score and pellet count
            collected_pellets = pygame.sprite.spritecollide(self.player, self.pellets, True)
            if collected_pellets:
                self.pellet_count -= len(collected_pellets)
                self.score += len(collected_pellets) * 100  # Add collected pellets to score
                print(f"Collected pellets: {len(collected_pellets)}, Remaining pellets: {self.pellet_count}")
                print(f"Score: {self.score}")

            # Display the score on the screen
            font = pygame.font.Font(None, 36)
            self.draw_text(f"Score: {self.score}", font, WHITE, self.screen, SCREEN_WIDTH - 100, 30)
           
            # Display the timer below the score
            self.draw_text(timer_text, font, WHITE, self.screen, SCREEN_WIDTH - 100, 60)

            if self.pellet_count <= 0:
                elapsed_time = time.time() - self.start_time  # Calculate elapsed time
                result = self.game_over_screen('win', self.score, elapsed_time)
                return result == 'retry'

            if pygame.sprite.spritecollideany(self.player, self.enemies):
                elapsed_time = time.time() - self.start_time  # Calculate elapsed time
                current_time = time.time()
                # technically IFrames
                if current_time - self.last_collision_time >= self.collision_cooldown_duration:
                    self.score -= 500  # Deduct points on collision
                    self.last_collision_time = current_time  # Update last collision time

            pygame.display.flip()
            self.clock.tick(60)


# Run the game
if __name__ == "__main__":
    game = Game()
    game.intro_screen()
    while game.game_loop():
        game.init_game()
