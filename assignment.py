import pygame
import random
import os
import math

# -------------------- CONSTANTS --------------------
WIDTH, HEIGHT = 1000, 500
SIZE = (WIDTH, HEIGHT)
Charging_RADIUS=150
LIGHT_RADIUS=20
CHARGING_POS=(0,0)
TANK_POS=(400,250)
TANK_ANGLE=90
TANK_SCALE=0.1
TANK_BATTERY_LEVEL=150
GRAY = (150, 150, 150)
GRAY_BORDER=(40,40,40)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FPS = 60
MAX_TRACE_DISTANCE=100
VL= VR= SL= SM= SR= 0
Battery_Max=200

def drawMap(screen):
    screen.fill(GRAY)
    pygame.draw.circle(screen, BLACK, CHARGING_POS,Charging_RADIUS)
    pygame.draw.circle(screen, YELLOW, CHARGING_POS,LIGHT_RADIUS)

def loadTANKImage():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'tank.png')
    TANKImage = pygame.image.load(path).convert_alpha()
    return TANKImage

def trace_to_light(TANK_rect, theta_deg, distance, screen_size):
    W, H = screen_size
    diagon = math.hypot(W, H)

    screen_rect = pygame.Rect(0, 0, W, H)

    start_pos_x_front_sensor = int(TANK_rect.center[0]+(61//2)*math.cos(math.radians(TANK_ANGLE)))
    start_pos_y_front_sensor = int(TANK_rect.center[1]-(61//2)*math.sin(math.radians(TANK_ANGLE)))
    pygame.draw.circle(screen, (255, 255, 255), (start_pos_x_front_sensor, start_pos_y_front_sensor), 5)
    
    start_pos_x_back_sensor = int(TANK_rect.center[0]-(61//2)*math.cos(math.radians(TANK_ANGLE)))
    start_pos_y_back_sensor = int(TANK_rect.center[1]+(61//2)*math.sin(math.radians(TANK_ANGLE)))
    pygame.draw.circle(screen, (255, 255, 255), (start_pos_x_back_sensor, start_pos_y_back_sensor), 5)

    return math.hypot(start_pos_x_front_sensor,start_pos_y_front_sensor)/diagon, math.hypot(start_pos_x_back_sensor,start_pos_y_back_sensor)/diagon

def trace_to_screen(TANK_rect, theta_deg, distance, screen_size):
    """
    TANK_rect: rectangle of the tank image
    theta_deg: angle in degrees (0 -> right, 90 -> up)
    distance: ray length
    screen_size: (W,H)
    Returns: (end_inside, clipped_line) where
      end_inside: (x,y) endpoint inside screen (or None if start is outside)
      clipped_line: (x1,y1,x2,y2) clipped segment, or None if not visible
    """
    W, H = screen_size
    screen_rect = pygame.Rect(0, 0, W, H)

    start_pos_x = int(TANK_rect.center[0]+(61//2)*math.cos(math.radians(TANK_ANGLE)))
    start_pos_y = int(TANK_rect.center[1]-(61//2)*math.sin(math.radians(TANK_ANGLE)))
    start_pos = (start_pos_x, start_pos_y)
    # Pygame screen coords: +x right, +y down, so "up" is -sin
    end = (
        start_pos[0] + math.cos(math.radians(theta_deg)) * distance,
        start_pos[1] - math.sin(math.radians(theta_deg)) * distance
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

def ground_sensor_is_in_black_area(screen,TANK_rect):
        x,y=TANK_rect.center[0],TANK_rect.center[1]
        if math.sqrt(x**2+y**2)<=Charging_RADIUS:
            return True
        return False

def drawTANK(screen, angle,TANKImage,TANKScale):
    TANK_drawn_surf = pygame.transform.rotozoom(TANKImage, angle, TANKScale)
    TANK_rect = TANK_drawn_surf.get_rect(center=TANK_POS)
    screen.blit(TANK_drawn_surf, TANK_rect)
    return TANK_drawn_surf, TANK_rect 

#TANK_drawn_surf, TANK_rect
def moveTank(TANK_rect,speed,Tank_angle,wheel_base=2,dt=1):#assume speed=[vl,vr]
    speed_y=-speed*math.sin(math.radians(Tank_angle))
    speed_x=speed*math.cos(math.radians(Tank_angle))
    TANK_rect.move_ip(speed_x, speed_y)    
    Tank_angle -= 1
    TANK_drawn_surf = pygame.transform.rotozoom(TANKImage, Tank_angle, TANK_SCALE)
    TANK_rect=TANK_drawn_surf.get_rect(center=TANK_rect.center)
    return TANK_drawn_surf, TANK_rect,Tank_angle

def displayValues(screen, SL, SM, SR, font,charging_area,front,back,battery_level, VL, VR):
    try:
        text_SL = font.render(f"SL: {SL:.3f}" if SL !=(None, None) else 'SL: None', True, BLUE)
        text_SM = font.render(f"SM: {SM:.3f}" if SM !=(None, None) else 'SM: None', True, BLUE)
        text_SR = font.render(f"SR: {SR:.3f}" if SR !=(None, None) else 'SR: None', True, BLUE)
        text_charging_area = font.render(f"Grnd: {1 if charging_area else 0}", True, BLUE)
        text_front = font.render(f"Frnt: {front:.3f}", True, BLUE)
        text_back = font.render(f"Bck: {back:.3f}", True, BLUE)
        text_battery_level = font.render(f"Batt: {battery_level}", True, BLUE)
        text_VL = font.render(f"VL: {VL:.3f}", True, BLUE)
        text_VR = font.render(f"VR: {VR:.3f}", True, BLUE)
    except:
        battery_level=0
    
    
    screen.blit(text_SL, (WIDTH*0.9, 10))
    screen.blit(text_SM, (WIDTH*0.9, 30))
    screen.blit(text_SR, (WIDTH*0.9, 50))
    screen.blit(text_charging_area, (WIDTH*0.9, 70))
    screen.blit(text_front, (WIDTH*0.9, 90))
    screen.blit(text_back, (WIDTH*0.9, 110))
    screen.blit(text_battery_level, (WIDTH*0.9, 130))
    screen.blit(text_VL, (WIDTH*0.9, 150))
    screen.blit(text_VR, (WIDTH*0.9, 170))

pygame.init()
font = pygame.font.SysFont(None, 30)
screen = pygame.display.set_mode(SIZE)
drawMap(screen)
pygame.display.set_caption("Random Points + collidepoint (pygame 2.6.1)")
clock = pygame.time.Clock()
TANKImage=loadTANKImage()
TANK_drawn_surf, TANK_rect=drawTANK(screen,TANK_ANGLE,TANKImage,TANK_SCALE)

index=0
running = True
speed=4
TANK_drawn_surf, TANK_rect=drawTANK(screen,TANK_ANGLE,TANKImage,TANK_SCALE)

while running:
    dt = clock.tick(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawMap(screen)
    
    pygame.draw.rect(screen, (255, 0, 0), TANK_rect, 1)
    TANK_drawn_surf, TANK_rect,TANK_ANGLE=moveTank(TANK_rect,speed,TANK_ANGLE,wheel_base=500,dt=dt)
    pygame.draw.rect(screen, (255, 255, 0), TANK_rect, 2)

    SR = trace_to_screen(TANK_rect, TANK_ANGLE-90, MAX_TRACE_DISTANCE, screen.get_size())
    SM = trace_to_screen(TANK_rect, TANK_ANGLE, MAX_TRACE_DISTANCE, screen.get_size())
    SL = trace_to_screen(TANK_rect, TANK_ANGLE+90, MAX_TRACE_DISTANCE, screen.get_size())
    front,back=trace_to_light(TANK_rect, TANK_ANGLE, MAX_TRACE_DISTANCE, screen.get_size())
    charging_area=ground_sensor_is_in_black_area(screen,TANK_rect)
    screen.blit(TANK_drawn_surf, TANK_rect)

    displayValues(screen, SL, SM, SR, font,charging_area,front,back, TANK_BATTERY_LEVEL, VL, VR)
    
    pygame.display.flip()
    clock.tick(FPS) 
pygame.quit()