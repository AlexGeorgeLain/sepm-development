import time

import pygame

from database import models
from game.cars import ComputerCar, PlayerCar
from game.profiles import PlayerProfile
from game.track import Track
from game.utilities import blit_text_center, censor_word

pygame.font.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/theme.wav")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pygame-test")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SMALL_FONT = pygame.font.SysFont("comicsans", 24)


FPS = 60


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time, 2)


class Button:
    def __init__(
        self, text, text_colour, x, y, width, height, button_colour, size=True
    ):
        self.text = text.upper()
        self.text_colour = text_colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_colour = button_colour

        if size:
            self.render_text = MAIN_FONT.render(self.text, bool(1), self.text_colour)
        else:
            self.render_text = SMALL_FONT.render(self.text, bool(1), self.text_colour)

        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.draw_button()

    def button_text(self):
        WIN.blit(
            self.render_text,
            (
                self.x + self.width / 2 - self.render_text.get_width() / 2,
                self.y + self.height / 2 - self.render_text.get_height() / 2,
            ),
        )

    def draw_button(self):
        pygame.draw.rect(WIN, self.button_colour, self.button_rect)
        self.button_text()


class TextBox:
    def __init__(self, text=""):
        self.text = text.lower()
        self.text_colour = (255, 255, 255)
        self.x = 300
        self.y = 300
        self.width = 200
        self.height = 50
        self.background_colour = (0, 0, 0)

        self.render_text = MAIN_FONT.render(self.text, bool(1), self.text_colour)

        self.textbox_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def input_text(self):
        WIN.blit(
            self.render_text,
            (
                self.x + self.width / 2 - self.render_text.get_width() / 2,
                self.y + self.height / 2 - self.render_text.get_height() / 2,
            ),
        )

    def draw_textbox(self):
        pygame.draw.rect(WIN, self.background_colour, self.textbox_rect)
        self.input_text()

    def update_text(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

        elif len(self.text) < 8:
            self.text += event.unicode
            self.text = self.text.lower()

        self.render_text = MAIN_FONT.render(self.text, bool(1), self.text_colour)


def quit_game():
    pygame.quit()
    exit()


def menu_button_text(button_text, x, y):
    text = MAIN_FONT.render(button_text.upper(), bool(1), (255, 255, 255))
    WIN.blit(text, (x, y))


def menu_title(menu_name):
    text = MAIN_FONT.render(menu_name.upper(), bool(1), (255, 255, 255))
    WIN.blit(text, (WIN.get_width() / 2 - text.get_width() / 2, 10))


def menu_basic(
    clock,
    track,
    player_car,
    computer_car,
    game_info,
    player_profile,
    menu_name,
    previous_menu,
    click,
):
    WIN.blit(track.background_image, (0, 0))
    WIN.blit(track.track_image, (0, 0))
    WIN.blit(track.finish_image, track.finish_position)
    WIN.blit(track.border_image, (0, 0))

    computer_car.draw(WIN)
    player_car.draw(WIN)

    if menu_name != "game":
        menu_title(menu_name)

    mute = "mute"
    if player_profile.mute:
        mute = "unmute"

    width, height = 150, 20

    mute_button = Button(
        mute,
        (255, 255, 255),
        WIN.get_width() - width - 10,
        10,
        width,
        height,
        (255, 0, 0),
        False,
    )
    if mute_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
        player_profile.update_mute()

    if menu_name != "main menu":
        main_menu_button = Button(
            "main menu", (255, 255, 255), 10, 10, width, height, (255, 0, 0), False
        )
        if main_menu_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            game_info.reset()
            player_car.reset()
            computer_car = ComputerCar(
                "black_car",
                track.computer_start_position,
                track.computer_path,
                track.track_record,
            )
            main_menu(clock, track, player_car, computer_car, game_info, player_profile)

        if menu_name != "game" and previous_menu in ["settings", "profiles"]:
            back_button = Button(
                "Back", (255, 255, 255), 10, 40, width, height, (255, 0, 0), False
            )
            if back_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
                if previous_menu == "settings":
                    settings_loop(
                        clock,
                        track,
                        player_car,
                        computer_car,
                        game_info,
                        player_profile,
                    )
                if previous_menu == "profiles":
                    profiles_settings(
                        clock,
                        track,
                        player_car,
                        computer_car,
                        game_info,
                        player_profile,
                    )

    if menu_name == "game":
        time_text = MAIN_FONT.render(
            f"Time: {game_info.get_level_time()}s", bool(1), (255, 255, 255)
        )
        WIN.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

        time_text = MAIN_FONT.render(
            f"Record: {track.track_record}s", bool(1), (255, 255, 255)
        )
        WIN.blit(time_text, (10, HEIGHT - time_text.get_height()))


def menu_bottom_nav_buttons(start_index, all_list, click):
    width, height = 150, 30
    if start_index + 5 < len(all_list):
        next_button = Button(
            "next",
            (255, 255, 255),
            WIN.get_width() - width - 10,
            WIN.get_height() - height - 10,
            150,
            30,
            (255, 0, 0),
            False,
        )
        if next_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            start_index += 5

    if start_index > 0:
        previous_button = Button(
            "previous",
            (255, 255, 255),
            10,
            WIN.get_height() - height - 10,
            150,
            30,
            (255, 0, 0),
            False,
        )
        if previous_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            start_index -= 5

    return start_index


def high_score_name_entry(
    clock, track, player_car, computer_car, game_info, time, player_profile
):
    if player_profile.username == "default":
        name_entry_box = TextBox()
    else:
        name_entry_box = TextBox(player_profile.username)

    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

            if event.type == pygame.KEYDOWN:
                name_entry_box.update_text(event)

                if event.key == pygame.K_RETURN:
                    if name_entry_box.text != "":
                        models.HighScore.create(
                            name=name_entry_box.text, time=time, track_id=track.track_id
                        )
                        game_loop(
                            clock,
                            track,
                            player_car,
                            computer_car,
                            game_info,
                            player_profile,
                        )
                    else:
                        game_loop(
                            clock,
                            track,
                            player_car,
                            computer_car,
                            game_info,
                            player_profile,
                        )

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "enter name",
            "main menu",
            click,
        )

        menu_button_text(f"Time: {time}", 300, 200)

        name_entry_box.draw_textbox()

        done_button = Button("done", (255, 255, 255), 300, 500, 200, 50, (255, 0, 0))
        if done_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            if name_entry_box.text != "":
                models.HighScore.create(
                    name=name_entry_box.text, time=time, track_id=track.track_id
                )
                game_loop(
                    clock, track, player_car, computer_car, game_info, player_profile
                )
            else:
                game_loop(
                    clock, track, player_car, computer_car, game_info, player_profile
                )

        pygame.display.update()


def handle_collision(clock, track, player_car, computer_car, game_info, player_profile):
    if player_car.collide(track.border_mask) is not None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(
        track.finish_mask, track.finish_x, track.finish_y
    )
    if computer_finish_poi_collide is not None:
        blit_text_center(WIN, MAIN_FONT, "You lost!")
        pygame.display.update()
        pygame.time.wait(2000)
        game_info.reset()
        player_car.reset()
        computer_car = ComputerCar(
            "black_car",
            track.computer_start_position,
            track.computer_path,
            track.track_record,
        )
        game_loop(clock, track, player_car, computer_car, game_info, player_profile)

    player_finish_poi_collide = player_car.collide(
        track.finish_mask, track.finish_x, track.finish_y
    )
    if player_finish_poi_collide is not None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            blit_text_center(WIN, MAIN_FONT, "You Win!")
            time = game_info.get_level_time()
            pygame.display.update()
            pygame.time.wait(2000)
            game_info.reset()
            player_car.reset()
            computer_car = ComputerCar(
                "black_car",
                track.computer_start_position,
                track.computer_path,
                track.track_record,
            )
            high_score_name_entry(
                clock, track, player_car, computer_car, game_info, time, player_profile
            )


def game_loop(clock, track, player_car, computer_car, game_info, player_profile):
    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "game",
            "main menu",
            click,
        )

        ################################################
        # for finding new track path
        if click:
            new_path_point = pygame.mouse.get_pos()
            path_x, path_y = new_path_point
            print(
                f"- model: path\n  track_id: {track.track_id}\n  path_x: {path_x}\n  path_y: {path_y}\n"
            )
        computer_car.draw_points(WIN)
        ###############################################

        while not game_info.started:
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

            width, height = 150, 20

            mute = "mute"
            if player_profile.mute:
                mute = "unmute"

            mute_button = Button(
                mute,
                (255, 255, 255),
                WIN.get_width() - width - 10,
                10,
                width,
                height,
                (255, 0, 0),
                False,
            )
            if mute_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
                player_profile.update_mute()

            main_menu_button = Button(
                "main menu", (255, 255, 255), 10, 10, width, height, (255, 0, 0), False
            )
            if (
                main_menu_button.button_rect.collidepoint(pygame.mouse.get_pos())
                and click
            ):
                game_info.reset()
                player_car.reset()
                computer_car = ComputerCar(
                    "black_car",
                    track.computer_start_position,
                    track.computer_path,
                    track.track_record,
                )
                main_menu(
                    clock, track, player_car, computer_car, game_info, player_profile
                )

            blit_text_center(WIN, MAIN_FONT, "Press any key to start!")

            pygame.display.update()

        player_car.move_player()
        computer_car.move()

        handle_collision(
            clock, track, player_car, computer_car, game_info, player_profile
        )

        pygame.display.update()


def settings_loop(clock, track, player_car, computer_car, game_info, player_profile):
    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "settings",
            "main menu",
            click,
        )

        car_button = Button("car", (255, 255, 255), 300, 200, 200, 50, (255, 0, 0))
        if car_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            car_settings(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        track_button = Button("track", (255, 255, 255), 300, 300, 200, 50, (255, 0, 0))
        if track_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            track_settings(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        pygame.display.update()


def car_settings(clock, track, player_car, computer_car, game_info, player_profile):
    all_cars = (
        models.Car.select(
            models.Car.car_id,
            models.Car.car_name,
            models.Car.max_vel,
            models.Car.rotation_vel,
            models.Car.acceleration,
        )
        .where(models.Car.car_id != "black_car")
        .order_by(models.Car.car_name)
        .limit(5)
    )

    start_index = 0

    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "cars",
            "settings",
            click,
        )

        car_buttons = []
        car_ids = []
        y = 200
        for item in all_cars:
            car_ids.append(item.car_id)
            button = Button(item.car_name, (255, 255, 255), 10, y, 200, 50, (255, 0, 0))
            car_buttons.append(button)
            stats_y = button.y + button.height / 2 - button.render_text.get_height() / 2
            menu_button_text(
                f"Speed:{item.max_vel}    Hand:{item.rotation_vel}    Acc:{item.acceleration}",
                200,
                stats_y,
            )
            y += 100

        for button in car_buttons:
            if button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
                _id = car_ids[car_buttons.index(button)]
                player_car = PlayerCar(_id, track.player_start_position)
                player_profile.update_last_car_id(player_car.car_id)

        start_index = menu_bottom_nav_buttons(start_index, all_cars, click)

        pygame.display.update()


def track_settings(clock, track, player_car, computer_car, game_info, player_profile):
    all_tracks = (
        models.Track.select(models.Track.track_id, models.Track.track_name)
        .order_by(models.Track.track_name)
        .limit(5)
    )
    start_index = 0

    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "tracks",
            "settings",
            click,
        )

        track_buttons = []
        track_ids = []
        y = 200
        for item in all_tracks:
            track_ids.append(item.track_id)
            button = Button(
                item.track_name, (255, 255, 255), 300, y, 200, 50, (255, 0, 0)
            )
            track_buttons.append(button)
            y += 100

        for button in track_buttons:
            if button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
                _id = track_ids[track_buttons.index(button)]
                track = Track(_id)
                player_car = PlayerCar(
                    player_profile.last_car_id, track.player_start_position
                )
                computer_car = ComputerCar(
                    "black_car",
                    track.computer_start_position,
                    track.computer_path,
                    track.track_record,
                )
                player_profile.update_last_track_id(track.track_id)

        start_index = menu_bottom_nav_buttons(start_index, all_tracks, click)

        pygame.display.update()


def high_scores(clock, track, player_car, computer_car, game_info, player_profile):
    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "high scores",
            "main menu",
            click,
        )

        top_scores = (
            models.HighScore.select(models.HighScore.name, models.HighScore.time)
            .where(models.HighScore.track_id == track.track_id)
            .order_by(models.HighScore.time)
            .limit(5)
        )

        x, y, score_pos = 150, 200, 1
        for item in top_scores:
            menu_button_text(f"{score_pos}.", x - 50, y)
            if (
                models.Profanity.select()
                .where(models.Profanity.word == item.name.lower())
                .exists()
            ):
                menu_button_text(censor_word(item.name), x, y)
            else:
                menu_button_text(item.name, x, y)
            menu_button_text(str(round(item.time, 3)), x + 300, y)
            y += 100
            score_pos += 1

        pygame.display.update()


def profiles_settings(
    clock, track, player_car, computer_car, game_info, player_profile
):
    all_profiles = (
        models.Profile.select(models.Profile.username)
        .order_by(models.Profile.username)
        .limit(5)
    )

    start_index = 0

    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "create profile",
            "main menu",
            click,
        )

        create_profile_button = Button(
            "create profile", (255, 255, 255), 300, 100, 200, 50, (255, 0, 0)
        )
        if (
            create_profile_button.button_rect.collidepoint(pygame.mouse.get_pos())
            and click
        ):
            create_profile(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        profile_buttons = []
        y = 200
        for profile in all_profiles:
            profile_buttons.append(
                Button(profile.username, (255, 255, 255), 300, y, 200, 50, (255, 0, 0))
            )
            y += 100

        for button in profile_buttons:
            if button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
                player_profile = PlayerProfile(button.text.lower())
                track = Track(player_profile.last_track_id)
                player_car = PlayerCar(
                    player_profile.last_car_id, track.player_start_position
                )
                computer_car = ComputerCar(
                    "black_car",
                    track.computer_start_position,
                    track.computer_path,
                    track.track_record,
                )

        start_index = menu_bottom_nav_buttons(start_index, all_profiles, click)

        pygame.display.update()


def create_profile(clock, track, player_car, computer_car, game_info, player_profile):
    name_entry_box = TextBox()
    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

            if event.type == pygame.KEYDOWN:

                name_entry_box.update_text(event)

                if (
                    event.key == pygame.K_RETURN
                    and len(name_entry_box.text) != 0
                    and not models.Profile.select()
                    .where(models.Profile.username == name_entry_box.text)
                    .exists()
                ):
                    models.Profile.create(
                        username=name_entry_box.text,
                        mute=player_profile.mute,
                        last_car_id=player_car.car_id,
                        last_track_id=track.track_id,
                    )
                    player_profile = PlayerProfile(name_entry_box.text)
                    profiles_settings(
                        clock,
                        track,
                        player_car,
                        computer_car,
                        game_info,
                        player_profile,
                    )

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "create profile",
            "profiles",
            click,
        )

        menu_button_text("enter new username", 300, 200)

        name_entry_box.draw_textbox()

        done_button = Button("done", (255, 255, 255), 300, 500, 200, 50, (255, 0, 0))
        if done_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            if (
                name_entry_box.text != ""
                # and name_entry_box.text
                # not in cur.execute(
                #     """SELECT username FROM player_profiles"""
                # ).fetchall()
                and not models.Profile.select()
                .where(models.Profile.username == name_entry_box.text)
                .exists()
            ):
                models.Profile.create(
                    username=name_entry_box.text,
                    mute=player_profile.mute,
                    last_car_id=player_car.car_id,
                    last_track_id=track.track_id,
                )
                player_profile = PlayerProfile(name_entry_box.text)
                profiles_settings(
                    clock, track, player_car, computer_car, game_info, player_profile
                )

        pygame.display.update()


def main_menu(clock, track, player_car, computer_car, game_info, player_profile):
    while True:
        clock.tick(FPS)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        menu_basic(
            clock,
            track,
            player_car,
            computer_car,
            game_info,
            player_profile,
            "main menu",
            "main menu",
            click,
        )

        play_button = Button("Play", (255, 255, 255), 300, 200, 200, 50, (255, 0, 0))
        if play_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            game_loop(clock, track, player_car, computer_car, game_info, player_profile)

        settings_button = Button(
            "Settings", (255, 255, 255), 300, 300, 200, 50, (255, 0, 0)
        )
        if settings_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            settings_loop(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        high_scores_button = Button(
            "High Scores", (255, 255, 255), 300, 400, 200, 50, (255, 0, 0)
        )
        if (
            high_scores_button.button_rect.collidepoint(pygame.mouse.get_pos())
            and click
        ):
            high_scores(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        profiles_button = Button(
            "profiles", (255, 255, 255), 300, 500, 200, 50, (255, 0, 0)
        )
        if profiles_button.button_rect.collidepoint(pygame.mouse.get_pos()) and click:
            profiles_settings(
                clock, track, player_car, computer_car, game_info, player_profile
            )

        pygame.display.update()


def main_game_loop():
    clock = pygame.time.Clock()

    player_profile = PlayerProfile("default")

    track = Track(player_profile.last_track_id)

    player_car = PlayerCar(player_profile.last_car_id, track.player_start_position)

    computer_car = ComputerCar(
        "black_car",
        track.computer_start_position,
        track.computer_path,
        track.track_record,
    )

    game_info = GameInfo()

    main_menu(clock, track, player_car, computer_car, game_info, player_profile)
