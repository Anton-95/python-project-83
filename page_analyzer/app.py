import os
import secrets
from datetime import datetime
from unittest import result
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, url_for
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
    url_parse = urlparse(url)

    if not validate_url(url):
        flash("Некорректная ссылка", category="error")
        return redirect(url_for("index", url=url))

    hostname = url_parse.hostname
    conn = psycopg2.connect(DATABASE_URL)
    query_name = "SELECT id, name FROM urls WHERE name = %s"

    with conn.cursor() as cursor:
        cursor.execute(query_name, (hostname,))
        result = cursor.fetchone()
        if result is None:
            add_url = """INSERT INTO
                            urls (name, created_at)
                         VALUES
                            (%s, %s) RETURNING id"""
            cursor.execute(add_url, (hostname, datetime.now()))
            url_id = cursor.fetchone()[0]
        else:
            url_id = result[0]
            flash("Такой адрес уже существует", category="info")
            return redirect(url_for("get_url", url_id=url_id))

    conn.commit()
    conn.close()
    flash("Ссылка успешно добавлена", category="success")
    return redirect(url_for("get_url", url_id=url_id))


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

    conn.close()
    return render_template("url.html", url=url, messages=messages)


@app.route("/urls")
def get_urls():
    query = "SELECT id, name, created_at FROM urls ORDER BY created_at DESC"
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query)
        urls = cursor.fetchall()

    conn.close()
    if urls is None:
        return render_template("urls.html", urls="")
    return render_template("urls.html", urls=urls)
