# Authors: Rick van Bellen, Pierre Onghena, Tim Debets

import pygame
from pygame.locals import *
import settings
import numpy as np
from Sensor import Sensor
from utility import *


# class that defines the robot
class Robot(pygame.sprite.Sprite):
    def __init__(self, radius, nr_sensors):
        super(Robot, self).__init__()
        self.id = 'robot'
        self.surf = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        self.surf.fill((255, 255, 255, 0))
        self.rect = self.surf.get_rect()
        self.rect.move_ip((settings.SCREEN_WIDTH // 2 - radius, settings.SCREEN_HEIGHT // 2 - radius))
        self.Vl = 0  # 1000000
        self.Vr = 0  # 1000000
        self.radius = radius
        self.l = 2 * radius
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.theta = 0.5 * math.pi
        self.sensors = []
        self.vacuum = 0
        self.activation_sensor = 0

        # Put the sensors on the robot evenly distanced from each other
        angles_between_sensors = 2 * math.pi / nr_sensors
        angle = 0
        for i in range(nr_sensors):
            sensor = Sensor(angle, i)
            sensor.id = i + 1
            angle += angles_between_sensors
            self.sensors.append(sensor)

    # Define the robot movement
    def update(self, pressed_keys, walls, dusts):
        # Handle user input
        if pressed_keys[K_w]:
            self.Vl += settings.V_step
        if pressed_keys[K_s]:
            self.Vl -= settings.V_step
        if pressed_keys[K_o]:
            self.Vr += settings.V_step
        if pressed_keys[K_l]:
            self.Vr -= settings.V_step
        if pressed_keys[K_x]:
            self.Vl = 0
            self.Vr = 0
        if pressed_keys[K_t]:
            self.Vl += settings.V_step
            self.Vr += settings.V_step
        if pressed_keys[K_g]:
            self.Vl -= settings.V_step
            self.Vr -= settings.V_step

        # Move the robot, and register positions
        x_old = self.rect.centerx
        y_old = self.rect.centery
        # If the wheels velocities do not match, calculate the angle in which to move
        if self.Vl != self.Vr:
            R = self.radius * (self.Vl + self.Vr) / (self.Vl - self.Vr)
            omega = (self.Vl - self.Vr) / self.l
            ICCx = self.x - R * math.sin(self.theta)
            ICCy = self.y + R * math.cos(self.theta)
            dt = settings.dt
            rotation_matrix = np.array([[math.cos(omega * dt), -math.sin(omega * dt), 0],
                                        [math.sin(omega * dt), math.cos(omega * dt), 0],
                                        [0, 0, 1]])
            difference_matrix = np.array([[self.x - ICCx],
                                          [self.y - ICCy],
                                          [self.theta]])
            ICC_matrix = np.array([[ICCx],
                                   [ICCy],
                                   [omega * dt]])
            new_location = np.matmul(rotation_matrix, difference_matrix) + ICC_matrix
            self.x, self.y, self.theta = new_location[0][0], new_location[1][0], new_location[2][0]
            x_new = self.x
            y_new = self.y

        # If the wheels move at the same velocity, move forward
        else:
            self.x = self.x + self.Vl * math.cos(self.theta) * settings.dt
            self.y = self.y + self.Vl * math.sin(self.theta) * settings.dt
            x_new = self.x
            y_new = self.y

        # Move the robot in the x direction and check for collision
        x_speed = x_new - x_old
        necessary_steps = int(abs(x_speed) // self.l + 1)
        collisionFound = False
        # If the step size is too big, move the robot in multiple smaller steps
        for step in range(necessary_steps):
            self.rect.centerx = x_old + (step + 1) / necessary_steps * x_speed
            for entity in walls:
                intersection = line_intersection([[x_old, y_old], [self.rect.centerx, self.rect.centery]],
                                                 [[entity.rect.left, entity.rect.top],
                                                  [entity.rect.left + entity.rect.width, entity.rect.top]])
                if intersection is not None:
                    if x_speed > 0:
                        self.rect.right = self.rect.right - (self.rect.centerx - intersection[0])
                        self.x = self.rect.centerx
                    if x_speed < 0:
                        self.rect.left = self.rect.left + (intersection[1] - entity.rect.centerx)
                        self.x = self.rect.centerx

                if self.rect.colliderect(entity):
                    collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top, entity.rect.width,
                                                             entity.rect.height,
                                                             self.rect.centerx, self.rect.centery, self.radius)
                    if collisionFound:
                        new_x = self.rect.centerx
                        if x_speed > 0:
                            while collisionFound:
                                new_x = new_x - 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width,
                                                                         entity.rect.height,
                                                                         new_x, self.rect.centery,
                                                                         self.radius)
                            self.rect.right = self.rect.right - (self.rect.centerx - new_x)
                            self.x = self.rect.centerx
                        if x_speed < 0:
                            while collisionFound:
                                new_x = new_x + 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         new_x, self.rect.centery,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.left = self.rect.left + (new_x - self.rect.centerx)
                            self.x = self.rect.centerx
            if collisionFound:
                break

        # Move the robot in the y direction and check for collision
        y_speed = y_new - y_old
        necessary_steps = int(abs(y_speed) // self.l + 1)
        collisionFound = False
        # If the step size is too big, move the robot in multiple smaller steps
        for step in range(necessary_steps):
            self.rect.centery = y_old + (step + 1) / necessary_steps * y_speed
            for entity in walls:
                intersection = line_intersection([[x_old, y_old], [self.rect.centerx, self.rect.centery]],
                                                 [[entity.rect.left, entity.rect.top],
                                                  [entity.rect.left + entity.rect.width, entity.rect.top]])
                if intersection is not None:
                    if y_speed > 0:
                        self.rect.bottom = self.rect.bottom - (self.rect.centery - intersection[1])
                        self.y = self.rect.centery
                    if y_speed < 0:
                        self.rect.top = self.rect.top + (intersection[1] - entity.rect.centery)
                        self.y = self.rect.centery
                if self.rect.colliderect(entity):
                    collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top, entity.rect.width,
                                                             entity.rect.height,
                                                             self.rect.centerx, self.rect.centery, self.radius)
                    if collisionFound:
                        new_y = self.rect.centery
                        if y_speed > 0:
                            while collisionFound:
                                new_y = new_y - 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         self.rect.centerx, new_y,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.bottom = self.rect.bottom - (self.rect.centery - new_y)
                            self.y = self.rect.centery
                        if y_speed < 0:
                            while collisionFound:
                                new_y = new_y + 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         self.rect.centerx, new_y,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.top = self.rect.top + (new_y - self.rect.centery)
                            self.y = self.rect.centery
            if collisionFound:
                break

        # Redraw the line indicating the direction the robot is facing
        radius = self.radius
        self.surf.fill((255, 255, 255, 0))
        pygame.draw.circle(self.surf, (100, 100, 200, 255), (radius, radius), radius)
        pygame.draw.line(self.surf, (0, 0, 0), (radius, radius),
                         (radius + math.cos(self.theta) * radius, radius + math.sin(self.theta) * radius), 5)
        # Recalculate the distances for the sensors
        for sensor in self.sensors:
            sensor.update(walls, self.theta, radius, self.rect)

        # Keep robot on the screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.centerx
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH
            self.x = self.rect.centerx
        if self.rect.top <= 0:
            self.rect.top = 0
            self.y = self.rect.centery
        if self.rect.bottom >= settings.SCREEN_HEIGHT:
            self.rect.bottom = settings.SCREEN_HEIGHT
            self.y = self.rect.centery

        # Retain distance of sensors to shape output
        front_sensors = 0
        right_sensors = 0
        left_sensors = 0
        back_sensors = 0
        for index, value in enumerate(self.sensors, start=1):
            if index == 1:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 2:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 12:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 3:
                right_sensors += round(value.distance - int(self.radius), 0)
            if index == 4:
                right_sensors += round(value.distance - int(self.radius), 0)
            if index == 10:
                left_sensors += round(value.distance - int(self.radius), 0)
            if index == 11:
                left_sensors += round(value.distance - int(self.radius), 0)
            if index == 5:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 6:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 8:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 9:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 10:
                back_sensors += round(value.distance - int(self.radius), 0)

                # Calculate behaviour of robot relative to walls
                self.activation_sensor = round(sensor_output(front_sensors) +
                                             0.2 * sensor_output(right_sensors) + 0.2 * sensor_output(left_sensors)
                                               + 0.5 * sensor_output(back_sensors))

        # Check for collision with dust
        for entity in dusts:
            if self.rect.colliderect(entity):
                self.vacuum += 1
                entity.kill()



    def update_from_network(self, network, walls, dusts):
        # Compute network output
        x = [sensor_output(sensor.distance) for sensor in self.sensors]
        output = network.feed_forward(x)
        self.Vl = output[0] * settings.MAX_VELOCITY
        self.Vr = output[1] * settings.MAX_VELOCITY

        # Move the robot, and register positions
        x_old = self.rect.centerx
        y_old = self.rect.centery
        # If the wheels velocities do not match, calculate the angle in which to move
        if self.Vl != self.Vr:
            R = self.radius * (self.Vl + self.Vr) / (self.Vl - self.Vr)
            omega = (self.Vl - self.Vr) / self.l
            ICCx = self.x - R * math.sin(self.theta)
            ICCy = self.y + R * math.cos(self.theta)
            dt = settings.dt
            rotation_matrix = np.array([[math.cos(omega * dt), -math.sin(omega * dt), 0],
                                        [math.sin(omega * dt), math.cos(omega * dt), 0],
                                        [0, 0, 1]])
            difference_matrix = np.array([[self.x - ICCx],
                                          [self.y - ICCy],
                                          [self.theta]])
            ICC_matrix = np.array([[ICCx],
                                   [ICCy],
                                   [omega * dt]])
            new_location = np.matmul(rotation_matrix, difference_matrix) + ICC_matrix
            self.x, self.y, self.theta = new_location[0][0], new_location[1][0], new_location[2][0]
            x_new = self.x
            y_new = self.y

        # If the wheels move at the same velocity, move forward
        else:
            self.x = self.x + self.Vl * math.cos(self.theta) * settings.dt
            self.y = self.y + self.Vl * math.sin(self.theta) * settings.dt
            x_new = self.x
            y_new = self.y

        # Move the robot in the x direction and check for collision
        x_speed = x_new - x_old
        necessary_steps = int(abs(x_speed) // self.l + 1)
        collisionFound = False
        # If the step size is too big, move the robot in multiple smaller steps
        for step in range(necessary_steps):
            self.rect.centerx = x_old + (step + 1) / necessary_steps * x_speed
            for entity in walls:
                intersection = line_intersection([[x_old, y_old], [self.rect.centerx, self.rect.centery]],
                                                 [[entity.rect.left, entity.rect.top],
                                                  [entity.rect.left + entity.rect.width, entity.rect.top]])
                if intersection is not None:
                    if x_speed > 0:
                        self.rect.right = self.rect.right - (self.rect.centerx - intersection[0])
                        self.x = self.rect.centerx
                    if x_speed < 0:
                        self.rect.left = self.rect.left + (intersection[1] - entity.rect.centerx)
                        self.x = self.rect.centerx

                if self.rect.colliderect(entity):
                    collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top, entity.rect.width,
                                                             entity.rect.height,
                                                             self.rect.centerx, self.rect.centery, self.radius)
                    if collisionFound:
                        new_x = self.rect.centerx
                        if x_speed > 0:
                            while collisionFound:
                                new_x = new_x - 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width,
                                                                         entity.rect.height,
                                                                         new_x, self.rect.centery,
                                                                         self.radius)
                            self.rect.right = self.rect.right - (self.rect.centerx - new_x)
                            self.x = self.rect.centerx
                        if x_speed < 0:
                            while collisionFound:
                                new_x = new_x + 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         new_x, self.rect.centery,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.left = self.rect.left + (new_x - self.rect.centerx)
                            self.x = self.rect.centerx
            if collisionFound:
                break

        # Move the robot in the y direction and check for collision
        y_speed = y_new - y_old
        necessary_steps = int(abs(y_speed) // self.l + 1)
        collisionFound = False
        # If the step size is too big, move the robot in multiple smaller steps
        for step in range(necessary_steps):
            self.rect.centery = y_old + (step + 1) / necessary_steps * y_speed
            for entity in walls:
                intersection = line_intersection([[x_old, y_old], [self.rect.centerx, self.rect.centery]],
                                                 [[entity.rect.left, entity.rect.top],
                                                  [entity.rect.left + entity.rect.width, entity.rect.top]])
                if intersection is not None:
                    # dist =
                    if y_speed > 0:
                        self.rect.bottom = self.rect.bottom - (self.rect.centery - intersection[1])
                        self.y = self.rect.centery
                    if y_speed < 0:
                        self.rect.top = self.rect.top + (intersection[1] - entity.rect.centery)
                        self.y = self.rect.centery
                if self.rect.colliderect(entity):
                    collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top, entity.rect.width,
                                                             entity.rect.height,
                                                             self.rect.centerx, self.rect.centery, self.radius)
                    if collisionFound:
                        new_y = self.rect.centery
                        if y_speed > 0:
                            while collisionFound:
                                new_y = new_y - 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         self.rect.centerx, new_y,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.bottom = self.rect.bottom - (self.rect.centery - new_y)
                            self.y = self.rect.centery
                        if y_speed < 0:
                            while collisionFound:
                                new_y = new_y + 1
                                collisionFound, x_col, y_col = collision(entity.rect.left, entity.rect.top,
                                                                         entity.rect.width, entity.rect.height,
                                                                         self.rect.centerx, new_y,
                                                                         self.radius)
                            collisionFound = True
                            self.rect.top = self.rect.top + (new_y - self.rect.centery)
                            self.y = self.rect.centery
            if collisionFound:
                break

        self.surf.fill((255, 255, 255, 0))
        pygame.draw.circle(self.surf, (100, 100, 200, 255), (self.radius, self.radius), self.radius)
        pygame.draw.line(self.surf, (0, 0, 0), (self.radius, self.radius),
                         (self.radius + math.cos(self.theta) * self.radius,
                          self.radius + math.sin(self.theta) * self.radius), 5)
        # Recalculate the distances for the sensors
        for sensor in self.sensors:
            sensor.update(walls, self.theta, self.radius, self.rect)

        # Keep robot on the screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.centerx
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH
            self.x = self.rect.centerx
        if self.rect.top <= 0:
            self.rect.top = 0
            self.y = self.rect.centery
        if self.rect.bottom >= settings.SCREEN_HEIGHT:
            self.rect.bottom = settings.SCREEN_HEIGHT
            self.y = self.rect.centery

        # Retain distance of sensors to shape output
        front_sensors = 0
        right_sensors = 0
        left_sensors = 0
        back_sensors = 0
        for index, value in enumerate(self.sensors, start=1):
            if index == 1:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 2:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 12:
                front_sensors += round(value.distance - int(self.radius), 0)
            if index == 3:
                right_sensors += round(value.distance - int(self.radius), 0)
            if index == 4:
                right_sensors += round(value.distance - int(self.radius), 0)
            if index == 10:
                left_sensors += round(value.distance - int(self.radius), 0)
            if index == 11:
                left_sensors += round(value.distance - int(self.radius), 0)
            if index == 5:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 6:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 8:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 9:
                back_sensors += round(value.distance - int(self.radius), 0)
            if index == 10:
                back_sensors += round(value.distance - int(self.radius), 0)

                # Calculate behaviour of robot relative to walls
                self.activation_sensor = round(sensor_output(front_sensors) +
                                                0.2 * sensor_output(right_sensors) + 0.2 * sensor_output(left_sensors)
                                                   + 0.5 * sensor_output(back_sensors))

        # Check for collision with dust
        for entity in dusts:
            if self.rect.colliderect(entity):
                self.vacuum += 1
                entity.kill()