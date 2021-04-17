import pymysql.cursors
from contextlib import closing
from config import DB_CONFIG


def get_connection():
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


def insert_data(data, table_name):
    data_keys = tuple(data.keys())
    data_values = tuple(data.values())

    fields = ','.join(data_keys)
    mask = ','.join(['%s'] * len(data_values))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.execute(sql, data_values)
            connection.commit()

    print(f'{table_name}: +{cursor.rowcount}(last_row_id = {cursor.lastrowid})')

    return cursor.lastrowid


def get_main_menu_buttons():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `main_menu_buttons` WHERE status = TRUE')

    return cursor.fetchall()


def get_user(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `users` WHERE tg_id = %s OR id = %s', (id, id))

    return cursor.fetchone()


def get_all_regions():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `regions` WHERE parent_id = 0")

    return cursor.fetchall()


def get_districts_by_parent(parent_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `regions` WHERE parent_id = %s", parent_id)

    return cursor.fetchall()


def get_region_and_district(region_id, district_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `regions` WHERE id = %s or id = %s", (region_id, district_id))

    return cursor.fetchall()


def get_region_districts(region_id, district_ids_list):
    new_list = list(district_ids_list)
    new_list.append(region_id)

    mark = ','.join(['%s' for i in range(len(new_list))])
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `regions` WHERE id IN ({mark})", new_list)

    return cursor.fetchall()


def get_active_driver_by_user_id(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `active_drivers` WHERE user_id = %s", user_id)

    return cursor.fetchone()


def get_active_drivers_by_seats(empty_seats):
    mark = ','.join(['%s' for i in range(len(empty_seats))])
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `active_drivers` WHERE empty_seats IN ({mark}) ORDER BY empty_seats DESC",
                           empty_seats)

    return cursor.fetchall()


def get_active_driver_by_driver_id(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `active_drivers` WHERE driver_id = %s", driver_id)

    return cursor.fetchone()


def get_driver_by_user_id(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `drivers` WHERE user_id = %s", user_id)

    return cursor.fetchone()


def get_driver_by_id(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `drivers` WHERE id = %s", driver_id)

    return cursor.fetchone()


def get_video_files():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `video_files`")

    return cursor.fetchall()


def get_driver_and_car_data(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT drivers.id, drivers.user_id,  cars.car_model, drivers.baggage, drivers.status FROM cars " \
                  "INNER JOIN drivers ON drivers.car_id = cars.id WHERE drivers.user_id = %s"
            cursor.execute(sql, user_id)

    return cursor.fetchone()


def get_car_models():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `cars`")

    return cursor.fetchall()


def update_active_driver_comment(new_comment, driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `active_drivers` SET comment = %s WHERE driver_id = %s', (new_comment, driver_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_active_driver_empty_seats(new_empty_seats, driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `active_drivers` SET empty_seats = %s WHERE driver_id = %s',
                           (new_empty_seats, driver_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_active_driver_ask_parcel(new_answer, driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `active_drivers` SET ask_parcel = %s WHERE driver_id = %s', (new_answer, driver_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_active_driver_departure_time(new_daparture_time, driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `active_drivers` SET departure_time = %s WHERE driver_id = %s',
                           (new_daparture_time, driver_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_active_driver_from_or_to(field, new_json, driver_id):
    field = 'from_' if field == 'from' else 'to_'
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE `active_drivers` SET {field} = %s WHERE driver_id = %s', (new_json, driver_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def delete_active_driver(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM `active_drivers` WHERE driver_id = %s', driver_id)
            connection.commit()

    return 'deleted' if connection.affected_rows() != 0 else 'not deleted'


def update_user_info(id, **kwargs):
    if 'lang' in kwargs.keys():
        value = kwargs['lang']
        sql = f'UPDATE `users` SET lang = %s WHERE tg_id = %s OR id = %s'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (value, id, id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'
