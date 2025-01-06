import os
import secrets
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from psycopg2.extras import RealDictCursor

load_dotenv()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DATABASE_URL = os.getenv("DATABASE_URL")


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    url = request.args.get("url", "")
    return render_template("index.html", url=url, messages=messages)


@app.post("/")
def new_url():
    url = request.form.get("url")
    name_url = get_name_url(url)

    if not validate_url(url):
        flash("Некорректная ссылка", category="error")
        return redirect(url_for("index", url=url))

    conn = psycopg2.connect(DATABASE_URL)
    query_name = "SELECT id, name FROM urls WHERE name = %s"

    with conn.cursor() as cursor:
        cursor.execute(query_name, (name_url,))
        result = cursor.fetchone()
        if result is None:
            add_url = """INSERT INTO
                            urls (name, created_at)
                         VALUES
                            (%s, %s) RETURNING id"""
            cursor.execute(add_url, (name_url, datetime.now()))
            url_id = cursor.fetchone()[0]
        else:
            url_id = result[0]
            flash("Такой адрес уже существует", category="info")
            return redirect(url_for("get_url", url_id=url_id))

    conn.commit()
    conn.close()
    flash("Ссылка успешно добавлена", category="success")
    return redirect(url_for("get_url", url_id=url_id))


def get_name_url(url):
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    hostname = url_parse.netloc
    return f"{scheme}://{hostname}"


def validate_url(url):
    return len(url) <= 255 and validators.url(url)


@app.route("/urls/<int:url_id>")
def get_url(url_id):
    messages = get_flashed_messages(with_categories=True)
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT id, name, created_at FROM urls WHERE id = %s"

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, (url_id,))
        url = cursor.fetchone()

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

    return render_template("url.html", url=url, check_url=check_url, messages=messages)


@app.post("/urls/<int:url_id>/checks")
def new_check(url_id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cursor:
        query = "SELECT name FROM urls WHERE id = %s"
        cursor.execute(query, (url_id,))
        url = cursor.fetchone()

    try:
        response = requests.get(url[0])
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", category="error")
        return redirect(url_for("get_url", url_id=url_id))

    status_code = response.status_code

    soup = BeautifulSoup(response.text, "html.parser")
    tag_h1 = soup.find("h1")
    if tag_h1:
        tag_h1 = tag_h1.text
    else:
        tag_h1 = ""

    tag_title = soup.find("title")
    if tag_title:
        tag_title = tag_title.text
    else:
        tag_title = ""

    tag_meta = soup.find("meta", {"name": "description"})
    if tag_meta and "content" in tag_meta.attrs:
        tag_meta = tag_meta["content"]
    else:
        tag_meta = ""

    with conn.cursor() as cursor:
        query = """INSERT INTO url_checks (
                       url_id, status_code, h1, title, description, created_at
                       )
                   VALUES
                       (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(
            query, (url_id, status_code, tag_h1, tag_title, tag_meta, datetime.now())
        )

    conn.commit()
    flash("Страница успешно проверена", category="success")
    return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls")
def get_all_urls():
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
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query)
        urls = cursor.fetchall()

    conn.close()

    if urls is None:
        return render_template("urls.html", urls="")
    return render_template("urls.html", urls=urls)
