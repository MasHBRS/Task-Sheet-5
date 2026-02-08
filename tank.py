import torch as t
import pygame,math

# -------------------- CONSTANTS --------------------
WIDTH, HEIGHT = 1000, 500
SIZE = (WIDTH, HEIGHT)
BATTERY_MAX=1
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GRAY_BORDER=(40,40,40)
GREEN = (0, 200, 0)
FPS = 60
LIMIT_NUMBER_OF_TRAINING_FRAMES=1000


TANK_POS=(400,250)
TANK_ANGLE=90

class Tank():
    def moveTank(self, TANK_rect,speed,Tank_angle,dt):#assume speed=[vl,vr]
        theta=(-(speed[0]-speed[1])/10)*dt
        speed_value=(speed[0]+speed[1])/2
        speed_y=-speed_value*math.sin(math.radians(Tank_angle+theta))*dt/5
        speed_x=speed_value*math.cos(math.radians(Tank_angle+theta))*dt/5
        #TANK_rect.move_ip(speed_x, speed_y)    
        TANK_rect.center = (TANK_rect.center[0] + speed_x, TANK_rect.center[1] + speed_y)
        Tank_angle += theta
        TANK_drawn_surf = pygame.transform.rotozoom(self.TANKImage, Tank_angle, self.TANKScale)
        TANK_rect=TANK_drawn_surf.get_rect(center=TANK_rect.center)
        return TANK_drawn_surf, TANK_rect,Tank_angle
        
    def __init__(self, screen, individual_weight,initial_angle,
                 initial_position,TANK_IMAGE,TANK_SCALE,
                 Charging_RADIUS,BATTERY_DECHARGE_RATE,MAX_TRACE_DISTANCE,
                 TANK_drawn_surf, TANK_rect):
        self.individual_weight = individual_weight
        self.i,self.v=[],[]
        self.TANK_ANGLE=initial_angle
        self.TANK_POS=initial_position
        self.screen=screen
        self.TANKImage=TANK_IMAGE
        self.TANKScale=TANK_SCALE
        self.Charging_RADIUS=Charging_RADIUS
        self.Battery_Level=1
        self.BATTERY_DECHARGE_RATE=BATTERY_DECHARGE_RATE
        self.MAX_TRACE_DISTANCE=MAX_TRACE_DISTANCE
        self.TANK_drawn_surf=TANK_drawn_surf 
        self.TANK_rect=TANK_rect

    def ground_sensor_is_in_black_area(self,screen,TANK_rect):
            x,y=TANK_rect.center[0],TANK_rect.center[1]
            if math.sqrt(x**2+y**2)<=self.Charging_RADIUS:
                return True
            return False
    
    def trace_to_light(self,TANK_rect, theta_deg, distance, screen_size):
        W, H = screen_size
        diagon = math.hypot(W, H)

        screen_rect = pygame.Rect(0, 0, W, H)

        start_pos_x_front_sensor = int(TANK_rect.center[0]+(61//2)*math.cos(math.radians(self.TANK_ANGLE)))
        start_pos_y_front_sensor = int(TANK_rect.center[1]-(61//2)*math.sin(math.radians(self.TANK_ANGLE)))
        pygame.draw.circle(self.screen, (255, 255, 255), (start_pos_x_front_sensor, start_pos_y_front_sensor), 5)

        start_pos_x_back_sensor = int(TANK_rect.center[0]-(61//2)*math.cos(math.radians(self.TANK_ANGLE)))
        start_pos_y_back_sensor = int(TANK_rect.center[1]+(61//2)*math.sin(math.radians(self.TANK_ANGLE)))
        pygame.draw.circle(self.screen, (255, 255, 255), (start_pos_x_back_sensor, start_pos_y_back_sensor), 5)

        return math.hypot(start_pos_x_front_sensor,start_pos_y_front_sensor)/diagon, math.hypot(start_pos_x_back_sensor,start_pos_y_back_sensor)/diagon

    def computeFitness(self):
        self.individual_weight[-1]=self.v.mean()*(1-self.i.mean())
        print(f"Fitness: {self.individual_weight[-1]:.4f}")


    def trace_to_screen(self, TANK_rect, theta_deg, distance, screen_size):
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

        start_pos_x = int(TANK_rect.center[0]+(61//2)*math.cos(math.radians(self.TANK_ANGLE)))
        start_pos_y = int(TANK_rect.center[1]-(61//2)*math.sin(math.radians(self.TANK_ANGLE)))
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
            pygame.draw.line(self.screen, (255, 0, 0), (x1, y1), (x2, y2), 2)
            pygame.draw.circle(self.screen, (0, 255, 0), (x2, y2), 5)  # end point inside screen
            S=1-math.sqrt((x1-x2)**2+(y1-y2)**2)/self.MAX_TRACE_DISTANCE
            return S
        return 

    def activatio_function_hidden_layer(self, x):
        return -1+2/(1+t.exp(-2*x))
    
    def activatio_function_final_layer(self, x):
        return -1+2/(1+t.exp(-2*x))

    def displayValues(self, SL, SM, SR, charging_area,front,back, VL, VR):
        try:
            font = pygame.font.SysFont(None, 30)
            text_SL = font.render(f"SL: {SL:.3f}" if SL !=(None, None) else 'SL: None', True, BLUE)
            text_SM = font.render(f"SM: {SM:.3f}" if SM !=(None, None) else 'SM: None', True, BLUE)
            text_SR = font.render(f"SR: {SR:.3f}" if SR !=(None, None) else 'SR: None', True, BLUE)
            text_charging_area = font.render(f"Grnd: {1 if charging_area else 0}", True, BLUE)
            text_front = font.render(f"Frnt: {front:.3f}", True, BLUE)
            text_back = font.render(f"Bck: {back:.3f}", True, BLUE)
            text_Battery_Level = font.render(f"Batt: {self.Battery_Level}", True, BLUE)
            text_VL = font.render(f"VL: {VL:.3f}", True, BLUE)
            text_VR = font.render(f"VR: {VR:.3f}", True, BLUE)
        except:
            self.Battery_Level=0
        self.screen.blit(text_SL, (WIDTH*0.9, 10))
        self.screen.blit(text_SM, (WIDTH*0.9, 30))
        self.screen.blit(text_SR, (WIDTH*0.9, 50))
        self.screen.blit(text_charging_area, (WIDTH*0.9, 70))
        self.screen.blit(text_front, (WIDTH*0.9, 90))
        self.screen.blit(text_back, (WIDTH*0.9, 110))
        self.screen.blit(text_Battery_Level, (WIDTH*0.9, 130))
        self.screen.blit(text_VL, (WIDTH*0.9, 150))
        self.screen.blit(text_VR, (WIDTH*0.9, 170))

    def step(self,dt):
        SR = self.trace_to_screen(self.TANK_rect, self.TANK_ANGLE-90, self.MAX_TRACE_DISTANCE, self.screen.get_size())
        SM = self.trace_to_screen(self.TANK_rect, self.TANK_ANGLE, self.MAX_TRACE_DISTANCE, self.screen.get_size())
        SL = self.trace_to_screen(self.TANK_rect, self.TANK_ANGLE+90, self.MAX_TRACE_DISTANCE, self.screen.get_size())
        if SL==(None,None) or SM==(None,None) or SR==(None,None):
            return self.individual_weight
        lightFront,lightBack=self.trace_to_light(self.TANK_rect, self.TANK_ANGLE, self.MAX_TRACE_DISTANCE, self.screen.get_size())
        blackSensor=self.ground_sensor_is_in_black_area(self.screen,self.TANK_rect)
        self.screen.blit(self.TANK_drawn_surf, self.TANK_rect)
        self.displayValues(SL, SM, SR, blackSensor,lightFront,lightBack, -9, -9)
        self.i.append((SL+SM+SR)/3)

        inputTensor=t.tensor([SL, SM, SR, lightFront,lightBack, blackSensor,self.Battery_Level])
        hiddenLayer=inputTensor@self.individual_weight[:35].reshape(7,5) #shape:(1,7)@(7,5)=(1,5)
        hiddenLayer+=self.individual_weight[35:40]+self.individual_weight[40:45] #shape:rec(1,5)+bias(1,5)=(1,5)
        hiddenLayer=self.activatio_function_hidden_layer(hiddenLayer)
        self.individual_weight[35:40]=hiddenLayer #updating the recurrents. shape:(1,5)
        outputlayer=hiddenLayer@self.individual_weight[45:55].reshape(5,2) #shape:(1,5)@(5,2)=(1,2)
        outputlayer+=self.individual_weight[55:57] #adding bias. shape:rec(1,2)
        outputlayer=self.activatio_function_final_layer(outputlayer)
        VL,VR=outputlayer[0],outputlayer[1]
        self.TANK_drawn_surf, self.TANK_rect,self.Tank_angle=self.moveTank(self.TANK_rect,outputlayer,self.TANK_ANGLE,dt)
        self.v.append(VL**2+VR**2)
        self.Battery_Level-=self.BATTERY_DECHARGE_RATE
        self.screen.blit(self.TANK_drawn_surf, self.TANK_rect)
        return outputlayer