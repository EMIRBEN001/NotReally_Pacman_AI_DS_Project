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
                elif tile == 'L' and self.difficulty in ['medium' ,'hard', 'very_hard']:
                    self.pinky = Pinky(self, col_index, row_index)  # Pink Ghost Enemy
                    self.enemies.add(self.pinky)
                elif tile == 'I' and self.difficulty in ['hard', 'very_hard']:
                    self.inky = Inky(self, col_index, row_index)  # Cyan Ghost Enemy
                    self.enemies.add(self.inky)
                elif tile == 'C' and self.difficulty == 'very_hard':
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

        
    # Intro Screen with Difficulty Options
    def intro_screen(self):
        font = pygame.font.Font(None, 74)
        message_font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 36)
        
        # Create buttons for Easy and Hard modes
        easy_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, 'Easy', button_font, GREEN, BLACK)
        medium_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 50, 'Medium', button_font, YELLOW, BLACK)
        hard_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 190, 200, 50, 'Hard', button_font, RED, BLACK)
        very_hard_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 260, 200, 50, 'Very Hard', button_font, DARK_RED, BLACK)
        
        while True:
            self.screen.fill(BLACK)
            
            # Draw game title
            self.draw_text("PACK-GUY", font, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
            self.draw_text("Please choose the difficulty of the game!",message_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

            # Draw difficulty selection buttons
            easy_button.draw(self.screen)
            hard_button.draw(self.screen)
            medium_button.draw(self.screen)
            very_hard_button.draw(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if easy_button.is_clicked(event.pos):
                            self.difficulty = 'easy'  # Set difficulty to easy
                            return 'intro'  # Proceed to game
                        elif medium_button.is_clicked(event.pos):
                            self.difficulty = 'medium'  # Set difficulty to medium
                            return 'intro'  # Proceed to game
                        elif hard_button.is_clicked(event.pos):
                            self.difficulty = 'hard'  # Set difficulty to hard
                            return 'intro'  # Proceed to game
                        elif very_hard_button.is_clicked(event.pos):
                            self.difficulty = 'very_hard'  # Set difficulty to very hard
                            return 'intro'  # Proceed to game
                        
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            print("Easy selected with Click + 1!")
                            self.difficulty = 'easy'
                            return 'intro'
                        elif event.key == pygame.K_2:
                            print("Medium selected with Click + 2!")
                            self.difficulty = 'medium'
                            return 'intro'
                        elif event.key == pygame.K_3: 
                            print("Hard selected with Click + 3!")
                            self.difficulty = 'hard'
                            return 'intro'
                        elif event.key == pygame.K_4:
                            print("Very Hard selected with Click + 4!")
                            self.difficulty = 'very_hard'
                            return 'intro'

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

        # Define the back button rectangle
        back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 100, 40)

        while True:
            self.screen.fill(BLACK)
            self.all_sprites.update()  # Update all sprites
            
            self.all_sprites.draw(self.screen)  # Draw all sprites
            self.draw_text(f"Score: {self.score}", pygame.font.Font(None, 36), WHITE, self.screen, SCREEN_WIDTH // 2, 20)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and back_button.collidepoint(event.pos):
                        return False # Exit the game loop and return to intro screen
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    return False
                    

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

            # Call each enemy's move method if they exist
            if hasattr(self, 'blinky'):  # Check if Blinky exists
                self.blinky.move()
            if hasattr(self, 'pinky'):  # Check if Pinky exists (only in Hard mode)
                self.pinky.move()
            if hasattr(self, 'inky'):  # Check if Inky exists (only in Hard mode)
                self.inky.move()
            if hasattr(self, 'clyde'):  # Check if Clyde exists (only in Hard mode)
                self.clyde.move()

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
            self.draw_text(timer_text, font, WHITE, self.screen, SCREEN_WIDTH - 100, 60)

             # Draw the back button
            pygame.draw.rect(self.screen, WHITE, back_button)
            self.draw_text("Back", font, BLACK, self.screen, back_button.centerx, back_button.centery)

            if self.pellet_count <= 0:
                elapsed_time = time.time() - self.start_time  # Calculate elapsed time
                result = self.game_over_screen('win', self.score, elapsed_time)
                return result == 'retry'

            if pygame.sprite.spritecollideany(self.player, self.enemies):
                elapsed_time = time.time() - self.start_time  # Calculate elapsed time
                current_time = time.time()
                # technically IFrames
                if current_time - self.last_collision_time >=  self.collision_cooldown_duration:
                    self.score -= 500  # Deduct points on collision
                    self.last_collision_time = current_time  # Update last collision time

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    while True:
        result = game.intro_screen()
        if result == 'intro':  # You can check this label to perform actions if needed
            if game.game_loop():
                game.init_game()
