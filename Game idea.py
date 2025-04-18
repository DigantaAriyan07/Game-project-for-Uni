import pygame
import sys
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Base sizes (for 1280x720 resolution)
BASE_PREDATOR_SIZE = 50
BASE_PLAYER_SIZE = BASE_PREDATOR_SIZE
BASE_TREE_SIZE = 80
BASE_ROCK_SIZE = 60
BASE_DOOR_WIDTH = 40
BASE_DOOR_HEIGHT = 60
BASE_SHADOW_EXTENSION = 20
BASE_TILE_SIZE = 64
BASE_PREDATOR_SPEED = 1
BASE_PLAYER_SPEED = 3
BASE_DETECTION_RADIUS = 150

# Animation settings
ANIMATION_SPEED = 0.1  # Time between frame changes in seconds
SPRITE_SHEET_WIDTH = 11  # Number of frames in the sprite sheet
SPRITE_SHEET_HEIGHT = 1  # Number of rows in the sprite sheet

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
SHADOW_COLOR = (20, 20, 20, 128)
PURPLE = (128, 0, 128)  # Add purple color

# Game settings
FONT_SIZE = 48
SAFE_SPAWN_RADIUS = 150
PLAYER_SPAWN_TRIES = 100

# Level settings
MAX_LEVELS = 4
LEVEL_SETTINGS = {
    1: {"predators": 2, "speed_multiplier": 1.0},
    2: {"predators": 3, "speed_multiplier": 2.0},
    3: {"predators": 4, "speed_multiplier": 2.5},
    4: {"predators": 5, "speed_multiplier": 3.0}
}

# Add this constant after other constants
MIN_OBJECT_DISTANCE = 200  # Increased minimum distance between objects

# Add these constants after other constants
COUNTDOWN_TIME = 2  # seconds
BLINK_INTERVAL = 0.2  # seconds for blinking effect

# Background tile settings
try:
    BACKGROUND_IMAGE = pygame.image.load("grass.png")
    # Scale the image to TILE_SIZE
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (BASE_TILE_SIZE, BASE_TILE_SIZE))
except:
    print("Warning: Could not load grass.png. Using default background color.")
    BACKGROUND_IMAGE = None

# Load tree image
try:
    TREE_IMAGE = pygame.image.load("tree.png")
    # Scale the image to TREE_SIZE
    TREE_IMAGE = pygame.transform.scale(TREE_IMAGE, (BASE_TREE_SIZE, BASE_TREE_SIZE))
except:
    print("Warning: Could not load tree.png. Using default green rectangle.")
    TREE_IMAGE = None

# Load stone image
try:
    STONE_IMAGE = pygame.image.load("stone.png")
    # Scale the image to ROCK_SIZE
    STONE_IMAGE = pygame.transform.scale(STONE_IMAGE, (BASE_ROCK_SIZE, BASE_ROCK_SIZE))
except:
    print("Warning: Could not load stone.png. Using default gray rectangle.")
    STONE_IMAGE = None

# Load player sprite sheet
try:
    PLAYER_SPRITE_SHEET = pygame.image.load("idle.png")
    # Get the exact frame size from the sprite sheet
    FRAME_WIDTH = PLAYER_SPRITE_SHEET.get_width() // SPRITE_SHEET_WIDTH
    FRAME_HEIGHT = PLAYER_SPRITE_SHEET.get_height() // SPRITE_SHEET_HEIGHT
    # Scale the frame size to match player size
    PLAYER_FRAME_WIDTH = BASE_PLAYER_SIZE
    PLAYER_FRAME_HEIGHT = BASE_PLAYER_SIZE
except:
    print("Warning: Could not load idle.png. Using default purple square.")
    PLAYER_SPRITE_SHEET = None

# Load predator sprite sheet
try:
    PREDATOR_SPRITE_SHEET = pygame.image.load("villain.png")
    # Get the exact frame size from the sprite sheet
    PREDATOR_FRAME_WIDTH = PREDATOR_SPRITE_SHEET.get_width() // SPRITE_SHEET_WIDTH
    PREDATOR_FRAME_HEIGHT = PREDATOR_SPRITE_SHEET.get_height() // SPRITE_SHEET_HEIGHT
except:
    print("Warning: Could not load villain.png. Using default red square.")
    PREDATOR_SPRITE_SHEET = None

def get_scaled_sizes(screen_width, screen_height):
    """Calculate scaled sizes based on screen dimensions"""
    # Calculate scaling factors
    width_scale = screen_width / WINDOW_WIDTH
    height_scale = screen_height / WINDOW_HEIGHT
    scale_factor = min(width_scale, height_scale)  # Use smaller scale to maintain proportions
    
    # Calculate scaled sizes
    return {
        'PREDATOR_SIZE': int(BASE_PREDATOR_SIZE * scale_factor),
        'PLAYER_SIZE': int(BASE_PLAYER_SIZE * scale_factor),
        'TREE_SIZE': int(BASE_TREE_SIZE * scale_factor),
        'ROCK_SIZE': int(BASE_ROCK_SIZE * scale_factor),
        'DOOR_WIDTH': int(BASE_DOOR_WIDTH * scale_factor),
        'DOOR_HEIGHT': int(BASE_DOOR_HEIGHT * scale_factor),
        'SHADOW_EXTENSION': int(BASE_SHADOW_EXTENSION * scale_factor),
        'TILE_SIZE': int(BASE_TILE_SIZE * scale_factor),
        'PLAYER_SPEED': int(BASE_PLAYER_SPEED * scale_factor),
        'PREDATOR_SPEED': int(BASE_PREDATOR_SPEED * scale_factor),
        'DETECTION_RADIUS': int(BASE_DETECTION_RADIUS * scale_factor)
    }

def create_background_tiles():
    """Create a surface with tiled background pattern"""
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    if BACKGROUND_IMAGE:
        # Calculate how many tiles we need in each direction
        tiles_x = WINDOW_WIDTH // BASE_TILE_SIZE + 1
        tiles_y = WINDOW_HEIGHT // BASE_TILE_SIZE + 1
        
        # Draw tiles
        for x in range(tiles_x):
            for y in range(tiles_y):
                background.blit(BACKGROUND_IMAGE, (x * BASE_TILE_SIZE, y * BASE_TILE_SIZE))
    else:
        background.fill((34, 139, 34))  # Fallback to forest green background
    
    return background

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.shadow = pygame.Rect(x - BASE_SHADOW_EXTENSION, 
                                y + height,
                                width + BASE_SHADOW_EXTENSION * 2,
                                BASE_SHADOW_EXTENSION * 2)

class Tree(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, BASE_TREE_SIZE, BASE_TREE_SIZE, DARK_GREEN)
        if TREE_IMAGE:
            self.image = TREE_IMAGE.copy()  # Create a copy to avoid modifying the original

class Rock(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, BASE_ROCK_SIZE, BASE_ROCK_SIZE, GRAY)
        if STONE_IMAGE:
            self.image = STONE_IMAGE.copy()  # Create a copy to avoid modifying the original

class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, forest_objects=None):
        super().__init__()
        self.image = pygame.Surface([BASE_DOOR_WIDTH, BASE_DOOR_HEIGHT])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        
        # Try different positions until we find one that doesn't collide
        while True:
            # Randomly choose a side
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                self.rect.x = 0
                self.rect.centery = random.randint(BASE_DOOR_HEIGHT, WINDOW_HEIGHT - BASE_DOOR_HEIGHT)
            elif side == 'right':
                self.rect.right = WINDOW_WIDTH
                self.rect.centery = random.randint(BASE_DOOR_HEIGHT, WINDOW_HEIGHT - BASE_DOOR_HEIGHT)
            elif side == 'top':
                self.rect.y = 0
                self.rect.centerx = random.randint(BASE_DOOR_WIDTH, WINDOW_WIDTH - BASE_DOOR_WIDTH)
            else:  # bottom
                self.rect.bottom = WINDOW_HEIGHT
                self.rect.centerx = random.randint(BASE_DOOR_WIDTH, WINDOW_WIDTH - BASE_DOOR_WIDTH)
            
            # If no forest objects provided or no collision with forest objects, break the loop
            if forest_objects is None or not pygame.sprite.spritecollideany(self, forest_objects):
                break

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if PLAYER_SPRITE_SHEET:
            # Create a list to store all frames
            self.frames = []
            # Extract frames from sprite sheet
            for i in range(SPRITE_SHEET_WIDTH):
                frame = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
                frame.blit(PLAYER_SPRITE_SHEET, (0, 0), 
                          (i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
                frame = pygame.transform.scale(frame, (BASE_PLAYER_SIZE, BASE_PLAYER_SIZE))
                self.frames.append(frame)
            
            # Set initial frame
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.animation_time = 0
            self.animation_speed = ANIMATION_SPEED
            self.facing_right = True  # Track which direction the player is facing
        else:
            self.image = pygame.Surface([BASE_PLAYER_SIZE, BASE_PLAYER_SIZE])
            self.image.fill(PURPLE)
            self.frames = []
            self.current_frame = 0
            self.animation_time = 0
            self.animation_speed = 0
            self.facing_right = True
        
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = BASE_PLAYER_SPEED
    
    def update(self):
        # Update animation
        if self.frames:
            self.animation_time += 1/FPS
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                # Flip the image based on direction
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
        
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            # Flip the image when changing direction
            if self.frames:
                self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            # Reset the image to original direction
            if self.frames:
                self.image = self.frames[self.current_frame]
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        # Keep player in bounds
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

def create_forest_objects():
    objects = pygame.sprite.Group()
    shadow_areas = []
    
    def is_valid_position(x, y, size, existing_objects):
        """Check if a position is valid (not too close to other objects)"""
        test_rect = pygame.Rect(x - size//2, y - size//2, size, size)
        for obj in existing_objects:
            # Calculate distance between centers
            obj_center = obj.rect.center
            test_center = test_rect.center
            distance = ((obj_center[0] - test_center[0])**2 + 
                       (obj_center[1] - test_center[1])**2)**0.5
            
            # Add extra padding for trees
            if isinstance(obj, Tree):
                min_distance = MIN_OBJECT_DISTANCE + 50  # Extra space for trees
            else:
                min_distance = MIN_OBJECT_DISTANCE
            
            # Check if distance is less than minimum required
            if distance < min_distance:
                return False
        return True
    
    # Create 5 trees
    for _ in range(5):
        attempts = 0
        while attempts < PLAYER_SPAWN_TRIES:
            x = random.randint(BASE_TREE_SIZE, WINDOW_WIDTH - BASE_TREE_SIZE)
            y = random.randint(BASE_TREE_SIZE, WINDOW_HEIGHT - BASE_TREE_SIZE)
            
            if is_valid_position(x, y, BASE_TREE_SIZE, objects):
                tree = Tree(x, y)
                objects.add(tree)
                shadow_areas.append(tree.shadow)
                break
            attempts += 1
    
    # Create 4 rocks
    for _ in range(4):
        attempts = 0
        while attempts < PLAYER_SPAWN_TRIES:
            x = random.randint(BASE_ROCK_SIZE, WINDOW_WIDTH - BASE_ROCK_SIZE)
            y = random.randint(BASE_ROCK_SIZE, WINDOW_HEIGHT - BASE_ROCK_SIZE)
            
            if is_valid_position(x, y, BASE_ROCK_SIZE, objects):
                rock = Rock(x, y)
                objects.add(rock)
                shadow_areas.append(rock.shadow)
                break
            attempts += 1
    
    return objects, shadow_areas

def is_in_shadow(sprite, shadow_areas):
    return any(shadow.colliderect(sprite.rect) for shadow in shadow_areas)

class Predator(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_multiplier):
        super().__init__()
        if PREDATOR_SPRITE_SHEET:
            # Create a list to store all frames
            self.frames = []
            # Extract frames from sprite sheet
            for i in range(SPRITE_SHEET_WIDTH):
                frame = pygame.Surface((PREDATOR_FRAME_WIDTH, PREDATOR_FRAME_HEIGHT), pygame.SRCALPHA)
                frame.blit(PREDATOR_SPRITE_SHEET, (0, 0), 
                          (i * PREDATOR_FRAME_WIDTH, 0, PREDATOR_FRAME_WIDTH, PREDATOR_FRAME_HEIGHT))
                # Scale the frame to the new size
                frame = pygame.transform.scale(frame, (BASE_PREDATOR_SIZE, BASE_PREDATOR_SIZE))
                self.frames.append(frame)
            
            # Set initial frame
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.animation_time = 0
            self.animation_speed = ANIMATION_SPEED
            self.facing_right = True  # Track which direction the predator is facing
        else:
            self.image = pygame.Surface([BASE_PREDATOR_SIZE, BASE_PREDATOR_SIZE])
            self.image.fill(RED)
            self.frames = []
            self.current_frame = 0
            self.animation_time = 0
            self.animation_speed = 0
            self.facing_right = True
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = pygame.math.Vector2(1, 0)
        self.speed = BASE_PREDATOR_SPEED * speed_multiplier
    
    def update(self, player):
        # Update animation
        if self.frames:
            self.animation_time += 1/FPS
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                # Flip the image based on direction
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
        
        if player:  # If player is visible
            direction = pygame.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            if direction.length() > 0:  # Avoid division by zero
                direction = direction.normalize()
                # Update facing direction based on movement
                self.facing_right = direction.x > 0
                # Flip the image if needed
                if self.frames and not self.facing_right:
                    self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
                elif self.frames and self.facing_right:
                    self.image = self.frames[self.current_frame]
                
                self.rect.x += direction.x * self.speed
                self.rect.y += direction.y * self.speed
        else:  # Random patrol
            if random.random() < 0.02:  # 2% chance to change direction
                self.direction.rotate_ip(random.choice([90, -90]))
                # Update facing direction based on new patrol direction
                self.facing_right = self.direction.x > 0
                # Flip the image if needed
                if self.frames and not self.facing_right:
                    self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
                elif self.frames and self.facing_right:
                    self.image = self.frames[self.current_frame]
            
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            
        # Keep predator in bounds
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

def show_pause_menu(screen, screen_width, screen_height, font):
    """Shows a pause menu with continue/exit options and returns True for continue, False for exit"""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Menu options
    options = ["Continue Game", "Exit Game"]
    selected_option = 0
    
    while True:
        # Draw menu options
        for i, option in enumerate(options):
            color = WHITE if i == selected_option else GRAY
            text = font.render(option, True, color)
            rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 50 + i * 100))
            screen.blit(text, rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Continue game
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:  # Enter key
                    return selected_option == 0  # True for continue, False for exit

def main():
    # Initialize screen with fixed size
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Forest Predator")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)
    
    # Create background surface with tiles
    background_surface = create_background_tiles()
    
    # Add window state tracking
    is_maximized = False

    def draw_background():
        screen.blit(background_surface, (0, 0))

    def toggle_maximize():
        nonlocal is_maximized, screen
        is_maximized = not is_maximized
        if is_maximized:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def show_options_screen(title_text):
        """Shows a screen with restart/exit options and returns True for restart, False for exit"""
        screen.fill(BLACK)
        title = font.render(title_text, True, WHITE)
        restart_text = font.render("Press ENTER to play again", True, WHITE)
        exit_text = font.render("Press SPACE to exit", True, WHITE)
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
        
        screen.blit(title, title_rect)
        screen.blit(restart_text, restart_rect)
        screen.blit(exit_text, exit_rect)
        
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Enter key
                        return True  # Restart game
                    elif event.key == pygame.K_SPACE:  # Space key
                        return False  # Exit game
            pygame.display.flip()
            clock.tick(FPS)
        return False

    def start_countdown(screen, all_sprites, player, predators, forest_objects, shadow_areas, level_text):
        """Run a 2-second countdown with blinking sprites"""
        start_time = pygame.time.get_ticks()
        last_blink = 0
        show_sprites = True
        
        while (pygame.time.get_ticks() - start_time) < COUNTDOWN_TIME * 1000:  # Convert to milliseconds
            current_time = pygame.time.get_ticks()
            
            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            
            # Blink effect
            if current_time - last_blink >= BLINK_INTERVAL * 1000:
                show_sprites = not show_sprites
                last_blink = current_time
            
            # Draw background and game state
            draw_background()
            
            # Draw shadows
            shadow_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            for shadow in shadow_areas:
                pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow)
            screen.blit(shadow_surface, (0, 0))
            
            # Draw forest objects
            forest_objects.draw(screen)
            
            # Draw sprites (blinking)
            if show_sprites:
                # Draw player and predators
                screen.blit(player.image, player.rect)
                for predator in predators:
                    screen.blit(predator.image, predator.rect)
            
            # Draw level text
            screen.blit(level_text, level_text.get_rect(center=(WINDOW_WIDTH // 2, 50)))
            
            pygame.display.flip()
            clock.tick(FPS)
        
        return True

    def start_game():
        current_level = 1
        game_over = False
        
        while current_level <= MAX_LEVELS and not game_over:
            # Create forest objects
            forest_objects, shadow_areas = create_forest_objects()
            
            # Create sprite groups
            all_sprites = pygame.sprite.Group()
            predators = pygame.sprite.Group()
            
            # Find a safe spawn location for player
            def get_safe_spawn_location(exit_door):
                max_distance = 0
                best_position = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                
                # Try multiple positions to find the farthest one from the exit
                for _ in range(PLAYER_SPAWN_TRIES):
                    x = random.randint(BASE_PLAYER_SIZE, WINDOW_WIDTH - BASE_PLAYER_SIZE)
                    y = random.randint(BASE_PLAYER_SIZE, WINDOW_HEIGHT - BASE_PLAYER_SIZE)
                    test_rect = pygame.Rect(x - BASE_PLAYER_SIZE//2, y - BASE_PLAYER_SIZE//2, 
                                          BASE_PLAYER_SIZE, BASE_PLAYER_SIZE)
                    
                    # Check if position is clear of objects
                    clear_of_objects = not any(test_rect.colliderect(obj.rect) 
                                             for obj in forest_objects)
                    
                    if clear_of_objects:
                        # Calculate distance to exit door
                        distance = ((x - exit_door.rect.centerx) ** 2 + 
                                  (y - exit_door.rect.centery) ** 2) ** 0.5
                        
                        # Update best position if this is farther
                        if distance > max_distance:
                            max_distance = distance
                            best_position = (x, y)
                
                return best_position

            # Add exit door first (before player)
            exit_door = ExitDoor(forest_objects)
            all_sprites.add(exit_door)

            # Create and position player at farthest point from exit
            player = Player()
            safe_x, safe_y = get_safe_spawn_location(exit_door)
            player.rect.center = (safe_x, safe_y)
            all_sprites.add(player)

            # Add predators based on current level
            level_settings = LEVEL_SETTINGS[current_level]
            for _ in range(level_settings["predators"]):
                for _ in range(PLAYER_SPAWN_TRIES):
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(0, WINDOW_HEIGHT)
                    
                    distance = ((x - player.rect.centerx) ** 2 + 
                               (y - player.rect.centery) ** 2) ** 0.5
                    
                    if distance >= SAFE_SPAWN_RADIUS:
                        predator = Predator(x, y, level_settings["speed_multiplier"])
                        if not pygame.sprite.spritecollide(predator, forest_objects, False):
                            predators.add(predator)
                            all_sprites.add(predator)
                            break
            
            # Level-specific variables
            level_complete = False
            level_text = font.render(f"Level {current_level}", True, WHITE)
            level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            
            # Start countdown before level begins
            if not start_countdown(screen, all_sprites, player, predators, forest_objects, shadow_areas, level_text):
                return False  # Exit if player quits during countdown
            
            # Level loop
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False  # Exit game
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Show pause menu
                            if not show_pause_menu(screen, WINDOW_WIDTH, WINDOW_HEIGHT, font):
                                return False  # Exit game
                        elif event.key == pygame.K_F11:  # Add F11 key handler
                            toggle_maximize()
                        elif level_complete and event.key == pygame.K_RETURN:
                            running = False
                
                if not level_complete:
                    # Update game objects
                    old_pos = player.rect.copy()
                    player.update()
                    if pygame.sprite.spritecollide(player, forest_objects, False):
                        player.rect = old_pos
                        
                    for predator in predators:
                        old_pos = predator.rect.copy()
                        if not is_in_shadow(player, shadow_areas):
                            predator.update(player)
                        else:
                            predator.update(None)
                        if pygame.sprite.spritecollide(predator, forest_objects, False):
                            predator.rect = old_pos
                    
                    # Check collisions
                    if pygame.sprite.spritecollide(player, predators, False):
                        # Only die if not in shadow
                        if not is_in_shadow(player, shadow_areas):
                            game_over = True
                            running = False
                    
                    if pygame.sprite.collide_rect(player, exit_door):
                        level_complete = True
                    
                    # Draw game
                    draw_background()
                    
                    shadow_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    for shadow in shadow_areas:
                        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow)
                    screen.blit(shadow_surface, (0, 0))
                    
                    forest_objects.draw(screen)
                    all_sprites.draw(screen)
                    screen.blit(level_text, level_rect)
                    pygame.display.flip()
                else:
                    # Draw level complete screen
                    screen.fill(BLACK)
                    if current_level < MAX_LEVELS:
                        complete_text = font.render(f"Level {current_level} Complete!", True, WHITE)
                        continue_text = font.render("Press any key to continue", True, WHITE)
                        complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
                        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
                        screen.blit(complete_text, complete_rect)
                        screen.blit(continue_text, continue_rect)
                        pygame.display.flip()
                    else:
                        # Game completion screen
                        return show_options_screen("Congratulations! You've completed all levels!")
                
                clock.tick(FPS)
            
            if not game_over:
                current_level += 1
        
        if game_over:
            return show_options_screen("Game Over!")
        
        return False  # Exit game
    
    # Main game loop that handles restarts
    while start_game():
        pass  # Continue playing if the game returns True (restart)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 