import sys
import pygame
from math import atan2, cos, pi, sin, sqrt
from random import randint, uniform

def length(v):
    return sqrt(v[0]**2 + v[1]**2)

def to_polar(vector):
    x, y = vector[0], vector[1]
    angle = atan2(y,x)
    return (length(vector), angle)

def add(*vectors):
    return (sum([v[0] for v in vectors]), sum([v[1] for v in vectors]))

def to_cartesian(polar_vector):
    length, angle = polar_vector[0], polar_vector[1]
    return (length*cos(angle), length*sin(angle)) 

def rotate2d(angle, vector):
    l,a = to_polar(vector)
    return to_cartesian((l, a+angle))

class PlygonModel():
    def __init__(self, points):
        self.points = points
        self.rotation_angle = 0
        self.x = 0
        self.y = 0

    def transformed(self):
        rotated = [rotate2d(self.rotation_angle, v) for v in self.points]
        return [add((self.x,self.y),v) for v in rotated]


class Ship(PlygonModel):
    def __init__(self):
        super().__init__([(0.5, 0), (-0.25, 0.25), (-0.25, -0.25)])    
        
class Asteroid(PlygonModel):
    def __init__(self):
        sides = randint(5, 9)
        vs = [to_cartesian((uniform(0.5,1.0), 2*pi*i/sides)) for i in range(0, sides)]
        super().__init__(vs)
        
ship = Ship()

asteroid_count = 10
asteroids = [Asteroid() for _ in range(0, asteroid_count)]

for ast in asteroids:
    ast.x= randint(-9,9)
    ast.y= randint(-9,9)
    
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

width, height = 400, 400

def to_pixels(x,y):
    return (width/2 + width * x / 20, height/2 - height * y / 20)

def draw_poly(screen, polygon_model, color=GREEN):
    pixel_points = [to_pixels(x,y) for x,y in polygon_model.transformed()]
    pygame.draw.aalines(screen, color, True, pixel_points, 10)

def main():


    pygame.init()


    screen = pygame.display.set_mode([width,height])

    pygame.display.set_caption("Asteroids!")

    done = False
    clock = pygame.time.Clock()

    # p key prints screenshot (you can ignore this variable)
    p_pressed = False

    while not done:

        clock.tick()

        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop

        # UPDATE THE GAME STATE

        milliseconds = clock.get_time()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            ship.rotation_angle += milliseconds * (2*pi / 1000)

        if keys[pygame.K_RIGHT]:
            ship.rotation_angle -= milliseconds * (2*pi / 1000)

        # p key saves screenshot (you can ignore this)
        if keys[pygame.K_p] and screenshot_mode:
            p_pressed = True
        elif p_pressed:
            pygame.image.save(screen, 'figures/asteroid_screenshot_%d.png' % milliseconds)
            p_pressed = False

        # DRAW THE SCENE

        screen.fill(WHITE)

        draw_poly(screen,ship)

        for asteroid in asteroids:
            if keys[pygame.K_SPACE] and asteroid.does_intersect(laser):
                asteroids.remove(asteroid)
            else:
                draw_poly(screen, asteroid, color=GREEN)


        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    if '--screenshot' in sys.argv:
        screenshot_mode = True
    main()