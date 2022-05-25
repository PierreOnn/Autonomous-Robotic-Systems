# Authors: Rick van Bellen, Tim Debets, Pierre Onghena
import pygame
from pygame.locals import *
from Robot import Robot
from Wall import Wall
from Dust import Dust
import settings
import math


def network_play(network, show, training_time_steps, room_type, generation):
    # Initialize pygame
    pygame.init()

    # Create robot object, walls and dust
    all_sprites = pygame.sprite.Group()
    robot = Robot(20, 12)
    all_sprites.add(robot)
    walls = pygame.sprite.Group()

    if room_type == "default":
        wall = Wall(250, 400, 5, 500)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(750, 400, 5, 500)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(500, 150, 504, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(500, 650, 504, 5)
        walls.add(wall)
        all_sprites.add(wall)

    elif room_type == "train":
        wall = Wall(50, 450, 5, 600)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(750, 450, 5, 600)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 150, 700, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 750, 700, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(200, 450, 5, 300)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(300, 300, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(300, 600, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 450, 5, 300)
        walls.add(wall)
        all_sprites.add(wall)

    elif room_type == "test":
        wall = Wall(200, 250, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(350, 300, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(450, 350, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(550, 300, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(700, 250, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(850, 450, 5, 400)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(700, 650, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(550, 600, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(450, 550, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(350, 600, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(200, 650, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(50, 450, 5, 400)
        walls.add(wall)
        all_sprites.add(wall)


    dusts = pygame.sprite.Group()
    for x in range(20, settings.SCREEN_HEIGHT, 40):
        for y in range(20, settings.SCREEN_HEIGHT, 40):
            dust = Dust(x, y)
            dusts.add(dust)
            all_sprites.add(dust)

    # History lists are for tracking movement of robot
    history_x = []
    history_y = []

    if show:
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        # Setup the clock to fix framerate
        clock = pygame.time.Clock()
        # For printing numbers:
        font = pygame.font.SysFont("Courier New", 14)

    # Do a number of time steps
    for i in range(training_time_steps):
        history_x.append(robot.x)
        history_y.append(robot.y)
        robot.update_from_network(network, walls, dusts)

        if show:
            # Fill the screen with white
            screen.fill((255, 255, 255))

            # Draw the route of the robot
            for i in range(len(history_x)):
                pygame.draw.circle(screen, (244, 235, 149), (history_x[i], history_y[i]), robot.radius)

            # Draw all entities
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)

            # Get everything ready to draw the text on the screen
            # Wheel speed + sensor distance
            text_areas = []
            text_rects = []

            top_left = robot.rect.topleft
            radius = robot.l // 2

            # Get speed of the wheels to print on screen
            left_wheel = robot.Vl
            right_wheel = robot.Vr
            left_wheel_text = font.render("Speed left wheel:  " + (str(round(left_wheel))), True, (0, 0, 0))
            text_areas.append(left_wheel_text)
            text_rect_left = left_wheel_text.get_rect()
            text_rect_left.left = 10
            text_rect_left.centery = 10
            text_rects.append(text_rect_left)
            right_wheel_text = font.render("Speed right wheel: " + (str(round(right_wheel))), True, (0, 0, 0))
            text_areas.append(right_wheel_text)
            text_rect_right = right_wheel_text.get_rect()
            text_rect_right.left = 10
            text_rect_right.centery = 30
            text_rects.append(text_rect_right)

            # Get sensor distance to print on screen
            for sensor in robot.sensors:
                text = font.render(str(round(sensor.distance) - radius), True, (0, 0, 0))
                text_areas.append(text)
                text_rect = text.get_rect()
                text_rect.center = (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * (radius + 20),
                                    top_left[1] + radius + math.sin(robot.theta + sensor.angle) * (radius + 20))
                text_rects.append(text_rect)

                # If instead you want to draw the lines of the sensor, comment above and uncomment below
                # pygame.draw.line(screen, (0, 255, 0),
                #                  (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * radius,
                #                   top_left[1] + radius + math.sin(robot.theta + sensor.angle) * radius),
                #                  (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * (int(sensor.distance)),
                #                   top_left[1] + radius + math.sin(robot.theta + sensor.angle) * (
                #                       int(sensor.distance))), 2)

            # Get collected dust to print on screen
            collected_dust = robot.vacuum
            collected_dust_text = font.render("Collected dust:  " + (str(round(collected_dust))), True, (0, 0, 0))
            text_areas.append(collected_dust_text)
            text_rect_dust = collected_dust_text.get_rect()
            text_rect_dust.left = 10
            text_rect_dust.centery = 60
            text_rects.append(text_rect_dust)

            # Get activation level sensors to print on screen
            activation_level = robot.activation_sensor
            activation_level_text = font.render("Sensor activation:  " + (str(round(activation_level))), True,
                                                (0, 0, 0))
            text_areas.append(activation_level_text)
            text_rect_activation = activation_level_text.get_rect()
            text_rect_activation.left = 10
            text_rect_activation.centery = 80
            text_rects.append(text_rect_activation)

            # Write the needed text on the screen
            for i in range(len(text_areas)):
                screen.blit(text_areas[i], text_rects[i])

            # Update the screen
            pygame.display.flip()

            # Maintain 30 fps
            clock.tick(settings.fps)

    if show:
        pygame.image.save(screen, f"screenshot_{room_type}{generation}.png")

    return robot.vacuum - robot.activation_sensor


def manual_play(room_type):
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # Create robot object, walls and dust
    all_sprites = pygame.sprite.Group()
    robot = Robot(20, 12)
    all_sprites.add(robot)
    walls = pygame.sprite.Group()

    if room_type == "default":
        wall = Wall(250, 400, 5, 500)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(750, 400, 5, 500)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(500, 150, 504, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(500, 650, 504, 5)
        walls.add(wall)
        all_sprites.add(wall)

    elif room_type == "train":
        wall = Wall(50, 450, 5, 600)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(750, 450, 5, 600)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 150, 700, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 750, 700, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(200, 450, 5, 300)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(300, 300, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(300, 600, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(400, 450, 5, 300)
        walls.add(wall)
        all_sprites.add(wall)

    elif room_type == "test":
        wall = Wall(200, 250, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(350, 300, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(450, 350, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(550, 300, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(700, 250, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(850, 450, 5, 400)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(700, 650, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(550, 600, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(450, 550, 200, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(350, 600, 5, 100)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(200, 650, 300, 5)
        walls.add(wall)
        all_sprites.add(wall)
        wall = Wall(50, 450, 5, 400)
        walls.add(wall)
        all_sprites.add(wall)

    dusts = pygame.sprite.Group()
    for x in range(20, settings.SCREEN_HEIGHT, 40):
        for y in range(20, settings.SCREEN_HEIGHT, 40):
            dust = Dust(x, y)
            dusts.add(dust)
            all_sprites.add(dust)

    # Variable to keep the main loop running
    running = True

    # Setup the clock to fix framerate
    clock = pygame.time.Clock()

    # For printing numbers:
    font = pygame.font.SysFont("Courier New", 14)

    # History lists for the route of the robot
    history_x = []
    history_y = []

    # Main game loop
    while running:
        history_x.append(robot.x)
        history_y.append(robot.y)
        # Look at every event in the queue
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If the user hit escape, stop the program
                if event.key == K_ESCAPE:
                    running = False

            # If the user closed the window, stop the program
            elif event.type == QUIT:
                running = False

        # Get the set of keys pressed and check for user input, update accordingly
        pressed_keys = pygame.key.get_pressed()
        robot.update(pressed_keys, walls, dusts)

        # Fill the screen with white
        screen.fill((255, 255, 255))

        # Draw the route of the robot
        x_path = []
        y_path = []
        for i in range(len(history_x)):
            surface = pygame.draw.circle(screen, (244, 235, 149), (history_x[i], history_y[i]), robot.radius)
            x_path.append(surface[0])
            y_path.append(surface[1])

        # Draw all entities
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Get everything ready to draw the text on the screen
        # Wheel speed + sensor distance + collected dust
        text_areas = []
        text_rects = []

        top_left = robot.rect.topleft
        radius = robot.l // 2

        # Get speed of the wheels to print on screen
        left_wheel = robot.Vl
        right_wheel = robot.Vr
        left_wheel_text = font.render("Speed left wheel:  " + (str(round(left_wheel, 2))), True, (0, 0, 0))
        text_areas.append(left_wheel_text)
        text_rect_left = left_wheel_text.get_rect()
        text_rect_left.left = 10
        text_rect_left.centery = 10
        text_rects.append(text_rect_left)
        right_wheel_text = font.render("Speed right wheel: " + (str(round(right_wheel, 2))), True, (0, 0, 0))
        text_areas.append(right_wheel_text)
        text_rect_right = right_wheel_text.get_rect()
        text_rect_right.left = 10
        text_rect_right.centery = 30
        text_rects.append(text_rect_right)

        # Get sensor distance to print on screen
        for sensor in robot.sensors:
            text = font.render(str(round(sensor.distance) - radius), True, (0, 0, 0))
            text_areas.append(text)
            text_rect = text.get_rect()
            text_rect.center = (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * (radius + 20),
                                top_left[1] + radius + math.sin(robot.theta + sensor.angle) * (radius + 20))
            text_rects.append(text_rect)

            # If instead you want to draw the lines of the sensor, comment above and uncomment below
            # pygame.draw.line(screen, (0, 255, 0),
            #                  (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * radius,
            #                   top_left[1] + radius + math.sin(robot.theta + sensor.angle) * radius),
            #                  (top_left[0] + radius + math.cos(robot.theta + sensor.angle) * (int(sensor.distance)),
            #                   top_left[1] + radius + math.sin(robot.theta + sensor.angle) * (
            #                       int(sensor.distance))), 2)

        # Get collected dust to print on screen
        collected_dust = robot.vacuum
        collected_dust_text = font.render("Collected dust:  " + (str(round(collected_dust))), True, (0, 0, 0))
        text_areas.append(collected_dust_text)
        text_rect_dust = collected_dust_text.get_rect()
        text_rect_dust.left = 10
        text_rect_dust.centery = 60
        text_rects.append(text_rect_dust)

        # Get activation level sensors to print on screen
        activation_level = robot.activation_sensor
        activation_level_text = font.render("Sensor activation:  " + (str(round(activation_level))), True, (0, 0, 0))
        text_areas.append(activation_level_text)
        text_rect_activation = activation_level_text.get_rect()
        text_rect_activation.left = 10
        text_rect_activation.centery = 80
        text_rects.append(text_rect_activation)

        # Write the needed text on the screen
        for i in range(len(text_areas)):
            screen.blit(text_areas[i], text_rects[i])


        # Update the screen
        pygame.display.flip()

        # Maintain 30 fps
        clock.tick(settings.fps)


if __name__ == "__main__":
    manual_play("test")
