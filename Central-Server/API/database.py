import psycopg2
import collections

import os
def get_db_secret():
    with open(os.getenv("DB_PASSWORD_FILE")) as f:
        return(str(f.read()))

db_secret = get_db_secret().strip()

def get_db_name():
    val = os.getenv("DB_NAME")
    if val == None:
        return "db"
    return val

db_host = get_db_name()

def connect():
    conn = psycopg2.connect(database="postgres",
                    host=db_host,
                    user="postgres",
                    password=db_secret,
                    port=5432)
    return conn

def set_db_struct(cursor: psycopg2.cursor, data: tuple):
    """
    @param data Tuple of data from the psycopg2 function cursor.fetchall()[0] or its equivalent
    @returns struct of the record in a namedtuple
    """
    cols = [desc[0] for desc in cursor.description]
    Record = collections.namedtuple("JobRecord", cols)
    return Record(**dict(zip(cols, data)))

def get_data_struct(cursor: psycopg2.cursor, data: list) -> list:
    """
    @param data List of data from the psycopg2 function cursor.fetchall()
    @returns struct of the record in a namedtuple
    """
    cols = [desc[0] for desc in cursor.description]
    Record = collections.namedtuple("JobRecord", cols)
    record_list = []
    for row in data:
        record_list.append(Record(**dict(zip(cols, row))))
    return record_list
