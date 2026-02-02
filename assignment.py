import pygame
import random
import os
import math

# -------------------- CONSTANTS --------------------
WIDTH, HEIGHT = 1000, 500
SIZE = (WIDTH, HEIGHT)
CIRCLE_RADIUS=100
LIGHT_RADIUS=20
CHARGING_POS=(0,0)
BIRD_POS=(200,100)
BIRD_ANGLE=0
BIRD_SCALE=0.1
GRAY = (150, 150, 150)
GRAY_BORDER=(40,40,40)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FPS = 60
MAX_TRACE_DISTANCE=100
SL= SM= SR= 0
Battery_Max=200
def drawMap(screen):
    screen.fill(GRAY)
    pygame.draw.circle(screen, BLACK, CHARGING_POS,CIRCLE_RADIUS)
    pygame.draw.circle(screen, YELLOW, CHARGING_POS,LIGHT_RADIUS)

def loadBirdImage():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'tank.png')
    birdImage = pygame.image.load(path).convert_alpha()
    return birdImage

def trace_to_screen(start_pos, theta_deg, distance, screen_size):
    """
    start_pos: (x,y) start point (e.g., image_rect.center)
    theta_deg: angle in degrees (0 -> right, 90 -> up)
    distance: ray length
    screen_size: (W,H)
    Returns: (end_inside, clipped_line) where
      end_inside: (x,y) endpoint inside screen (or None if start is outside)
      clipped_line: (x1,y1,x2,y2) clipped segment, or None if not visible
    """
    W, H = screen_size
    screen_rect = pygame.Rect(0, 0, W, H)

    theta = math.radians(theta_deg)

    # Pygame screen coords: +x right, +y down, so "up" is -sin
    end = (
        start_pos[0] + math.cos(theta) * distance,
        start_pos[1] - math.sin(theta) * distance
    )

    clipped = screen_rect.clipline(start_pos, end)  # () if no intersection/visible

    if not clipped:
        return None, None

    (x1, y1), (x2, y2) = clipped
    end_inside = (x2, y2)  # this is the limit point inside the screen
    clipped_line=x1, y1, x2, y2
    if clipped_line:
        x1, y1, x2, y2 = clipped_line
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)
        pygame.draw.circle(screen, (0, 255, 0), (x2, y2), 5)  # end point inside screen
        S=1-math.sqrt((x1-x2)**2+(y1-y2)**2)/MAX_TRACE_DISTANCE
        return S
    return 

def drawBird(screen, angle,birdImage,birdScale):
    bird_drawn_surf = pygame.transform.rotozoom(birdImage, angle, birdScale)
    bird_rect = bird_drawn_surf.get_rect(center=BIRD_POS)
    screen.blit(bird_drawn_surf, bird_rect)
    return bird_drawn_surf, bird_rect

pygame.init()
screen = pygame.display.set_mode(SIZE)
drawMap(screen)
pygame.display.set_caption("Random Points + collidepoint (pygame 2.6.1)")
clock = pygame.time.Clock()
birdImage=loadBirdImage()
bird_drawn_surf, bird_rect=drawBird(screen,BIRD_ANGLE,birdImage,BIRD_SCALE)

start = bird_rect.center          # image center
SR = trace_to_screen(start, BIRD_ANGLE, MAX_TRACE_DISTANCE, screen.get_size())
SM = trace_to_screen(start, BIRD_ANGLE+90, MAX_TRACE_DISTANCE, screen.get_size())
SL = trace_to_screen(start, BIRD_ANGLE+180, MAX_TRACE_DISTANCE, screen.get_size())

# -------------------- RECT + POINTS --------------------

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawMap(screen)
    bird_drawn_surf, bird_rect=drawBird(screen,BIRD_ANGLE,birdImage,BIRD_SCALE)

    start = bird_rect.center          # image center
    SR = trace_to_screen(start, BIRD_ANGLE, MAX_TRACE_DISTANCE, screen.get_size())
    SM = trace_to_screen(start, BIRD_ANGLE+90, MAX_TRACE_DISTANCE, screen.get_size())
    SL = trace_to_screen(start, BIRD_ANGLE+180, MAX_TRACE_DISTANCE, screen.get_size())
    print(f"{SR=}, {SM=}, {SL=}")
    

    # -------------------- RECT + POINTS --------------------
    rect = pygame.Rect(220, 200, 250, 140)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()