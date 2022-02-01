from math import atan, cos, degrees, pi, radians, sin

import pygame

from database import models
from game.utilities import blit_rotate_center


class Car:
    def __init__(self, car_id, start_position):
        lookup_car = models.Car.get(models.Car.car_id == car_id)
        self.car_id = lookup_car.car_id
        self.car_name = lookup_car.car_name
        self.car_path = lookup_car.car_path
        self.max_vel = lookup_car.max_vel
        self.rotation_vel = lookup_car.rotation_vel
        self.acceleration = lookup_car.acceleration / 10

        self.car_image = pygame.image.load(self.car_path)

        self.vel = 0
        self.angle = 0

        self.start_position = start_position
        self.x, self.y = self.start_position

    def draw(self, win):
        blit_rotate_center(win, self.car_image, (self.x, self.y), self.angle)

    def move(self):
        vertical = cos(radians(self.angle)) * self.vel
        horizontal = sin(radians(self.angle)) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.car_image)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.start_position
        self.angle = 0
        self.vel = 0


class PlayerCar(Car):
    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel / 2
        self.move()

    def move_player(self):
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_vel
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_vel
        if keys[pygame.K_UP]:
            moved = True
            self.vel = min(self.vel + self.acceleration, self.max_vel)
            self.move()
        if keys[pygame.K_DOWN]:
            moved = True
            self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
            self.move()

        if not moved:
            self.vel = max(self.vel - self.acceleration / 2, 0)
            self.move()


# Path_new is to be swapped with path when complete
class ComputerCar(Car):
    def __init__(self, car_id, start_position, path, track_record):
        super().__init__(car_id, start_position)
        self.path = path
        self.current_point = 0
        self.track_record = track_record
        self.vel = self.max_vel // 1.25

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), (point.path_x, point.path_y), 5)

    def draw(self, win):
        super().draw(win)

    def calculate_angle(self):
        target_x = list(self.path)[self.current_point].path_x
        target_y = list(self.path)[self.current_point].path_y
        x_delta = target_x - self.x
        y_delta = target_y - self.y

        if y_delta == 0:
            desired_angle = pi / 2
        else:
            desired_angle = atan(x_delta / y_delta)

        if target_y > self.y:
            desired_angle += pi

        difference_in_angle = self.angle - degrees(desired_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = list(self.path)[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.car_image.get_width(), self.car_image.get_height()
        )

        if rect.collidepoint(target.path_x, target.path_y):
            self.current_point += 1

    def move(self):
        if self.current_point < len(self.path):
            self.calculate_angle()
            self.update_path_point()
            super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0
