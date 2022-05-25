# Author: Tim Debets

import settings
from utility import *


# Sensor class
class Sensor:
    def __init__(self, angle, id):
        super(Sensor, self).__init__()
        self.angle = angle
        self.id = id
        self.distance = settings.MAX_SENSOR_DIST

    # Update the sensors
    def update(self, sprites, theta, radius, rect):
        top_left_robot = rect.topleft
        robot_center = rect.center
        self.distance = settings.MAX_SENSOR_DIST
        # Calculate the distance to all the walls which can be sensed by the sensor
        for entity in sprites:
            if entity.id != 'robot':
                topleft = entity.rect.topleft
                topright = entity.rect.topright
                bottomleft = entity.rect.bottomleft
                bottomright = entity.rect.bottomright

                # sensor_start = [top_left_robot[0] + radius + math.cos(theta + self.angle) * radius,
                #                 top_left_robot[1] + radius + math.sin(theta + self.angle) * radius]

                # To calculate intersections, create 5 lines: One for the sensor and four that
                # represent the edges of a wall
                sensor_start = [robot_center[0], robot_center[1]]

                sensor_end = [
                    top_left_robot[0] + radius + math.cos(theta + self.angle) * (radius + settings.MAX_SENSOR_DIST),
                    top_left_robot[1] + radius + math.sin(theta + self.angle) * (radius + settings.MAX_SENSOR_DIST)]

                sensor_line = [sensor_start, sensor_end]
                top_entity_line = [[topleft[0], topleft[1]], [topright[0], topright[1]]]
                right_entity_line = [[topright[0], topright[1]], [bottomright[0], bottomright[1]]]
                bottom_entity_line = [[bottomleft[0], bottomleft[1]], [bottomright[0], bottomright[1]]]
                left_entity_line = [[topleft[0], topleft[1]], [bottomleft[0], bottomleft[1]]]

                # Check whether sensor can sense the edges of a wall
                sensor_top_int = line_intersection(sensor_line, top_entity_line)
                sensor_right_int = line_intersection(sensor_line, right_entity_line)
                sensor_bottom_int = line_intersection(sensor_line, bottom_entity_line)
                sensor_left_int = line_intersection(sensor_line, left_entity_line)

                # If a sensor can sense an edge, calculate the distance towards this edge and use the minimum value
                if sensor_top_int:
                    distance = calc_distance([sensor_start[0], sensor_start[1]],
                                             [sensor_top_int[0], sensor_top_int[1]])
                    if distance < self.distance:
                        self.distance = distance
                if sensor_right_int:
                    distance = calc_distance([sensor_start[0], sensor_start[1]],
                                             [sensor_right_int[0], sensor_right_int[1]])
                    if distance < self.distance:
                        self.distance = distance
                if sensor_bottom_int:
                    distance = calc_distance([sensor_start[0], sensor_start[1]],
                                             [sensor_bottom_int[0], sensor_bottom_int[1]])
                    if distance < self.distance:
                        self.distance = distance
                if sensor_left_int:
                    distance = calc_distance([sensor_start[0], sensor_start[1]],
                                             [sensor_left_int[0], sensor_left_int[1]])
                    if distance < self.distance:
                        self.distance = distance
