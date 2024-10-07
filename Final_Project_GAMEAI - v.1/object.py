import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()

        # Set initial position
        self.tile_x = x
        self.tile_y = y
        self.rect.topleft = (self.tile_x * TILESIZE, self.tile_y * TILESIZE)

        # Movement control
        self.moving = False
        self.target_x = self.tile_x * TILESIZE
        self.target_y = self.tile_y * TILESIZE
        self.collected_pellets = 0 # Track Collected Pellets

    def move(self, dx, dy):
        if not self.moving:  # Only move if not already moving
            new_tile_x = self.tile_x + dx
            new_tile_y = self.tile_y + dy
            self.moving = True
            self.target_x = self.tile_x * TILESIZE
            self.target_y = self.tile_y * TILESIZE

            # Create a rect for the next position
            new_rect = pygame.Rect(new_tile_x * TILESIZE, new_tile_y * TILESIZE, TILESIZE, TILESIZE)

            # Check for collisions with blocks
            if not any(new_rect.colliderect(block.rect) for block in self.game.blocks):
                # No collision, move to the new tile
                self.tile_x = new_tile_x
                self.tile_y = new_tile_y
                self.target_x = self.tile_x * TILESIZE
                self.target_y = self.tile_y * TILESIZE

            # Handle teleporters
            if tilemap[self.tile_y][self.tile_x] == 'T':
                self.teleport()

    def teleport(self):
        # Teleport logic: Move to the corresponding teleporter
        if (self.tile_x, self.tile_y) == (20, 9):  # Right teleporter
            self.tile_x, self.tile_y = 0, 9  # Move to left teleporter
        elif (self.tile_x, self.tile_y) == (0, 9):  # Left teleporter
            self.tile_x, self.tile_y = 20, 9  # Move to right teleporter

        # Update the rect position immediately to the new tile position
        self.rect.topleft = (self.tile_x * TILESIZE, self.tile_y * TILESIZE)
        self.moving = False  # Set moving to false immediately after teleportation

    def update(self):
        if self.moving:
            # Move towards the target tile
            if self.rect.x < self.target_x:
                self.rect.x += PLAYER_SPEED
            elif self.rect.x > self.target_x:
                self.rect.x -= PLAYER_SPEED
            elif self.rect.y < self.target_y:
                self.rect.y += PLAYER_SPEED
            elif self.rect.y > self.target_y:
                self.rect.y -= PLAYER_SPEED

            # Stop moving once the player reaches the target position
            if self.rect.x == self.target_x and self.rect.y == self.target_y:
                self.moving = False  # Stop moving when tile is reached



class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/enemy.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))  # Scale player to TILESIZE
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

    def update(self):
        # Placeholder for future AI movement
        pass

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)  # Blue blocks
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

class Pellet(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.pellets
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((TILESIZE // 2, TILESIZE // 2))
        self.image.fill(WHITE)  # White pellets
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE + TILESIZE // 4
        self.y = y * TILESIZE + TILESIZE // 4
        self.rect.topleft = (self.x, self.y)

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.pellets
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((TILESIZE // 2, TILESIZE // 2))
        self.image.fill(BLACK)  # White pellets
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE + TILESIZE // 4
        self.y = y * TILESIZE + TILESIZE // 4
        self.rect.topleft = (self.x, self.y)
