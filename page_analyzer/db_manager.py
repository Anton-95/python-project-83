from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


class URLError(Exception):
    pass


class DatabaseConnection:
    def __init__(self, dsn, cursor_factory=None):
        self.dsn = dsn
        self.cursor_factory = cursor_factory
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        if self.cursor_factory:
            return self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        if self.conn:
            self.conn.close()


class UrlsRepository:
    def __init__(self, dsn):
        self.dsn = dsn

    def save_url(self, url):
        with DatabaseConnection(self.dsn) as cursor:
            query = "SELECT id, name FROM urls WHERE name = %s"
            cursor.execute(query, (url,))
            result = cursor.fetchone()
            if result is None:
                add_url = """INSERT INTO urls (name, created_at)
                             VALUES (%s, %s)"""
                cursor.execute(add_url, (url, datetime.now()))
            else:
                raise URLError()

    def get_url(self, url_id):
        with DatabaseConnection(self.dsn, cursor_factory=RealDictCursor) as cursor:
            query = "SELECT id, name, created_at FROM urls WHERE id = %s"
            cursor.execute(query, (url_id,))
            url = cursor.fetchone()
        return url

    def get_id_url(self, url):
        with DatabaseConnection(self.dsn) as cursor:
            query = "SELECT id FROM urls WHERE name = %s"
            cursor.execute(query, (url,))
            result = cursor.fetchone()
            url_id = result[0]
        return url_id

    def get_all_urls(self):
        with DatabaseConnection(self.dsn, cursor_factory=RealDictCursor) as cursor:
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
        return urls

    def save_url_check(self, url_id, status_code, tags):
        with DatabaseConnection(self.dsn) as cursor:
            query = """INSERT INTO url_checks (
                        url_id, status_code, h1, title, description, created_at
                        )
                       VALUES (%s, %s, %s, %s, %s, %s)"""
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

    def get_all_url_checks(self, url_id):
        with DatabaseConnection(self.dsn, cursor_factory=RealDictCursor) as cursor:
            query = """SELECT
                           id,
                           status_code,
                           h1,
                           title,
                           description,
                           created_at
                       FROM url_checks
                       WHERE url_id = %s
                       ORDER BY created_at DESC"""
            cursor.execute(query, (url_id,))
            check_url = cursor.fetchall()
        return check_url
