import pygame
import random
import os
import math
from tank import Tank
import torch
# -------------------- CONSTANTS --------------------
WIDTH, HEIGHT = 1000, 500
SIZE = (WIDTH, HEIGHT)
WIDTH, HEIGHT = 1000, 500
SIZE = (WIDTH, HEIGHT)
BATTERY_DECHARGE_RATE=0.01
Charging_RADIUS=150
LIGHT_RADIUS=20
CHARGING_POS=(0,0)
TANK_SCALE=0.1
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GRAY_BORDER=(40,40,40)
GREEN = (0, 200, 0)
FPS = 60
LIMIT_NUMBER_OF_TRAINING_FRAMES=1000
MAX_TRACE_DISTANCE=100

Battery_Level=1
TANK_POS=(400,250)
TANK_ANGLE=90
Train_Epoch_Limit=1000
Num_individuals=3

def drawMap(screen):
    screen.fill(GRAY)
    pygame.draw.circle(screen, BLACK, CHARGING_POS,Charging_RADIUS)
    pygame.draw.circle(screen, YELLOW, CHARGING_POS,LIGHT_RADIUS)

def loadTANKImage():
    path = 'images/tank.png'
    TANKImage = pygame.image.load(path).convert_alpha()
    return TANKImage

def drawTANK(screen, angle,TANKImage,TANKScale):
    TANK_drawn_surf = pygame.transform.rotozoom(TANKImage, angle, TANKScale)
    TANK_rect = TANK_drawn_surf.get_rect(center=TANK_POS)
    screen.blit(TANK_drawn_surf, TANK_rect)
    return TANK_drawn_surf, TANK_rect

def createTank(individual_weight,screen,TANKImage,TANK_drawn_surf, TANK_rect):
    return Tank(individual_weight=individual_weight,
                      screen=screen,
                      initial_angle=TANK_ANGLE,
                      initial_position=TANK_POS,
                      TANK_IMAGE=TANKImage,
                      TANK_SCALE=TANK_SCALE,
                      Charging_RADIUS=Charging_RADIUS,
                      BATTERY_DECHARGE_RATE=BATTERY_DECHARGE_RATE,
                      MAX_TRACE_DISTANCE=MAX_TRACE_DISTANCE,
                      TANK_drawn_surf=TANK_drawn_surf, 
                      TANK_rect=TANK_rect)        
def evolve(model):
    return model #placeholder for evolution function, should return the new model after applying selection, crossover and mutation

def train(model):
    pygame.init()
    pygame.display.set_caption("Random Points + collidepoint (pygame 2.6.1)")
    individualIndex=tempIndex=0
    tank=None
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SIZE)
    drawMap(screen)
    TANKImage=loadTANKImage()
    TANK_drawn_surf, TANK_rect=drawTANK(screen,TANK_ANGLE,TANKImage,TANK_SCALE)
    Train_epoch_limit=1000 #Each individual is trained for 1000 frames
    while running:
        dt = clock.tick(FPS)
        drawMap(screen)

        if(tempIndex%Train_epoch_limit==0):
            tank=createTank(model[individualIndex],screen,TANKImage,TANK_drawn_surf, TANK_rect)
        tank.step(dt)
        if (tempIndex+1)% Train_Epoch_Limit==0:
            tank.computeFitness()
            model[individualIndex,:]=tank.individual_weight
            if (individualIndex+1)%Num_individuals==0:
                model=evolve(model)
            individualIndex=(individualIndex+1)%Num_individuals
        tempIndex+=1
        #if pressed key s: save model
        #if pressed key q: quit training
        

        pygame.display.flip()
    pygame.quit()
    
model=torch.rand(Num_individuals, 58)*2-1 #random weights between -1 and 1
train(model)