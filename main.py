import pygame as pg
import time
import numpy as np
import math
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (50,50,255)
G = 6.67428*pow(10,-11)
PL_MASS = pow(10,7)
WIDTH, HEIGHT = 1600,800
screen = pg.display.set_mode((WIDTH, HEIGHT)) 
pg.display.set_caption('Space Physics sim')
screen.fill(BLACK) 
pg.display.flip() 
clock = pg.time.Clock()
orientation = 0
rotation_vec = 0
zoom = 1
zoom_out = True
ydist = 0.00000000001
xdist = 0.00000000001
a = 0
R_MASS = 1000
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


    
class Planet():
    def __init__(self):
        self.radius = 100000
        self.x = 0
        self.y = 0.0000000000001 - rocket.heigt * 4
        self.collision = False
        self.x_vec = 0
        self.y_vec = 0
        self.zoomed_pos = (0,0)
        self.f = 0.015
    def update(self):
        self.y_vec -= (G*(PL_MASS*R_MASS/ydist*ydist)*1/60)*math.cos(a*math.pi/360) 
        self.x_vec += (G*(PL_MASS*R_MASS/xdist*xdist)*1/60)*math.sin(a*math.pi/360) 
        if keys[pg.K_SPACE] == 1:
            self.x_vec += math.sin(orientation*math.pi/360*2)*self.f
            self.y_vec += math.cos(orientation*math.pi/360*2)*self.f
        self.y -= self.y_vec
        self.x += self.x_vec 
        self.zoomed_pos = (self.x*zoom +WIDTH/2, -self.y*zoom + HEIGHT/2 + self.radius*zoom)
        pg.draw.circle(screen, GREEN, self.zoomed_pos, self.radius*zoom)

class Laser():
    def update(self):
        self.x = rocket.x - WIDTH/2
        self.y = rocket.y - HEIGHT/2
        self.x_vec = planet.x_vec
        self.y_vec = planet.y_vec
        self.x_pos = self.x
        self.y_pos = self.y
        self.ydist = ydist
        self.xdist = xdist
        self.a = a
        for i in range(5000):
            self.x_pos = self.x
            self.y_pos = self.y
            self.y_vec -= (G*(PL_MASS*R_MASS/ydist*ydist)*1/60)*math.cos(a*math.pi/360)*1
            self.x_vec += (G*(PL_MASS*R_MASS/xdist*xdist)*1/60)*math.sin(a*math.pi/360)*1
            self.y -= self.y_vec/1
            self.x += self.x_vec/1
            self.zoomed_pos = (-self.x*zoom  +WIDTH/2 , self.y*zoom  + HEIGHT/2 )
            self.pos = (-self.x_pos*zoom  +WIDTH/2 , self.y_pos*zoom  + HEIGHT/2 )
            pg.draw.line(screen, BLUE, self.pos, self.zoomed_pos, int(5*zoom)+1)
            
    
rocket = Rocket()
planet = Planet()
laser = Laser()
pos = [0,0]
running = True
while running: 
    orientation -= rotation_vec
    rotation_vec = rotation_vec / 1.12
    keys = pg.key.get_pressed()
    rotation_vec += (keys[pg.K_d] - keys[pg.K_q]) * 0.1
    if zoom < 0.1: zoom_out == False
    else: zoom_out = True
    if zoom > 5: zoom = 5
    if zoom_out == True : zoom += (keys[pg.K_i] - keys[pg.K_o]) * 0.007*zoom
    else: zoom += abs((keys[pg.K_i] - keys[pg.K_o])) * 0.007*zoom
    for event in pg.event.get(): 
        if event.type == pg.QUIT: 
            running = False

    screen.fill(BLACK)
    rocket.draw()
    laser.update()
    ydist = abs(rocket.x-WIDTH/2 -planet.x)
    xdist = abs(rocket.y-HEIGHT/2 -planet.y)
    a = math.atan(xdist/ydist)*180/math.pi
    planet.update()
    
    pg.display.flip()
    clock.tick(60)
    
pg.quit()
