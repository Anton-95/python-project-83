import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


class URLError(Exception):
    pass


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def save_url(url):
    conn = get_connection()

    with conn.cursor() as cursor:
        query = "SELECT id, name FROM urls WHERE name = %s"
        cursor.execute(query, (url,))
        result = cursor.fetchone()

        if result is None:
            add_url = """INSERT INTO
                            urls (name, created_at)
                         VALUES
                            (%s, %s)"""
            cursor.execute(add_url, (url, datetime.now()))

        else:
            raise URLError()

    conn.commit()
    conn.close()


def get_url(url_id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        query = "SELECT id, name, created_at FROM urls WHERE id = %s"
        cursor.execute(query, (url_id,))
        url = cursor.fetchone()

    conn.commit()
    conn.close()
    return url


def get_id_url(url):
    conn = get_connection()

    with conn.cursor() as cursor:
        query = "SELECT id FROM urls WHERE name = %s"
        cursor.execute(query, (url,))
        result = cursor.fetchone()
        url_id = result[0]

    conn.commit()
    conn.close()
    return url_id


def get_all_urls():
    conn = get_connection()

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """SELECT
                       urls.id,
                       urls.name,
                       urls.created_at,
                       MAX(url_checks.created_at) as last_check,
                       url_checks.status_code
                   FROM urls
                   LEFT JOIN url_checks ON urls.id = url_checks.url_id
                   GROUP BY urls.id, url_checks.status_code
                   ORDER BY created_at DESC"""
        cursor.execute(query)
        urls = cursor.fetchall()

    conn.commit()
    conn.close()
    return urls


def save_url_check(url_id, status_code, tags):
    conn = get_connection()

    with conn.cursor() as cursor:
        query = """INSERT INTO url_checks (
                       url_id, status_code, h1, title, description, created_at
                       )
                   VALUES
                       (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(
            query,
            (
                url_id,
                status_code,
                tags["h1"],
                tags["title"],
                tags["description"],
                datetime.now(),
            ),
        )

    conn.commit()
    conn.close()


def get_all_url_checks(url_id):
    conn = get_connection()

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """SELECT
                       id,
                       status_code,
                       h1,
                       title,
                       description,
                       created_at
                   FROM url_checks
                   WHERE url_id = %s ORDER BY created_at DESC"""
        cursor.execute(query, (url_id,))
        check_url = cursor.fetchall()

    conn.commit()
    conn.close()
    return check_url
