import pygame as pg
import random
import numpy as np
import time
from numba import jit


@jit(parallel=True, fastmath=True, forceobj=True)
def trajectory(a, objects, screen):
    delta_time = 30
    for i in range(240):
        for j, b in enumerate(objects):
            dx = b.x - a.x
            dy = b.y - a.y
            dist_sq = dx**2 + dy**2
            dist = np.sqrt(dist_sq)
            if dist == 0:
                continue
            force_mag = 6.674e-11 * a.mass * b.mass / dist_sq
            fx = force_mag * dx / dist
            fy = force_mag * dy / dist

            a.force[0] += fx
            a.force[1] += fy
            b.force[0] -= fx
            b.force[1] -= fy
        ax = a.force[0] / a.mass
        ay = a.force[1] / a.mass
        a.vel[0] += ax * delta_time
        a.vel[1] += ay * delta_time
        prev_x, prev_y = a.x, a.y
        a.x += a.vel[0] * delta_time
        a.y += a.vel[1] * delta_time
        a.force = np.array([0.0, 0.0])
            
        pg.draw.line(screen, [int(np.sin(time.time() + i) * 128 + 128) for i in [i, i + 1, i + 2]], app.to_screen_pos(prev_x, prev_y), app.to_screen_pos(a.x, a.y))
            


class Body:
    def __init__(self, x=0, y=0, radius=100, color=[random.randint(0, 255) for _ in range(3)]):
        self.x, self.y = x, y  # meters
        self.color = color
        self.radius = radius  # meters
        self.volume = 4 * 3.14 * (self.radius ** 3) / 3  # m^3
        self.mass = 1500 * self.volume  # Kg
        self.vel = np.array([0.0, 0.0])  # m/s
        self.force = np.array([0.0, 0.0])
        
class Rocket:
    def __init__(self, x, y):
        self.x, self.y = x, y  # meters
        self.color = [random.randint(0, 255) for _ in range(3)]
        self.dim = (100, 100) #meters
        self.volume = self.dim[0] * self.dim[1] * 1 #m^3
        self.mass = 2200 * self.volume  # Kg
        self.vel = np.array([0.0, 0.0])  # m/s
        self.force = np.array([0.0, 0.0])

class App:
    def __init__(self):
        self.running = False
        self.clock = pg.time.Clock()
        self.RES = (1200, 900)
        self.screen = None
        self.FPS = 120
        self.mouse_pos = (0, 0)
        self.clicks = ()

        self.bodies = []
        self.preview_new_body = None
        self.space_craft = None
        self.preview_space_craft = None

        self.cam_offset = [0, 0]
        self.zoom = 1.0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.paused = False
        self.dragging_body = None
        
        self.font = pg.font.Font('freesansbold.ttf', 24)

    def to_screen_pos(self, world_x, world_y):
        return (
            int((world_x + self.cam_offset[0]) * self.zoom),
            int((world_y + self.cam_offset[1]) * self.zoom)
            )
    
    def to_real_pos(self, screen_x, screen_y):
        return (
            int(screen_x / self.zoom - self.cam_offset[0]),
            int(screen_y / self.zoom - self.cam_offset[1])
            )

    def cam_input(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.dragging = True
                self.last_mouse_pos = pg.mouse.get_pos()
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                self.dragging = False
        elif event.type == pg.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            dx = mouse_x - self.last_mouse_pos[0]
            dy = mouse_y - self.last_mouse_pos[1]
            self.last_mouse_pos = (mouse_x, mouse_y)
            self.cam_offset[0] += dx / self.zoom
            self.cam_offset[1] += dy / self.zoom
        elif event.type == pg.MOUSEWHEEL:
            mx, my = pg.mouse.get_pos()
            world_x = mx / self.zoom - self.cam_offset[0]
            world_y = my / self.zoom - self.cam_offset[1]
    
            zoom_factor = 1.1
            if event.y > 0:
                self.zoom *= zoom_factor
            elif event.y < 0:
                self.zoom /= zoom_factor
    
            self.cam_offset[0] = mx / self.zoom - world_x
            self.cam_offset[1] = my / self.zoom - world_y
                
    def update(self, mouse_pos):
        
        if self.space_craft != None:
            if not self.paused:
                sc = self.space_craft
                for i, b in enumerate(self.bodies):
                    dx = sc.x - b.x
                    dy = sc.y - b.y
                    dist_sq = dx**2 + dy**2
                    dist = np.sqrt(dist_sq)
                    if dist == 0:
                        continue
                    force_mag = 6.674e-11 * b.mass * sc.mass / dist_sq
                    fx = force_mag * dx / dist
                    fy = force_mag * dy / dist
        
                    b.force[0] += fx
                    b.force[1] += fy
                    sc.force[0] -= fx
                    sc.force[1] -= fy
                
                ax = self.space_craft.force[0] / self.space_craft.mass
                ay = self.space_craft.force[1] / self.space_craft.mass
                self.space_craft.vel[0] += ax
                self.space_craft.vel[1] += ay
                self.space_craft.x += self.space_craft.vel[0]
                self.space_craft.y += self.space_craft.vel[1]
                    
            pg.draw.rect(self.screen, self.space_craft.color, ())
            
            self.space_craft.force = np.array([0.0, 0.0])
            
        if self.dragging_body != None:
            dx = mouse_pos[0] - self.dragging_body.x
            dy = mouse_pos[1] - self.dragging_body.y
            drag_force = self.dragging_body.mass / (self.dragging_body.radius * 100)
            self.dragging_body.force[0] += dx * drag_force
            self.dragging_body.force[1] += dy * drag_force
        
        for i, b in enumerate(self.bodies):
            if not self.paused:
                for j, b2 in enumerate(self.bodies[i + 1:]):
                    dx = b2.x - b.x
                    dy = b2.y - b.y
                    dist = np.hypot(dx, dy)
                    if dist < b.radius + b2.radius:
                        if b.radius > b2.radius:
                            b.radius += b2.radius
                            self.bodies.remove(b2)
                        else:
                            b2.radius += b.radius
                            self.bodies.remove(b)
                            
                for j, b2 in enumerate(self.bodies):
                    if i >= j:
                        continue
                    dx = b2.x - b.x
                    dy = b2.y - b.y
                    dist_sq = dx**2 + dy**2
                    dist = np.sqrt(dist_sq)
                    if dist == 0:
                        continue
                    force_mag = 6.674e-11 * b.mass * b2.mass / dist_sq
                    fx = force_mag * dx / dist
                    fy = force_mag * dy / dist
        
                    b.force[0] += fx
                    b.force[1] += fy
                    b2.force[0] -= fx
                    b2.force[1] -= fy
                
                ax = b.force[0] / b.mass
                ay = b.force[1] / b.mass
                b.vel[0] += ax
                b.vel[1] += ay
                b.x += b.vel[0]
                b.y += b.vel[1]
            
            x, y = self.to_screen_pos(b.x, b.y)
            x_f, y_f = self.to_screen_pos(b.x + b.force[0] / 50, b.y + b.force[1] / 50)
            x_v, y_v = self.to_screen_pos(b.x + b.vel[0] * 40, b.y + b.vel[1] * 40)
            r = int(b.radius * self.zoom)
            pg.draw.circle(self.screen, b.color, (x, y), r)
            try:
                pg.draw.line(self.screen, (255, 0, 0), (x, y), (x_f, y), r // 10)
                pg.draw.line(self.screen, (0, 0, 255), (x, y), (x, y_f), r // 10)
                pg.draw.line(self.screen, (0, 255, 0), (x, y), (x_v, y_v), r // 10)
            except:
                pass
            
            b.force = np.array([0.0, 0.0])

    def run(self):
        self.running = True
        self.screen = pg.display.set_mode(self.RES)

        while self.running:
            pg.display.set_caption(f'Py-Space Physics Simulator                 {round(self.clock.get_fps(), 2)}')
            self.screen.fill((0, 0, 0))
            self.mouse_pos = pg.mouse.get_pos()
            mouse_pos = self.to_real_pos(self.mouse_pos[0], self.mouse_pos[1])
            self.clicks = pg.mouse.get_pressed()
            
            text = self.font.render('Delete Spaceship' if self.space_craft else 'Spawn Spaceship', True, (0, 0, 0), (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.topleft = (5, 5)
            self.screen.blit(text, text_rect)
                    
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.paused = not self.paused
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        colliding = False
                        if text_rect.collidepoint(self.mouse_pos):
                            if self.space_craft != None:
                                self.space_craft = None
                                self.preview_scape_craft = None
                            else:
                                self.preview_space_craft = mouse_pos
                        else:
                            if self.preview_space_craft != None:
                                self.space_craft = Rocket(mouse_pos[0], mouse_pos[1])
                                self.preview_space_craft = None
                            else:
                                if self.preview_new_body == None:
                                    for i in self.bodies:
                                        if i.radius >= np.hypot(i.x - mouse_pos[0], i.y - mouse_pos[1]):
                                            colliding = True
                                    if not colliding:
                                        self.preview_new_body = mouse_pos
                                else:
                                    for i in self.bodies:
                                        if i.radius + np.hypot(mouse_pos[0] - self.preview_new_body[0], mouse_pos[1] - self.preview_new_body[1]) > np.hypot(i.x - self.preview_new_body[0], i.y - self.preview_new_body[1]):
                                            colliding = True
                                    if not colliding:
                                        self.bodies.append(Body(self.preview_new_body[0], self.preview_new_body[1], np.hypot(mouse_pos[0] - self.preview_new_body[0], mouse_pos[1] - self.preview_new_body[1]), [int(np.sin(time.time() + i) * 128 + 128) for i in [0, 1, 2]]))
                                        self.preview_new_body = None
                        
                    if event.button == 2:
                        for b in self.bodies:
                            if np.hypot(mouse_pos[0] - b.x, mouse_pos[1] - b.y) < b.radius:
                                self.dragging_body = b
    
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 2:
                        self.dragging_body = None
                                
                self.cam_input(event)

            self.update(mouse_pos)

            if self.preview_new_body != None:
                x, y = self.to_screen_pos(self.preview_new_body[0], self.preview_new_body[1])
                r = int(np.hypot(mouse_pos[0] - self.preview_new_body[0], mouse_pos[1] - self.preview_new_body[1]) * self.zoom)
                pg.draw.circle(self.screen, [int(np.sin(time.time() + i) * 128 + 128) for i in [0, 1, 2]], (x, y), r)
            if self.preview_space_craft != None:
                self.preview_space_craft = mouse_pos
                x, y = self.to_screen_pos(self.preview_space_craft[0], self.preview_space_craft[1])
                pg.draw.rect(self.screen, [int(np.sin(time.time() + i) * 128 + 128) for i in [0, 1, 2]], (x, y, 100, 100))

            pg.display.flip()
            self.clock.tick(self.FPS)

        pg.quit()

if __name__ == '__main__':
    pg.init()
    app = App()
    app.run()
