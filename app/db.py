import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor


def connection():
    load_dotenv('config.env', encoding='utf-8')
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'))
    return conn

def get_cursor():
    conn = connection()
    return conn.cursor(cursor_factory=DictCursor), conn

