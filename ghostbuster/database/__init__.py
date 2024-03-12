import os
import sqlite3
import logging
from typing import Optional
import datetime

database_file = 'ghost.sqlite3'
database_structure_file = 'structure.sql'


def get_conn():
    global conn
    global database_file

    fullpath_database_file = os.path.join(os.getcwd(), database_file)
    # database structure file should be in the same directory as this file
    fullpath_database_structure_file = os.path.join(os.path.dirname(__file__), database_structure_file)


    # if file does not exist, it will be created
    if not os.path.exists(database_file):
        # create file and make it writable by the user and group
        open(database_file, 'w').close()
        os.chmod(database_file, 0o660)
        logging.info('Database file does not exist. Creating new database file {}'.format(fullpath_database_file))
        conn = sqlite3.connect(database_file)

        with open(fullpath_database_structure_file, 'r') as f:
            conn.executescript(f.read())
    else:
        # if file is not writable by the user and group exit with error
        if os.stat(database_file).st_mode & 0o600 != 0o600:
            logging.error(f'Database file {database_file} is not writable by the user and group. Exiting.')
            exit(1)
        conn = sqlite3.connect(database_file)
        conn.commit()

    conn.row_factory = sqlite3.Row

    return conn

def datetime_format(datetime: datetime.datetime) -> Optional[str]:
    if datetime:
        return datetime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None

def datetime_format_now() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
