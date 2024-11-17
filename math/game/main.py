import sys
import pygame
from math import atan2, cos, pi, sin, sqrt
from random import randint, uniform
import numpy as np


def standard_form(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    a = y2 - y1
    b = x1 - x2
    c = x1 * y2 - y1 * x2
    return a, b, c


def intersection(u1, u2, v1, v2):
    a1, b1, c1 = standard_form(u1, u2)
    a2, b2, c2 = standard_form(v1, v2)
    m = np.array(((a1, b1), (a2, b2)))
    c = np.array((c1, c2))
    return np.linalg.solve(m, c)


def subtract(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])


def distance(v1, v2):
    return length(subtract(v1, v2))


def segment_checks(s1, s2):
    u1, u2 = s1
    v1, v2 = s2
    l1, l2 = distance(*s1), distance(*s2)
    x, y = intersection(u1, u2, v1, v2)
    return [
        distance(u1, (x, y)) <= l1,
        distance(u2, (x, y)) <= l1,
        distance(v1, (x, y)) <= l2,
        distance(v2, (x, y)) <= l2
    ]


def do_segments_intersect(s1, s2):
    u1, u2 = s1
    v1, v2 = s2
    d1, d2 = distance(*s1), distance(*s2)
    try:
        x, y = intersection(u1, u2, v1, v2)
        return (distance(u1, (x, y)) <= d1 and
                distance(u2, (x, y)) <= d1 and
                distance(v1, (x, y)) <= d2 and
                distance(v2, (x, y)) <= d2)
    except np.linalg.linalg.LinAlgError:
        return False


def length(v):
    return sqrt(v[0]**2 + v[1]**2)


def to_polar(vector):
    x, y = vector[0], vector[1]
    angle = atan2(y, x)
    return (length(vector), angle)


def add(*vectors):
    return (sum([v[0] for v in vectors]), sum([v[1] for v in vectors]))


def to_cartesian(polar_vector):
    length, angle = polar_vector[0], polar_vector[1]
    return (length*cos(angle), length*sin(angle))


def rotate2d(angle, vector):
    l, a = to_polar(vector)
    return to_cartesian((l, a+angle))


class PlygonModel():
    def __init__(self, points):
        self.points = points
        self.rotation_angle = 0
        self.x = 0
        self.y = 0

    def transformed(self):
        rotated = [rotate2d(self.rotation_angle, v) for v in self.points]
        return [add((self.x, self.y), v) for v in rotated]

    def does_intersect(self, other_segment):
        for segment in self.segments():
            if do_segments_intersect(other_segment, segment):
                return True
        return False
    
    def segments(self):
        point_count = len(self.points)
        points = self.transformed()
        return [(points[i], points[(i+1)%point_count])
                for i in range(0,point_count)]


class Ship(PlygonModel):
    def __init__(self):
        super().__init__([(0.5, 0), (-0.25, 0.25), (-0.25, -0.25)])

    def laser_segment(self):
        dist = 20. * sqrt(2)
        x, y = self.transformed()[0]
        return (x, y), (x + dist * cos(self.rotation_angle), y + dist*sin(self.rotation_angle))


class Asteroid(PlygonModel):
    def __init__(self):
        sides = randint(5, 9)
        vs = [to_cartesian((uniform(0.5, 1.0), 2*pi*i/sides))
              for i in range(0, sides)]
        super().__init__(vs)


ship = Ship()

asteroid_count = 10
asteroids = [Asteroid() for _ in range(0, asteroid_count)]

for ast in asteroids:
    ast.x = randint(-9, 9)
    ast.y = randint(-9, 9)

GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)

width, height = 400, 400


def to_pixels(x, y):
    return (width/2 + width * x / 20, height/2 - height * y / 20)


def draw_poly(screen, polygon_model, color=GREEN):
    pixel_points = [to_pixels(x, y) for x, y in polygon_model.transformed()]
    pygame.draw.aalines(screen, color, True, pixel_points, 10)


def draw_segment(screen, v1, v2, color=RED):
    pygame.draw.aaline(screen, color, to_pixels(*v1), to_pixels(*v2), 10)


def main():

    pygame.init()

    screen = pygame.display.set_mode([width, height])

    pygame.display.set_caption("Asteroids!")

    done = False
    clock = pygame.time.Clock()

    # p key prints screenshot (you can ignore this variable)
    p_pressed = False

    while not done:

        clock.tick()

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        # UPDATE THE GAME STATE

        milliseconds = clock.get_time()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            ship.rotation_angle += milliseconds * (2*pi / 1000)

        if keys[pygame.K_RIGHT]:
            ship.rotation_angle -= milliseconds * (2*pi / 1000)

        laser = ship.laser_segment()

        # p key saves screenshot (you can ignore this)
        if keys[pygame.K_p] and screenshot_mode:
            p_pressed = True
        elif p_pressed:
            pygame.image.save(
                screen, 'figures/asteroid_screenshot_%d.png' % milliseconds)
            p_pressed = False

        # DRAW THE SCENE

        screen.fill(WHITE)

        if keys[pygame.K_SPACE]:
            draw_segment(screen, *laser)

        draw_poly(screen, ship)

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
