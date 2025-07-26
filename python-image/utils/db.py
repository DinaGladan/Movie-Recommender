# za povzivanje s postgreSQL
import psycopg2
import os

# kao i selenium, instalirala sam ga i spremila u requirements.txt
# ali ga ne prepoznaje
from dotenv import load_dotenv

load_dotenv(dotenv_path="/app/.env")  # ucitavamo podatke iz .env-a


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )
        return conn
    except psycopg2.Error as error:
        print(f"Error connecting to PostgreSQL {error}")


def close_db_connection(conn):
    return conn.close()
