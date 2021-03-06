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


def insert_order_items(data_values, fields_list, table_name):
    fields = ','.join(fields_list)
    mask = ','.join(['%s'] * len(fields_list))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.executemany(sql, data_values)
            connection.commit()

    print(f'{table_name}: +{cursor.rowcount}')

    return cursor.rowcount


def get_main_menu_buttons():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `main_menu_buttons` WHERE status = TRUE')

    return cursor.fetchall()


def get_user(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `users` WHERE tg_id = %s OR id = %s', (id, id))

    return cursor.fetchone()


def get_all_users():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `users`')

    return cursor.fetchall()


def get_all_regions():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `regions` WHERE parent_id = 0')

    return cursor.fetchall()


def get_all_active_drivers():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `active_drivers`')

    return cursor.fetchall()


def get_districts_by_parent(parent_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `regions` WHERE parent_id = %s', parent_id)

    return cursor.fetchall()


def get_region_and_district(region_id, district_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `regions` WHERE id = %s or id = %s', (region_id, district_id))

    return cursor.fetchall()


def get_region_districts(region_id, district_ids_list):
    new_list = list(district_ids_list)
    new_list.append(region_id)

    mark = ','.join(['%s' for i in range(len(new_list))])
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `regions` WHERE id IN ({mark})', new_list)

    return cursor.fetchall()


def get_region_discricts_num(region_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT count(id) as num FROM `regions` WHERE parent_id = %s', region_id)

    return cursor.fetchone()


def get_active_driver_by_user_id(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `active_drivers` WHERE user_id = %s", user_id)

    return cursor.fetchone()


def get_active_drivers_by_seats(empty_seats):
    mark = ','.join(['%s' for i in range(len(empty_seats))])
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `active_drivers` WHERE empty_seats IN ({mark}) ORDER BY empty_seats DESC',
                           empty_seats)

    return cursor.fetchall()


def get_active_driver_by_driver_id(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `active_drivers` WHERE driver_id = %s', driver_id)

    return cursor.fetchone()


def get_driver_by_user_id(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `drivers` WHERE user_id = %s', user_id)

    return cursor.fetchone()


def get_driver_by_id(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `drivers` WHERE id = %s', driver_id)

    return cursor.fetchone()


def get_video_files():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `video_files`')

    return cursor.fetchall()


def get_driver_and_car_data(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = 'SELECT drivers.id, drivers.user_id,  cars.car_model, drivers.baggage, drivers.status FROM cars ' \
                  'INNER JOIN drivers ON drivers.car_id = cars.id WHERE drivers.user_id = %s'
            cursor.execute(sql, user_id)

    return cursor.fetchone()


def get_car_models():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `cars`')

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


def update_driver_car_model(car_id, user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `drivers` SET car_id = %s WHERE user_id = %s', (car_id, user_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_baggage(baggage, user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `drivers` SET baggage = %s WHERE user_id = %s', (baggage, user_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def delete_active_driver(driver_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM `active_drivers` WHERE driver_id = %s', driver_id)
            connection.commit()

    return 'deleted' if connection.affected_rows() != 0 else 'not deleted'


def update_user_fullname(fullname, user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `users` SET fullname = %s WHERE id = %s', (fullname, user_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_user_lang(lang, id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE `users` SET lang = %s WHERE id = %s OR tg_id = %s', (lang, id, id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_user_phone_numbers(field, phone_number, user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE `users` SET {field} = %s WHERE id = %s', (phone_number, user_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_post_status(status, post_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE posts SET status = %s WHERE id = %s', (status, post_id))
            connection.commit()

    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def check_phone_number_existence(phone_number):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM `users` WHERE phone_number = %s OR phone_number_2 = %s',
                           (phone_number, phone_number))
            connection.commit()

    return cursor.fetchone()
