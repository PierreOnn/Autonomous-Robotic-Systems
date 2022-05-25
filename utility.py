# Author: Tim Debets

import math
import numpy as np


# Function to calculate distance between two points
def calc_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# Function to determine whether two lines intersect
# Code used from: https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines

# Code used from: https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
# to determine whether the intersection point is actually on the two determined line segments

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    # Check whether the calculated intersection point is actually part of the two line segments
    # we are using to calculate the intersection point
    if ((round(x) < round(max(min(line1[0][0], line1[1][0]), min(line2[0][0], line2[1][0])))) or
            (round(x) > round(min(max(line1[0][0], line1[1][0]), max(line2[0][0], line2[1][0]))))):
        return
    else:
        if ((round(y) < round(max(min(line1[0][1], line1[1][1]), min(line2[0][1], line2[1][1])))) or
                (round(y) > round(min(max(line1[0][1], line1[1][1]), max(line2[0][1], line2[1][1]))))):
            return
        else:
            return x, y


# To determine of a rectangle collides with a circle
# Inspiration from: https://stackoverflow.com/questions/24727773/detecting-rectangle-collision-with-a-circle
def collision(rleft, rtop, width, height,  # rectangle definition
              center_x, center_y, radius):  # circle definition
    """ Detect collision between a rectangle and circle. """

    # complete boundbox of the rectangle
    rright, rbottom = rleft + width, rtop + height

    # bounding box of the circle
    cleft, ctop = center_x - radius, center_y - radius
    cright, cbottom = center_x + radius, center_y + radius

    # trivial reject if bounding boxes do not intersect
    if rright < cleft or rleft > cright or rbottom < ctop or rtop > cbottom:
        return False, 0, 0  # no collision possible

    # check whether any point of rectangle is inside circle's radius
    for x in range(rleft, rleft + width + 1):
        for y in range(rtop, rtop + height + 1):
            # compare distance between circle's center point and each point of
            # the rectangle with the circle's radius
            distance = math.hypot(x - center_x, y - center_y)
            if distance < radius:
                return True, x, y  # collision detected

    # check if center of circle is inside rectangle
    if rleft <= center_x <= rright and rtop <= center_y <= rbottom:
        return True, 0, 0  # overlaid

    return False, 0, 0  # no collision detected


# TODO: use the function with A from the slides
def sensor_output(distance):
    max_output = 100
    min_factor = 0.00
    influence_faraway = 20
    return max_output + ((max_output * min_factor) - max_output) * (1 - math.exp(-distance / influence_faraway))


# calculate the euclidean distance of our population
def euclidean_distance(population):
    total_distance = 0
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            for genome in range(len(population[i])):
                difference = population[i][genome] - population[j][genome]
                total_distance += difference ** 2
    total_distance = np.sqrt(total_distance)
    return total_distance