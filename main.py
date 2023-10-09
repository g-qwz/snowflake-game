import random
from enum import Enum
from io import BytesIO

import pygame
import cairosvg

pygame.init()
info_object = pygame.display.Info()


class Direction(Enum):
    DOWN = [1, 1]
    RIGHT = [0, 1]
    UP = [1, -1]
    LEFT = [0, -1]


def create_screen(
        width=info_object.current_w,
        height=info_object.current_h
        ) -> tuple:
    return (width, height)


GAME_TITLE = "Snowflake Game"
GAME_WINDOW_SIZE = create_screen()
GAME_BACKGROUND_COLOR = (0, 0, 0)
GAME_TICKS = 20
GAME_BORDER_START = 10
GAME_BORDER_END = 50
SNOWFLAKE_FILE_NAME = "snowflake.svg"
SNOWFLAKE_COLOR = (255, 255, 255)
SNOWFLAKE_COUNT = 90
SNOWFLAKE_WIDTH = 25
SNOWFLAKE_HEIGHT = 25
SNOWFLAKE_DIRECTION: Direction = Direction.UP
SNOWFLAKE_VELOCITY = 5
SNOWFLAKE_ROTATIONS = True
SNOWFLAKE_ROTATION_SPEED = 30


def check_tuple(
        item: object,
        item_name: str,
        length: int,
        color: bool = False
        ):
    should_exit = False

    if type(item) is not tuple or len(item) != length:
        should_exit = True
    if color:
        for value in item:
            if value > 255:
                should_exit = True
                break

    if should_exit:
        exit(item_name + " is not valid!")


def check_int(item: object, item_name: str, max_size: int = None):
    should_exit = False

    if type(item) is not int:
        should_exit = True
    elif max_size is not None and item > max_size:
        should_exit = True

    if should_exit:
        exit(item_name + " is not valid!")


check_tuple(GAME_WINDOW_SIZE, "Window Size", 2)
check_tuple(GAME_BACKGROUND_COLOR, "Background Color", 3, True)
check_tuple(SNOWFLAKE_COLOR, "Snowflake Color", 3, True)
check_int(GAME_TICKS, "Game Ticks")
check_int(SNOWFLAKE_COUNT, "Snowflake Count")
check_int(SNOWFLAKE_WIDTH, "Snowflake Width", 500)
check_int(SNOWFLAKE_HEIGHT, "Snowflake Height", 500)
check_int(SNOWFLAKE_VELOCITY, "Snowflake Velocity")

if type(SNOWFLAKE_ROTATIONS) is not bool:
    exit("Snowflake Rotation is not valid!")

if type(SNOWFLAKE_DIRECTION) is not Direction:
    exit("Snowflake Direction is not valid!")


class Game:
    def __init__(self):
        self.transformed_snowflake = None
        self.clock = pygame.time.Clock()
        self.angle = 0
        self.rotation_speed = SNOWFLAKE_ROTATION_SPEED / 100

        self.window = pygame.display.set_mode(GAME_WINDOW_SIZE)
        pygame.display.set_caption(str(GAME_TITLE))

        self.snowfall = self.initialize_snowflakes()
        self.load_snowflake_image()

    def initialize_snowflakes(self):
        snowfall = []
        for _ in range(SNOWFLAKE_COUNT):
            x = random.randrange(
                GAME_BORDER_START,
                self.window.get_width() - (
                    (GAME_BORDER_END if (self.window.get_width() > 70) else 0)
                    if SNOWFLAKE_DIRECTION.value[0] == 1 else 0
                )
            )
            y = random.randrange(
                GAME_BORDER_START,
                self.window.get_height() - (
                    (GAME_BORDER_END if (self.window.get_height() > 70) else 0)
                    if SNOWFLAKE_DIRECTION.value[0] == 0 else 0
                )
            )
            snowfall.append([x, y])
        return snowfall

    def load_snowflake_image(self):
        try:
            with open(SNOWFLAKE_FILE_NAME, "r") as snowflake_file:
                hex_color = "#{:02x}{:02x}{:02x}".format(*SNOWFLAKE_COLOR)
                snowflake = snowflake_file.read().replace(
                    "#000000",
                    hex_color
                )
                transformed_data = cairosvg.svg2png(
                    bytestring=snowflake,
                    output_height=SNOWFLAKE_HEIGHT,
                    output_width=SNOWFLAKE_WIDTH
                )
                self.transformed_snowflake = pygame.image.load(
                    BytesIO(transformed_data)
                )
        except FileNotFoundError:
            print(f"The file '{SNOWFLAKE_FILE_NAME}' does not exist.")

    def update_snowflakes(self):
        direction_axis = SNOWFLAKE_DIRECTION.value[0]
        direction_value = SNOWFLAKE_DIRECTION.value[1]
        direction_axis_opposite = 1 if direction_axis == 0 else 0

        window_direction_value = (
            self.window.get_height() if direction_axis == 1
            else self.window.get_width()
        )
        window_direction_value_opposite = (
            self.window.get_width() if direction_axis == 1
            else self.window.get_height()
        )

        limit = (
            [-50, -10]
            if direction_value > 0
            else [window_direction_value - 10, window_direction_value]
        )

        for snowflake in self.snowfall:
            snowflake[direction_axis] += direction_value * SNOWFLAKE_VELOCITY
            if (
                    (snowflake[direction_axis] >= window_direction_value)
                    if direction_value > 0
                    else (snowflake[direction_axis] <= 0)
            ):
                snowflake[direction_axis_opposite] = random.randrange(
                    GAME_BORDER_START,
                    window_direction_value_opposite - (
                        GAME_BORDER_END if (
                            self.window.get_width() > 70
                            or self.window.get_height() > 70
                        ) else 0
                    )
                )
                snowflake[direction_axis] = random.randrange(*limit)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                return False
        return True

    def run_game(self):
        running = True
        while running:
            running = self.handle_events()
            self.window.fill(GAME_BACKGROUND_COLOR)
            for snowflake in self.snowfall:
                if SNOWFLAKE_ROTATIONS:
                    rotated_snowflake = pygame.transform.rotate(
                        self.transformed_snowflake,
                        self.angle
                    )
                    self.angle += self.rotation_speed
                    rotated_rect = rotated_snowflake.get_rect(center=snowflake)
                    self.window.blit(rotated_snowflake, rotated_rect)
                else:
                    self.window.blit(self.transformed_snowflake, snowflake)
            pygame.display.flip()
            self.update_snowflakes()
            self.clock.tick(GAME_TICKS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run_game()
