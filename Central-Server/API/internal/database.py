"""This file exposes functions that abstract certain database functions"""
import os
import collections

import psycopg2

import util.test_env as testing

DATABASE_PORT = 5432  # Default postgres port


def get_db_secret() -> str:
    """Returns the database secret (password)"""
    with open(os.getenv("DB_PASSWORD_FILE")) as f:
        return (str(f.read()))


db_secret = get_db_secret().strip()


def get_db_name() -> str:
    """Returns the name of the database used to store Kamaji data"""
    val = os.getenv("DB_NAME")
    if val is None:
        return "db"
    return val


db_host = get_db_name()  # Exposed variable for getting database


def connect():
    """Returns a database connection after connecting with the DB credentials"""
    global DATABASE_PORT
    conn = psycopg2.connect(database="postgres",
                            host=db_host,
                            user="postgres",
                            password=db_secret,
                            port=DATABASE_PORT)
    return conn


def convert_database_tuple(cursor: psycopg2.extensions.cursor, data: tuple):
    """
    Normally, database output is in a struct, but we can fix that
    @param data Tuple of data from the psycopg2 function cursor.fetchall()[0] or its equivalent
    @returns struct of the record in a namedtuple
    """
    cols = [desc[0] for desc in cursor.description]
    Record = collections.namedtuple("JobRecord", cols)
    return Record(**dict(zip(cols, data)))


def convert_database_list(
        cursor: psycopg2.extensions.cursor,
        data: list) -> list:
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


def generate_jobs_table():
    """Generates database if it doesn't exist"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_tables WHERE tablename='hilsim_runs'")
    exists = cursor.fetchone()
    if not exists:
        with open("database.sql") as f:
            cursor.execute(f.read())
        conn.commit()
        conn.close()
        cursor.close()
    else:
        # If we are in the testing environment, we need to clear the database, even if it exists.
        print("(generate_jobs_table) Detecting testing environment", flush=True)
        if(testing.is_test_environment()):
            print("(generate_jobs_table) Detected testing environment. Resetting database.", flush=True)
            try:
                cursor.execute("DELETE FROM hilsim_runs")
                print("(generate_jobs_table) Database reset successfully", flush=True)
            except Exception as e:
                print("(generate_jobs_table) Database error:", e)
                print("(generate_jobs_table) Failed to reset database. Continuing..", flush=True)
        else:
            print("(generate_jobs_table) Non-testing environment detected", flush=True)