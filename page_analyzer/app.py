import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer import db_manager, utils

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

urls_repo = db_manager.UrlsRepository(DATABASE_URL)


@app.route("/")
def index():
    url = request.args.get("url", "")
    return render_template("index.html", url=url)


@app.post("/urls")
def new_url():
    url = request.form.get("url")
    name_url = utils.normalizating_url(url)

    if not utils.validating_url(name_url):
        flash("Некорректный URL", category="error")
        return render_template("index.html", url=url), 422

    try:
        url_id = urls_repo.save_url(name_url)
    except db_manager.URLError:
        url_id = urls_repo.get_id_url(name_url)
        flash("Страница уже существует", category="info")
        return redirect(url_for("get_url", url_id=url_id))

    flash("Страница успешно добавлена", category="success")
    return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls/<int:url_id>")
def get_url(url_id):
    url = urls_repo.get_url(url_id)
    checks_url = urls_repo.get_all_url_checks(url_id)
    return render_template("url.html", url=url, checks_url=checks_url)


@app.post("/urls/<int:url_id>/checks")
def new_check(url_id):
    url = urls_repo.get_url(url_id)["name"]
    response = utils.get_response(url)

    if response is None:
        flash("Произошла ошибка при проверке", category="error")
        return redirect(url_for("get_url", url_id=url_id))

    status_code = utils.get_status_code(response)
    tags = utils.get_tags_url(response)
    urls_repo.save_url_check(url_id, status_code, tags)
    flash("Страница успешно проверена", category="success")
    return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls")
def get_all_urls():
    urls = urls_repo.get_all_urls()
    return render_template("urls.html", urls=urls)
