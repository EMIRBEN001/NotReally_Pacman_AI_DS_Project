import pygame
from config import *
from collections import deque

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
        self.speed = PLAYER_SPEED      

        self.score = 0 # attribute for SCORES

    def move(self, dx, dy):
        if not self.moving:  # Only move if not already moving
            new_tile_x = self.tile_x + dx
            new_tile_y = self.tile_y + dy

            # Create a rect for the next position
            new_rect = pygame.Rect(new_tile_x * TILESIZE, new_tile_y * TILESIZE, TILESIZE, TILESIZE)

            # Check for collisions with blocks
            if any(new_rect.colliderect(block.rect) for block in self.game.blocks):
                return  # Stop the move if there is a collision

            # No collision, proceed with movement
            self.moving = True
            self.direction = (dx, dy)  # Update direction
            self.target_x = new_tile_x * TILESIZE
            self.target_y = new_tile_y * TILESIZE

            # Update tile position immediately
            self.tile_x = new_tile_x
            self.tile_y = new_tile_y

            # Handle teleporters
            if tilemap[self.tile_y][self.tile_x] == 'T':
                self.teleport()

            # Check if the current tile has a pellet
            if tilemap[self.tile_y][self.tile_x] == '.':
                self.eat_pellet()  # Eat the pellet and update the score

          
    def eat_pellet(self):
        pass

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
            # Calculate the distance to the target
            dx = self.target_x - self.rect.x
            dy = self.target_y - self.rect.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance != 0:  # Prevent division by zero
                # Normalize the direction vector and scale by speed
                step_x = (dx / distance) * self.speed
                step_y = (dy / distance) * self.speed

                # Move towards the target
                self.rect.x += step_x
                self.rect.y += step_y

                # Stop moving if close enough to the target
                if abs(dx) <= self.speed and abs(dy) <= self.speed:
                    self.rect.x, self.rect.y = self.target_x, self.target_y  # Snap to target position
                    self.moving = False  # Stop moving




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
        self.speed = GHOST_SPEED  # Set the speed for smooth movement (adjust this as needed)
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile the enemy is moving towards
        self.path = []  # Initialize path attribute

    def calculate_goal(self):
        """Directly target the player's current tile."""
        player = self.game.player
        goal_x, goal_y = player.tile_x, player.tile_y

        # Clamp the goal to the tilemap boundaries
        goal_x = max(0, min(len(tilemap[0]) - 1, goal_x))
        goal_y = max(0, min(len(tilemap) - 1, goal_y))

        return goal_x, goal_y

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

        elif current_time - self.last_move_time > self.speed:  # Check if it's time to move to the next tile
            if not self.is_moving:  # Only calculate path if not currently moving
                start = (self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                goal = self.calculate_goal()
                self.path = self.bfs(start, goal, tilemap)  # Find the path using BFS
                if self.path:  # If a valid path exists
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

        return []  # Return an empty list if no path is found

    def start_moving(self, next_tile):
        self.target_tile = next_tile  # Set the target tile
        self.is_moving = True  # Start moving towards the target tile


class Inky(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/inky.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))  # Scale enemy to TILESIZE
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

        # Movement attributes
        self.is_moving = False  # Whether the enemy is currently moving
        self.speed = GHOST_SPEED  # Set the speed for smooth movement (adjust this as needed)
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile the enemy is moving towards
        self.path = []  # Initialize path attribute

    def calculate_goal(self):
        """Calculate the goal tile for Inky based on player's position and offset."""
        player = self.game.player
        player_tile = (player.rect.x // TILESIZE, player.rect.y // TILESIZE)
        radius = 2  # Offset distance from player
        offset_x = radius if player.direction[0] >= 0 else -radius
        offset_y = radius if player.direction[1] >= 0 else -radius
        inky_goal_tile = (player_tile[0] + offset_x, player_tile[1] + offset_y)

        # Clamp the goal to the tilemap boundaries
        inky_goal_tile = (
            max(0, min(len(tilemap[0]) - 1, inky_goal_tile[0])),
            max(0, min(len(tilemap) - 1, inky_goal_tile[1]))
        )
        return inky_goal_tile

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

        elif current_time - self.last_move_time > self.speed:  # Check if it's time to move
            if not self.path:  # If no path exists, calculate it
                inky_goal_tile = self.calculate_goal()
                self.path = self.dfs((self.rect.x // TILESIZE, self.rect.y // TILESIZE), inky_goal_tile, tilemap)
            
            if self.path and not self.is_moving:  # If a path exists and not moving
                next_tile = self.path.pop(0)  # Get the next tile in the path
                self.start_moving(next_tile)
                self.last_move_time = current_time  # Update the last move time

    def can_move_to(self, x, y, tilemap):
        if x < 0 or x >= len(tilemap[0]) or y < 0 or y >= len(tilemap):
            return False  # Out of bounds
        if tilemap[y][x] == 'W':  # Wall tiles are not walkable
            return False
        return True

    def dfs(self, start, goal, tilemap):
        """DFS for pathfinding."""
        stack = [(start, [])]
        visited = set()

        while stack:
            current, path = stack.pop()
            if current == goal:
                return path

            if current not in visited:
                visited.add(current)
                x, y = current

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.can_move_to(new_x, new_y, tilemap):
                        stack.append(((new_x, new_y), path + [(new_x, new_y)]))

        return []  # Return empty path if no valid path is found

    def start_moving(self, next_tile):
        self.target_tile = next_tile
        self.is_moving = True

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
        self.speed = GHOST_SPEED  # Set the speed for smooth movement (adjust this as needed)
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile the enemy is moving towards
        self.path = []  # Initialize path attribute

    def calculate_goal(self):
        """Calculate the goal tile based on the player's position and direction."""
        player = self.game.player
        dx, dy = player.direction
        goal_x = player.tile_x + dx * 4
        goal_y = player.tile_y + dy * 4

        # Clamp the goal to the tilemap boundaries
        goal_x = max(0, min(len(tilemap[0]) - 1, goal_x))
        goal_y = max(0, min(len(tilemap) - 1, goal_y))

        return goal_x, goal_y

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

        elif current_time - self.last_move_time > self.speed:  # Check if it's time to move to the next tile
            if not self.is_moving:  # Only calculate path if not currently moving
                start = (self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                goal = self.calculate_goal()
                self.path = self.bfs(start, goal, tilemap)  # Find the path using BFS
                if self.path:  # If a valid path exists
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

    def start_moving(self, next_tile):
        self.target_tile = next_tile  # Set the target tile
        self.is_moving = True  # Start moving towards the target tile


class Clyde(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load('assets/clyde.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))  # Scale enemy to TILESIZE
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.topleft = (self.x, self.y)

        # Movement attributes
        self.is_moving = False  # Whether Clyde is currently moving
        self.speed = GHOST_SPEED  # Set the speed for smooth movement (adjust this as needed)
        self.last_move_time = pygame.time.get_ticks()  # Time of the last move

        self.target_tile = None  # Target tile Clyde is moving towards
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

            # Check if Clyde reached the target tile
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.rect.x, self.rect.y = target_x, target_y  # Snap to the exact position
                self.is_moving = False  # Stop moving once the target is reached

        elif current_time - self.last_move_time > self.speed:  # Check if it's time to move
            if not self.path:  # If no path exists, calculate it
                goal_tile = (self.game.player.rect.x // TILESIZE, self.game.player.rect.y // TILESIZE)
                start_tile = (self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                self.path = self.dfs(start_tile, goal_tile, tilemap)

            if self.path and not self.is_moving:  # If a path exists and Clyde is not moving
                next_tile = self.path.pop(0)  # Get the next tile in the path
                self.start_moving(next_tile)
                self.last_move_time = current_time  # Update the last move time

    def can_move_to(self, x, y, tilemap):
        if x < 0 or x >= len(tilemap[0]) or y < 0 or y >= len(tilemap):
            return False  # Out of bounds
        if tilemap[y][x] == 'W':  # Wall tiles are not walkable
            return False
        return True

    def dfs(self, start, goal, tilemap):
        """DFS for pathfinding."""
        stack = [(start, [])]
        visited = set()

        while stack:
            current, path = stack.pop()
            if current == goal:
                return path

            if current not in visited:
                visited.add(current)
                x, y = current

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if self.can_move_to(new_x, new_y, tilemap):
                        stack.append(((new_x, new_y), path + [(new_x, new_y)]))

        return []  # Return empty path if no valid path is found

    def start_moving(self, next_tile):
        self.target_tile = next_tile
        self.is_moving = True


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
    
class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_obj = self.font.render(self.text, True, self.text_color)
        text_rect = text_obj.get_rect(center=self.rect.center)
        surface.blit(text_obj, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
