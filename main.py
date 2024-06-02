import pygame as pg
import time
import numpy as np
import math
import taichi as ti
ti.init(arch=ti.gpu)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (50,50,255)
G = 6.67428*pow(10,-11)
PL_MASS = pow(10,7)
WIDTH, HEIGHT = 1600,800
screen = pg.display.set_mode((WIDTH, HEIGHT)) 
screen.fill(BLACK) 
pg.display.flip() 
clock = pg.time.Clock()
pg.display.set_caption('Space Physics sim' + str(clock.get_fps()))
orientation = 0
rotation_vec = 0
zoom = 1
zoom_out = True
ydist = 0.00000000001
xdist = 0.00000000001
a = 0
R_MASS = 1000
sensy = 0.2
pg.font.init()
method = 0
pos = [(0,0), (0,0), (0,0)]



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
        self.y = -self.radius - rocket.heigt * 4
        self.collision = False
        self.x_vec = 0
        self.y_vec = 0
        self.zoomed_pos = (0,0)
        self.f = 0.05
    def update(self):
        if keys[pg.K_SPACE] == 1:
            self.x_vec += math.sin(orientation*math.pi/360*2)*self.f
            self.y_vec += math.cos(orientation*math.pi/360*2)*self.f
        if math.sqrt((ydist)**2 + (xdist)**2)-self.radius -rocket.heigt/2>0:
            self.y_vec -= (G*(PL_MASS*R_MASS/ydist*ydist)*1/60)*math.cos(math.radians(a))
            self.x_vec += (G*(PL_MASS*R_MASS/xdist*xdist)*1/60)*math.sin(math.radians(a))
        else:
            self.y_vec=abs(self.y_vec/1.5)* np.sign(self.y_vec)
            self.x_vec=abs(self.x_vec/1.5)* np.sign(self.x_vec)
        self.y -= self.y_vec
        self.x += self.x_vec 
        self.zoomed_pos = (self.x*zoom +WIDTH/2, -self.y*zoom + HEIGHT/2)
        pg.draw.circle(screen, GREEN, self.zoomed_pos, self.radius*zoom)
class Laser():
    def update(self):
        self.x = rocket.x - WIDTH/2
        self.y = rocket.y - HEIGHT/2
        self.x_vec = planet.x_vec
        self.y_vec = planet.y_vec
        self.x_pos = self.x
        self.y_pos = self.y
        self.xdist = xdist
        self.ydist = ydist
        self.a = a
        for i in range(5000):
            self.x_pos = self.x
            self.y_pos = self.y
            self.xdist = planet.x - self.x
            self.ydist = planet.y - self.y
            self.a = math.degrees(math.atan2(self.xdist, self.ydist))
            self.y_vec += (G*(PL_MASS*R_MASS/self.ydist*self.ydist)*1/60)*math.cos(math.radians(self.a)) 
            self.x_vec += (G*(PL_MASS*R_MASS/self.xdist*self.xdist)*1/60)*math.sin(math.radians(self.a)) 
            self.y += self.y_vec
            self.x += self.x_vec
            self.zoomed_pos = (-self.x*zoom  +WIDTH/2 , -self.y*zoom  + HEIGHT/2 )
            self.pos = (-self.x_pos*zoom  +WIDTH/2 , -self.y_pos*zoom  + HEIGHT/2 )
            pg.draw.line(screen, BLUE, self.pos, self.zoomed_pos, int(5*zoom)+1)
class GUI():
    def __init__(self):
        self.sf = pg.font.SysFont('Corbel',30)
    def update(self):
        self.velocity = self.sf.render('velocity : ' + str(round((math.sqrt(planet.x_vec**2 + planet.y_vec**2)*100))/100), True, WHITE)
        self.alt = self.sf.render('altitude : ' + str(round((math.sqrt((ydist)**2 + (xdist)**2)-planet.radius)*10)/10), True, WHITE)
        screen.blit(self.velocity,(0, 0))
        screen.blit(self.alt, (0, 30))
        
rocket = Rocket()
planet = Planet()
laser = Laser()
gui = GUI()
running = True
while running: 
    pg.display.set_caption('Space Physics sim                 ' + str(clock.get_fps()))
    orientation -= rotation_vec
    rotation_vec = rotation_vec / 1.12
    keys = pg.key.get_pressed()
    rotation_vec += (keys[pg.K_d] - keys[pg.K_q]) * 0.2
    if zoom < 0.1: zoom_out == False
    else: zoom_out = True
    if zoom > 5: zoom = 5
    if zoom_out == True : zoom += (keys[pg.K_i] - keys[pg.K_o]) * sensy*zoom
    else: zoom += abs((keys[pg.K_i] - keys[pg.K_o])) * sensy*zoom
    for event in pg.event.get(): 
        if event.type == pg.QUIT: 
            running = False

    screen.fill(BLACK)
    rocket.draw()
    xdist = rocket.x-WIDTH/2 -planet.x
    ydist = rocket.y-HEIGHT/2 -planet.y
    a = math.degrees(math.atan2(xdist, ydist))
    planet.update()
    laser.update()
    gui.update()
    pg.display.flip()
    clock.tick(60)
    
pg.quit()
