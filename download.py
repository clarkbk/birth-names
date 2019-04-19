import requests

from bs4 import BeautifulSoup
from objects import UkArchive


def download_uk_files():
    archives = []
    for sex in ['boys', 'girls']:
        url = f"/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/babynamesenglandandwalesbabynamesstatistics{sex}"

        r = requests.get(UkArchive.base_url + url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(r.headers)
            raise e

        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.select('a.btn.btn--primary.btn--thick')

        for link in [l['href'] for l in links]:
            try:
                a = UkArchive(link)
                archives.append(a)
            except AttributeError as e:
                raise e

    for archive in archives:
        archive.download_xls()


if __name__ == '__main__':
    download_uk_files()
