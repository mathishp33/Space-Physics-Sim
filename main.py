import pygame as pg
import time
import numpy as np
import math
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
G = 6.67428*pow(10,-11)
PL_MASS = pow(10,8)
WIDTH, HEIGHT = 800,400
screen = pg.display.set_mode((WIDTH, HEIGHT)) 
pg.display.set_caption('Space Physics sim')
screen.fill(BLACK) 
pg.display.flip() 
clock = pg.time.Clock()
orientation = 0
rotation_vec = 0
zoom = 1
zoom_out = True
class Rocket():
    def __init__(self):
        self.rocket_img = pg.image.load('rocket.png')
        self.x = WIDTH/2 + 0.000000000001
        self.y = HEIGHT/2
        self.width = 25
        self.heigt = 50
    def draw(self):
        if zoom > 0.1:
            self.rocket_img = pg.transform.scale(self.rocket_img,(self.width*zoom,self.heigt*zoom))
            self.image_rect = self.rocket_img.get_rect(topleft = (self.x-(self.width*zoom/2), self.y-(self.heigt*zoom/2)))
        else:
            self.rocket_img = pg.transform.scale(self.rocket_img,(self.width*0.1,self.heigt*0.1))
            self.image_rect = self.rocket_img.get_rect(topleft = (self.x-(self.width*0.1/2), self.y-(self.heigt*0.1/2)))
        self.offset_center_to_pivot = pg.math.Vector2((self.x,self.y)) - self.image_rect.center
        self.rotated_offset = self.offset_center_to_pivot.rotate(orientation)
        self.rotated_image_center = (self.x - self.rotated_offset.x, self.y - self.rotated_offset.y)
        self.rotated_image = pg.transform.rotate(self.rocket_img, orientation)
        self.rotated_image_rect = self.rotated_image.get_rect(center = self.rotated_image_center)
        screen.blit(self.rotated_image, self.rotated_image_rect)
        return (self.x-WIDTH/2, self.y-HEIGHT/2)

    
class Planet():
    def __init__(self):
        self.radius = 5000
        self.x = 0
        self.y = 0.0000000000001 - rocket.heigt * 2
        self.collision = False
        self.x_vec = 0
        self.y_vec = 0
        self.x_thrust = 0
        self.y_thrust = 0
        self.zoomed_pos = (0,0)
    def draw(self):
        
        return (self.x, self.y)
    def update(self):
        if keys[pg.K_SPACE] == 1:
            self.x_thrust = keys[pg.K_SPACE]*math.sin(orientation*math.pi/360*2)*1.5
            self.y_thrust = keys[pg.K_SPACE]*math.cos(orientation*math.pi/360*2)*1.5
        if math.sqrt((ydist*ydist) + (xdist*xdist)) - (rocket.heigt/2) + self.radius < self.radius :
            self.collision = True
        else: self.collision = False
        self.y_vec = (G*(PL_MASS*1000/ydist*ydist)*1/60)*math.cos(a*math.pi/360) - self.y_thrust
        self.x_vec = (G*(PL_MASS*1000/xdist*xdist)*1/60)*math.sin(a*math.pi/360) + self.x_thrust
        if self.collision == True: 
            self.y = self.y - abs(self.y_vec)
        else : self.y = self.y + self.y_vec
        self.x = self.x + self.x_vec 
        self.zoomed_pos = (self.x*zoom +WIDTH/2, -self.y*zoom + HEIGHT/2 + self.radius*zoom)
        pg.draw.circle(screen, GREEN, self.zoomed_pos, self.radius*zoom)


rocket = Rocket()
planet = Planet()
pos = [0,0]
running = True
while running: 
    orientation -= rotation_vec
    rotation_vec = rotation_vec / 1.12
    keys = pg.key.get_pressed()
    rotation_vec += (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * 0.1
    if zoom < 0.1: zoom_out == False
    else: zoom_out = True
    if zoom > 5: zoom = 5
    if zoom_out == True : zoom += (keys[pg.K_i] - keys[pg.K_o]) * 0.007*zoom
    else: zoom += abs((keys[pg.K_i] - keys[pg.K_o])) * 0.007*zoom
    for event in pg.event.get(): 
        if event.type == pg.QUIT: 
            running = False

    screen.fill(BLACK)
    pos[0] = rocket.draw()
    pos[1] = planet.draw()
    ydist = abs(pos[0][1]- pos[1][1])
    xdist = abs(pos[0][0]- pos[1][0])
    a = math.atan(xdist/ydist)*180/math.pi
    planet.update()
    
    pg.display.flip()
    clock.tick(60)
    
pg.quit()