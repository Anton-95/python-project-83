from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup


def validate_url(url):
    return len(url) <= 255 and validators.url(url)


def normalization_url(url):
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    hostname = url_parse.netloc
    return f"{scheme.lower()}://{hostname.lower()}"


def get_status_code(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException:
        return False


def get_tags_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    h1 = soup.find("h1")
    if h1:
        h1 = h1.text
    else:
        h1 = ""

    title = soup.find("title")
    if title:
        title = title.text
    else:
        title = ""

    meta = soup.find("meta", {"name": "description"})
    if meta and "content" in meta.attrs:
        meta = meta["content"]
    else:
        meta = ""

    return {"h1": h1, "title": title, "description": meta}
