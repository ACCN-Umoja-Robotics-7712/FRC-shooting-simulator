import pygame
import math

pygame.init()

# Window settings
WIDTH, HEIGHT = 1302, 634
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triangle Player with Hexagon")

clock = pygame.time.Clock()

# Colors
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
RED = (255, 0, 0)

# Load player image
player_image_original = pygame.image.load(
    "images/Red_triangle.png"
).convert_alpha()

# --- IMPORTANT ---
# If your triangle image points UP by default, use -90
# If it points RIGHT, use 0
SPRITE_HEADING_OFFSET = -90

# Player settings
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_angle = 0
rotation_speed = 3  # degrees per frame

# Hexagon settings
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 94

# Heading line
LINE_LENGTH = 1000000

def hexagon_points(center, radius):
    cx, cy = center
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # flat-top hexagon
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def get_rotated_image(image, angle, position):
    rotated_image = pygame.transform.rotate(
        image,
        angle + SPRITE_HEADING_OFFSET
    )
    rect = rotated_image.get_rect(center=position)
    return rotated_image, rect

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Movement (WASD)
    if keys[pygame.K_w]:
        player_pos.y -= player_speed
    if keys[pygame.K_s]:
        player_pos.y += player_speed
    if keys[pygame.K_a]:
        player_pos.x -= player_speed
    if keys[pygame.K_d]:
        player_pos.x += player_speed

    # Rotation (Arrow keys)
    if keys[pygame.K_LEFT]:
        player_angle += rotation_speed
    if keys[pygame.K_RIGHT]:
        player_angle -= rotation_speed

    # Draw
    screen.fill(LIGHT_GRAY)

    # Draw centered hexagon
    hexagon = pygame.draw.polygon(
        screen,
        DARK_GRAY,
        hexagon_points(HEX_CENTER, HEX_RADIUS),
        10
    )

    # Draw player
    rotated_image, rotated_rect = get_rotated_image(
        player_image_original,
        player_angle,
        player_pos
    )
    
    screen.blit(rotated_image, rotated_rect)

    # --- Heading line ---
    # Player center
    player_center = pygame.Vector2(rotated_rect.center)

    # Heading direction (RIGHT = forward)
    angle_rad = math.radians(player_angle)

    direction = pygame.Vector2(
        math.cos(angle_rad),
        -math.sin(angle_rad)
    )

    # Find triangle tip by moving from center to rect edge
    line_start = player_center + direction * (rotated_rect.width / 2)

    line_end = line_start + direction * LINE_LENGTH

    pygame.draw.line(
        screen,
        RED,
        line_start,
        line_end,
        10
    )
    

    pygame.display.flip()

pygame.quit()
