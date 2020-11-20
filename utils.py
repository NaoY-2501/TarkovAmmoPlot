import io
from pathlib import Path

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

BASE_URL = "https://escapefromtarkov.gamepedia.com"
BASE_PATH = "cache/{}.html"


def get_soup(path):
    filepath = Path(BASE_PATH.format(path))
    url = f"{BASE_URL}/{path}"
    if not filepath.exists():
        body = requests.get(url).content
        soup = bs(body, "html.parser")
        save_soup(soup, filepath.absolute())
    soup = load_soup(filepath.absolute())
    return soup


def save_soup(soup: bs, doc_name: str):
    with open(doc_name, "w", encoding="utf-8") as f:
        f.write(soup.prettify())


def load_soup(doc_name):
    with open(doc_name, "r", encoding="utf-8") as f:
        return bs(f, "html.parser")


def make_dfs_from_doc(doc):
    f = io.StringIO(str(doc))
    dfs = pd.read_html(f)
    return dfs


def retrieve_ammo_types(soup):
    docs = soup.find_all("table", class_="wikitable")
    all_types = []
    for doc in docs:
        dfs = make_dfs_from_doc(doc)
        type_names = dfs[0]["Name"].values
        all_types.extend(type_names)
    return all_types
