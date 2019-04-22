import os
import re
import requests

from bs4 import BeautifulSoup
from logger import logger
from urllib.parse import urlparse


class UkArchive(object):
    base_url = "https://www.ons.gov.uk"
    download_prefix = '/file?uri='
    output_data_directory = os.path.join('data', 'uk')

    def __init__(self, link):
        self.link = link.replace(self.download_prefix, '')

        p = urlparse(self.link)
        self.filename = os.path.basename(p.path)

        self.year = int(re.search(r'(\d{4})', self.filename).group(0))

        sexes = {
            'boy': 'M',
            'girl': 'F'
        }
        self.sex = sexes[re.search(r'(boy|girl)', self.filename).group(0)]

        self.output_filename = f'{self.year}_{self.sex}.xls'

    def download_xls(self):
        if self.output_filename in os.listdir(self.output_data_directory):
            logger.warn(f'{self.output_filename} already exists')
            return

        r = requests.get(self.base_url + self.download_prefix + self.link)
        with open(os.path.join('data', 'uk', self.output_filename), 'wb') as f:
            f.write(r.content)


def download_uk_files():
    archives = []
    for sex in ['boys', 'girls']:
        url = f'/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/' \
              'datasets/babynamesenglandandwalesbabynamesstatistics{sex}'

        r = requests.get(UkArchive.base_url + url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug(r.headers)
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
