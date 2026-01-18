import pygame
import math

pygame.init()

WIDTH, HEIGHT = 651.2, 158.85*2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FRC 2026 Shot Simulator")

clock = pygame.time.Clock()

# Colors
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
DARK_GRAY = (80, 80, 80)

# Load player image
player_image_original = pygame.image.load(
    "images/Red_triangle.png"
).convert_alpha()
player_image_original = pygame.transform.scale(
    player_image_original, (50, 50)
)

player_pos = pygame.Vector2(182.12, HEIGHT // 2)
player_speed = 5
player_angle = 0
rotation_speed = 3
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 24.1

def hexagon_points(center, radius):
    cx, cy = center
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def get_rotated_image(image, angle, position):
    rotated_image = pygame.transform.rotate(image, angle)
    rect = rotated_image.get_rect(center=position)
    return rotated_image, rect

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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


    screen.fill(LIGHT_GRAY)

    pygame.draw.polygon(
        screen,
        DARK_GRAY,
        hexagon_points(HEX_CENTER, HEX_RADIUS),
        3
    )

    rotated_image, rotated_rect = get_rotated_image(
        player_image_original,
        player_angle,
        player_pos
    )
    screen.blit(rotated_image, rotated_rect)
    if keys[pygame.K_SPACE]:
        pygame.draw.line(screen, pygame.Color("green"), player_pos, HEX_CENTER, 10)
    pygame.display.flip()

pygame.quit()
