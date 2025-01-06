from email import message
import secrets

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

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    url = request.args.get("url", "")
    return render_template("index.html", url=url, messages=messages)


@app.post("/")
def new_url():
    url = request.form.get("url")
    name_url = utils.normalization_url(url)

    if not utils.validate_url(name_url):
        flash("Некорректный URL", category="error")
        return redirect(url_for("get_all_urls", url=url))

    try:
        db_manager.save_url(name_url)
        url_id = db_manager.get_id_url(name_url)
        flash("Страница успешно добавлена", category="success")
        return redirect(url_for("get_url", url_id=url_id))
    except db_manager.URLError:
        url_id = db_manager.get_id_url(name_url)
        flash("Страница уже существует", category="info")
        return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls/<int:url_id>")
def get_url(url_id):
    messages = get_flashed_messages(with_categories=True)
    url = db_manager.get_url(url_id)
    checks_url = db_manager.get_all_url_checks(url_id)
    return render_template(
        "url.html", url=url, checks_url=checks_url, messages=messages
    )


@app.post("/urls/<int:url_id>/checks")
def new_check(url_id):
    url = db_manager.get_url(url_id)["name"]
    status_code = utils.get_status_code(url)

    if status_code:
        tags = utils.get_tags_url(url)
        db_manager.save_url_check(url_id, status_code, tags)
        flash("Страница успешно проверена", category="success")
        return redirect(url_for("get_url", url_id=url_id))
    else:
        flash("Произошла ошибка при проверке", category="error")
        return redirect(url_for("get_url", url_id=url_id))


@app.route("/urls")
def get_all_urls(url=''):
    messages = get_flashed_messages(with_categories=True)
    if messages:
        return render_template("index.html", url=url, messages=messages)
    urls = db_manager.get_all_urls()
    return render_template("urls.html", urls=urls)
