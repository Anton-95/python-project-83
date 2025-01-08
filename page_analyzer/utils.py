from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup


def validating_url(url):
    return len(url) <= 255 and validators.url(url)


def normalizating_url(url):
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    hostname = url_parse.netloc
    return f"{scheme.lower()}://{hostname.lower()}"


def get_response(url):
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    return response


def get_status_code(response):
    return response.status_code


def get_tags_url(response):
    soup = BeautifulSoup(response.text, "html.parser")

    find_h1 = soup.find("h1")
    h1 = find_h1.text if find_h1 else ""

    find_title = soup.find("title")
    title = find_title.text if find_title else ""

    find_meta = soup.find("meta", {"name": "description"})
    if find_meta and "content" in find_meta.attrs:
        meta = find_meta["content"]
    else:
        meta = ""

    return {"h1": h1, "title": title, "description": meta}
