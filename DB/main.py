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


users_table_name = 'users'


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

    value = cursor.lastrowid

    print(f'{table_name}: +{cursor.rowcount}(last_row_id = {value})')

    return value


def get_main_menu_buttons():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `main_menu_buttons` WHERE status = TRUE')

    return cursor.fetchall()


def insert_order_items(items_data, table_name):
    basket = items_data.pop('basket')
    data_keys = list(items_data.keys())
    data_keys += ['book_id', 'quantity']
    data_values = tuple(items_data.values())

    data_values = [data_values + tuple([book_id, quantity]) for (book_id, quantity) in basket.items()]

    fields = ','.join(data_keys)
    mask = ','.join(['%s'] * len(data_keys))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.executemany(sql, data_values)
            connection.commit()

    value = cursor.rowcount

    print(f'{table_name}: +{value}')

    return value


def get_user(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {users_table_name} WHERE tg_id = %s OR id = %s', (id, id))

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


def get_driver(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `drivers` WHERE user_id = %s", user_id)

    return cursor.fetchone()


def get_order_items(order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM order_items WHERE order_items.order_id = %s', order_id)

    return cursor.fetchall()


def get_user_orders(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM orders WHERE orders.user_id = %s ORDER BY id DESC', user_id)

    return cursor.fetchall()


def get_car_models():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `cars`")

    return cursor.fetchall()


def get_orders_by_status(status):
    if isinstance(status, tuple):
        sql = f'SELECT * FROM orders WHERE orders.status = %s OR orders.status = %s ORDER BY id DESC'
    else:
        sql = f'SELECT * FROM orders WHERE orders.status = %s ORDER BY id DESC'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, status)

    return cursor.fetchall()


def update_order_status(status, order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
            connection.commit()

    return_value = 'not updated'

    if connection.affected_rows() != 0:
        return_value = 'updated'

    return return_value


def update_user_info(id, **kwargs):
    if 'lang' in kwargs.keys():
        value = kwargs['lang']
        sql = f'UPDATE {users_table_name} SET lang = %s WHERE tg_id = %s OR id = %s'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (value, id, id))
            connection.commit()

    return_value = 'not updated'

    if connection.affected_rows() != 0:
        return_value = 'updated'

    return return_value
