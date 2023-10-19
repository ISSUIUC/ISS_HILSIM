import psycopg2

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
    print(db_secret, flush=True)
    conn = psycopg2.connect(database="postgres",
                    host=db_host,
                    user="postgres",
                    password=db_secret,
                    port=5432)
    return conn
