import os

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


# @app.post("/urls")
# def new_url():
#     url = request.form.get("url")
#     name_url = utils.normalization_url(url)

#     if not utils.validate_url(name_url):
#         flash("Некорректный URL", category="error")
#         return redirect(url_for("index", url=url), 422)

#     try:
#         db_manager.save_url(name_url)
#         url_id = db_manager.get_id_url(name_url)
#         flash("Страница успешно добавлена", category="success")
#         return redirect(url_for("get_url", url_id=url_id))
#     except db_manager.URLError:
#         url_id = db_manager.get_id_url(name_url)
#         flash("Страница уже существует", category="info")
#         return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls/<int:url_id>")
def get_url(url_id):
    messages = get_flashed_messages(with_categories=True)
    url = urls_repo.get_url(url_id)
    checks_url = urls_repo.get_all_url_checks(url_id)
    return render_template(
        "url.html", url=url, checks_url=checks_url, messages=messages
    )


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


@app.route("/urls", methods=["GET", "POST"])
def get_all_urls():

    if request.method == "POST":
        url = request.form.get("url")
        name_url = utils.normalizating_url(url)

        if not utils.validate_url(name_url):
            flash("Некорректный URL", category="error")
            messages = get_flashed_messages(with_categories=True)
            return render_template("index.html", url=url, messages=messages), 422
        try:
            urls_repo.save_url(name_url)
            url_id = urls_repo.get_id_url(name_url)
            flash("Страница успешно добавлена", category="success")
            return redirect(url_for("get_url", url_id=url_id))
        except db_manager.URLError:
            url_id = urls_repo.get_id_url(name_url)
            flash("Страница уже существует", category="info")
            return redirect(url_for("get_url", url_id=url_id))

    urls = urls_repo.get_all_urls()
    return render_template("urls.html", urls=urls)
