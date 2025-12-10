import sqlite3
from record_log import log_info, log_error


DB_FILE = 'db.db'


def initialize_database(): # initialization db
    try:
        log_info('initialize_database')

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS Users (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT,
                    balance_water INTEGER
                )
                '''
            )


    except Exception as e:
        log_error(f'initialize_database with error: {e}')


def add_user(user_id): # add new user
    try:
        log_info('add_user')

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT telegram_id FROM Users WHERE telegram_id = ?', (user_id,))
            user = cursor.fetchone()
            if user is None:
                cursor.execute(
                    '''
                    INSERT INTO Users (telegram_id, balance_water)
                    VALUES (?, ?)
                    ''', (user_id, 0)
                )

            conn.commit()


    except Exception as e:
        log_error(f'add_user with error: {e}')



def add_balance_water(user_id, ml): # add water balance
    try:
        log_info('add_balance_water')

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # Проверяем есть ли пользователь
            cursor.execute('SELECT telegram_id, balance_water FROM Users WHERE telegram_id = ?', (user_id,))
            row = cursor.fetchone()

            if row is None:
                # Вставляем нового пользователя с начальным балансом 0
                cursor.execute('INSERT INTO Users (telegram_id, balance_water) VALUES (?, ?)', (user_id, ml))

            else:
                #
                new_balance = int(row[1]) + int(ml)
                cursor.execute('UPDATE Users SET balance_water = ? WHERE telegram_id = ?', (new_balance, user_id))

                conn.commit()
                return True



    except Exception as e:
        log_error(f'add_balance_water with error: {e}')




def get_balance_water(user_id): # get balance water
    try:
        log_info('get_balance_water')

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT telegram_id, balance_water FROM Users WHERE telegram_id = ?', (user_id,))
            row = cursor.fetchone()

            return row[1]


    except Exception as e:
        log_error(f'get_balance_water with error: {e}')




def reset_balance_water(): # reset all balance water
    try:
        log_info('reset_balance_water')

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE Users SET water = 0')
            conn.commit()
            return True


    except Exception as e:
        log_error(f'reset_balance_water with error: {e}')