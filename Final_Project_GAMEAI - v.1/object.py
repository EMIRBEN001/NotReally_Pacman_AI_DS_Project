import pygame
from config import *
from collections import deque
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/packman.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))
        
        # Initialize attributes
        self.direction = (0, 0)  # Initialize direction (dx, dy)
        self.tile_x = x
        self.tile_y = y
        self.rect.topleft = (self.tile_x * TILESIZE, self.tile_y * TILESIZE)
        self.moving = False
        self.target_x = self.tile_x * TILESIZE
        self.target_y = self.tile_y * TILESIZE
        self.collected_pellets = 0  # Track collected pellets

    def move(self, dx, dy):
        if not self.moving:  # Only move if not already moving
            new_tile_x = self.tile_x + dx
            new_tile_y = self.tile_y + dy
            self.moving = True
            self.direction = (dx, dy)  # Update direction
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



class Blinky(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/blinky.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))  # Scale enemy to TILESIZE
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

        # Movement attributes
        self.is_moving = False  # Whether the enemy is currently moving
        self.move_delay = 1000 // PLAYER_SPEED  # Movement delay based on player's speed
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile the enemy is moving towards
        self.speed = 2  # Set the speed for smooth movement (adjust this as needed)
        self.path = []  # Initialize path attribute

    def move(self):
        current_time = pygame.time.get_ticks()

        if self.target_tile and self.is_moving:  # Smoothly move towards the target tile
            target_x, target_y = self.target_tile[0] * TILESIZE, self.target_tile[1] * TILESIZE
            dx, dy = target_x - self.rect.x, target_y - self.rect.y

            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                # Normalize the movement vector (dx, dy) and multiply by speed
                step_x = (dx / distance) * self.speed
                step_y = (dy / distance) * self.speed
                self.rect.x += step_x
                self.rect.y += step_y

            # Check if the enemy reached the target tile
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.rect.x, self.rect.y = target_x, target_y  # Snap to the exact position
                self.is_moving = False  # Stop moving once the target is reached

        elif current_time - self.last_move_time > self.move_delay:  # Check if it's time to move to the next tile
            if self.path and not self.is_moving:  # If a path exists and the enemy is not moving
                next_tile = self.path.pop(0)  # Get the next tile in the path
                self.start_moving(next_tile)
                self.last_move_time = current_time  # Update the last move time

    def can_move_to(self, x, y, tilemap):
        if x < 0 or x >= len(tilemap[0]) or y < 0 or y >= len(tilemap):
            return False  # Out of bounds
        if tilemap[y][x] == 'W':  # Wall tiles are not walkable
            return False
        return True

    def bfs(self, start, goal, tilemap):
        queue = deque([start])
        visited = set([start])
        paths = {start: []}  # Store the path to each tile

        while queue:
            current = queue.popleft()
            if current == goal:
                return paths[current]

            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) not in visited and self.can_move_to(new_x, new_y, tilemap):
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))
                    paths[(new_x, new_y)] = paths[current] + [(new_x, new_y)]

        return []
    
    def dfs(self, start, goal, tilemap): ### for now this DFS method isnt used yet
        stack = [(start, [])]  # Use a stack instead of a queue
        visited = set()
        visited.add(start)

        while stack:
            current, path = stack.pop()  # Get the current position and the path taken to reach it
            if current == goal:
                return path  # Return the path to the goal
            
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left movements
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                
                if new_pos not in visited and self.can_move_to(new_x, new_y, tilemap):
                    visited.add(new_pos)
                    stack.append((new_pos, path + [new_pos]))  # Add the new position and updated path to the stack

        return []  # Return empty path if no valid path is found

    def start_moving(self, next_tile):
        self.target_tile = next_tile  # Set the target tile
        self.is_moving = True  # Start moving towards the target tile

    def update(self):
        self.move()  # Call move in the update method

class Pinky(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/pinky.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))  # Scale enemy to TILESIZE
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

        # Movement attributes
        self.is_moving = False  # Whether the enemy is currently moving
        self.move_delay = 1000 // PLAYER_SPEED  # Movement delay based on player's speed
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile the enemy is moving towards
        self.speed = 2  # Set the speed for smooth movement (adjust this as needed)
        self.path = []  # Initialize path attribute

    def move(self):
        current_time = pygame.time.get_ticks()

        if self.target_tile and self.is_moving:  # Smoothly move towards the target tile
            target_x, target_y = self.target_tile[0] * TILESIZE, self.target_tile[1] * TILESIZE
            dx, dy = target_x - self.rect.x, target_y - self.rect.y

            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                # Normalize the movement vector (dx, dy) and multiply by speed
                step_x = (dx / distance) * self.speed
                step_y = (dy / distance) * self.speed
                self.rect.x += step_x
                self.rect.y += step_y

            # Check if the enemy reached the target tile
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.rect.x, self.rect.y = target_x, target_y  # Snap to the exact position
                self.is_moving = False  # Stop moving once the target is reached

        elif current_time - self.last_move_time > self.move_delay:  # Check if it's time to move to the next tile
            if self.path and not self.is_moving:  # If a path exists and the enemy is not moving
                next_tile = self.path.pop(0)  # Get the next tile in the path
                self.start_moving(next_tile)
                self.last_move_time = current_time  # Update the last move time

    def can_move_to(self, x, y, tilemap):
        if x < 0 or x >= len(tilemap[0]) or y < 0 or y >= len(tilemap):
            return False  # Out of bounds
        if tilemap[y][x] == 'W':  # Wall tiles are not walkable
            return False
        return True

    def bfs(self, start, goal, tilemap):
        queue = deque([start])
        visited = set([start])
        paths = {start: []}  # Store the path to each tile

        while queue:
            current = queue.popleft()
            if current == goal:
                return paths[current]

            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) not in visited and self.can_move_to(new_x, new_y, tilemap):
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))
                    paths[(new_x, new_y)] = paths[current] + [(new_x, new_y)]

        return []
    
    def dfs(self, start, goal, tilemap): ### for now this DFS method isnt used yet
        stack = [(start, [])]  # Use a stack instead of a queue
        visited = set()
        visited.add(start)

        while stack:
            current, path = stack.pop()  # Get the current position and the path taken to reach it
            if current == goal:
                return path  # Return the path to the goal
            
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left movements
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                
                if new_pos not in visited and self.can_move_to(new_x, new_y, tilemap):
                    visited.add(new_pos)
                    stack.append((new_pos, path + [new_pos]))  # Add the new position and updated path to the stack

        return []  # Return empty path if no valid path is found

    def start_moving(self, next_tile):
        self.target_tile = next_tile  # Set the target tile
        self.is_moving = True  # Start moving towards the target tile

    def update(self):
        self.move()  # Call move in the update method


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
        super().__init__()  # Not adding to any sprite group here
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)  # Color for the ground
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))

    def update(self):
        pass  # No update needed for ground tiles
