import pygame
import math
import numpy as np
from ShotFinder import find_ideal_shot
from collections import OrderedDict

pygame.init()
pygame.font.init()

# Window settings
WIDTH, HEIGHT = 1302, 634
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FRC 2026 Shooting Simulator - REBUILT")

clock = pygame.time.Clock()

# Colors and settings
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 201, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# FRC parameters
ROBOT_HEIGHT = 0.51
HUB_HEIGHT = 2.5
HUB_RADIUS = 0.3
PIXELS_PER_METER = 100

# Try to load player image
try:
    player_image_original = pygame.image.load("images/Red_triangle.png").convert_alpha()
except:
    player_image_original = pygame.Surface((50, 50), pygame.SRCALPHA)
    points = [(25, 0), (0, 50), (50, 50)]
    pygame.draw.polygon(player_image_original, RED, points)

SPRITE_HEADING_OFFSET = -90

# Player settings
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_angle = 0
rotation_speed = 3

# Hexagon settings
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 94

# Cache for shot calculations
class ShotCache:
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, distance):
        # Round to 0.1m for cache hits
        key = round(distance, 1)
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, distance, angle, speed):
        key = round(distance, 1)
        self.cache[key] = (angle, speed)
        if len(self.cache) > self.max_size:
            # Remove oldest entry
            self.cache.popitem(last=False)

# Create cache
shot_cache = ShotCache()

def get_shot_parameters(distance_m):
    """Get shot parameters with caching."""
    if distance_m < 0.5:  # Too close
        return None, None
    
    # Check cache first
    cached = shot_cache.get(distance_m)
    if cached is not None:
        return cached
    
    # Calculate new values
    try:
        # Use faster grid search
        ideal_angle = find_ideal_shot(
            hs=ROBOT_HEIGHT,
            ht=HUB_HEIGHT,
            d=distance_m,
            hub_radius=HUB_RADIUS,
            v_max=15.0,  # Lower max speed for faster search
            theta_min_deg=30,
            theta_max_deg=80,
            descent_angle_max_deg=-10,
            min_angle_separation_deg=2,
            criterion="balanced",
            return_type="theta"
        )
        
        ideal_speed = find_ideal_shot(
            hs=ROBOT_HEIGHT,
            ht=HUB_HEIGHT,
            d=distance_m,
            hub_radius=HUB_RADIUS,
            v_max=15.0,
            theta_min_deg=30,
            theta_max_deg=80,
            descent_angle_max_deg=-10,
            min_angle_separation_deg=2,
            criterion="balanced",
            return_type="v"
        )
        
        # Cache the result
        shot_cache.set(distance_m, ideal_angle, ideal_speed)
        
        return ideal_angle, ideal_speed
    except Exception as e:
        print(f"Error calculating shot: {e}")
        return None, None

# Helper functions
def hexagon_points(center, radius):
    cx, cy = center
    return [(cx + radius * math.cos(math.radians(60 * i - 30)),
             cy + radius * math.sin(math.radians(60 * i - 30))) 
            for i in range(6)]

def get_rotated_image(image, angle, position):
    rotated = pygame.transform.rotate(image, angle + SPRITE_HEADING_OFFSET)
    rect = rotated.get_rect(center=position)
    return rotated, rect

def pixels_to_meters(pixels):
    return pixels / PIXELS_PER_METER

# Main loop
running = True
last_distance = 0
frame_counter = 0

# Initialize variables before the loop
ideal_angle = None
ideal_speed = None

while running:
    screen.fill((245, 245, 245))
    clock.tick(60)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Handle input
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]:
        player_pos.y -= player_speed
    if keys[pygame.K_s]:
        player_pos.y += player_speed
    if keys[pygame.K_a]:
        player_pos.x -= player_speed
    if keys[pygame.K_d]:
        player_pos.x += player_speed
    if keys[pygame.K_LEFT]:
        player_angle += rotation_speed
    if keys[pygame.K_RIGHT]:
        player_angle -= rotation_speed
    
    # Draw    
    # Draw hexagon (HUB)
    pygame.draw.polygon(screen, (7, 204, 168), hexagon_points(HEX_CENTER, HEX_RADIUS), 10)
    
    # Draw player
    rotated_image, rotated_rect = get_rotated_image(
        player_image_original, player_angle, player_pos
    )
    screen.blit(rotated_image, rotated_rect)
    
    # Calculate distance
    player_center = pygame.Vector2(rotated_rect.center)
    hex_center_vec = pygame.Vector2(HEX_CENTER)
    distance_px = hex_center_vec.distance_to(player_center)
    distance_m = pixels_to_meters(distance_px)
    
    # Only update shot parameters every 5 frames to reduce computation
    frame_counter += 1
    if frame_counter % 5 == 0 or abs(distance_m - last_distance) > 0.05:
        ideal_angle, ideal_speed = get_shot_parameters(distance_m)
        last_distance = distance_m
    
    # Draw line to hub
    pygame.draw.line(screen, GREEN, player_center, HEX_CENTER, 3)
    pygame.draw.circle(screen, GREEN, HEX_CENTER, 5)
    
    # Display text
    font = pygame.font.SysFont("Arial", 20, bold=True)
    
    distance_text = font.render(f"Distance: {distance_m:.2f} m", True, BLUE)
    screen.blit(distance_text, (20, 20))
    angle = 0
    if ideal_angle is not None:
        
        angle_text = font.render(f"Launch Angle: {ideal_angle:.1f}°", True, BLUE)
        speed_text = font.render(f"Launch Speed: {ideal_speed:.2f} m/s", True, BLUE)
    else:
        angle_text = font.render("Launch Angle: ---", True, BLACK)
        speed_text = font.render("Launch Speed: ---", True, BLACK)
    
    screen.blit(angle_text, (20, 50))
    screen.blit(speed_text, (20, 80))
    
    # Instructions
    instructions = font.render("WASD: Move | Arrows: Rotate | ESC: Quit", True, RED)
    screen.blit(instructions, (20, HEIGHT - 30))
    
    # Keep player in bounds
    player_pos.x = max(0, min(WIDTH, player_pos.x))
    player_pos.y = max(0, min(HEIGHT, player_pos.y))
    player_angle %= 360
    
    pygame.display.flip()

pygame.quit()