import pygame
clock = pygame.time.Clock()
import time

start = time.time()
dt = clock.tick(20)  # milliseconds since last frame

index=0
while True:
    index+=1

    fps = clock.get_fps()
    elapsed = int(time.time() - start)
    minutes, seconds = divmod(elapsed, 60)
    print(f"{index}, {dt} , {fps} ,{minutes:02d}:{seconds:02d}")
    