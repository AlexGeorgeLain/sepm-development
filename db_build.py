import config

con = config.con
cur = con.cursor()


def create_tracks():
    cur.execute("""CREATE TABLE tracks
                    (
                    track_id text PRIMARY KEY,
                    track_name text,
                    track_path text,
                    border_path text,
                    background_path text,
                    player_x int,
                    player_y int,
                    computer_x int,
                    computer_y int,
                    finish_x int,
                    finish_y int
                    )
                """)

    track_list = [('track_1', 'Track 1', 'imgs/track.png', 'imgs/track-border.png', 'imgs/grass.jpg',
                   180, 200,
                   150, 200,
                   130, 250), ]

    cur.executemany("""INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", track_list)
    con.commit()


def create_cars():
    cur.execute("""CREATE TABLE cars
                    (
                    car_id text PRIMARY KEY,
                    car_name text,
                    car_path text,
                    max_vel int,
                    rotation_vel int,
                    acceleration int
                    )
                """)

    car_list = [('red_car', 'Red Car', 'imgs/red-car.png', 4, 4, 1),
                ('green_car', 'Green Car', 'imgs/green-car.png', 4, 4, 1),
                ('grey_car', 'Grey Car', 'imgs/grey-car.png', 4, 4, 1),
                ('purple_car', 'Purple Car', 'imgs/purple-car.png', 4, 4, 1),
                ('white_car', 'White Car', 'imgs/white-car.png', 4, 4, 1), ]

    cur.executemany("""INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?)""", car_list)
    con.commit()


def build_db():
    create_tracks()
    create_cars()