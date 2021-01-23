import csv
import io
import os
import re
import requests
import xlrd
import zipfile

from bs4 import BeautifulSoup
from logger import logger
from urllib.parse import urlparse


def download_us_annual_records():
    url = 'https://www.ssa.gov/oact/babynames/names.zip'
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(os.path.join('data', 'us'))


def download_us_summary_record():
    url = 'https://www.ssa.gov/oact/babynames/numberUSbirths.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find('table', class_='t-stripe')

    with open(os.path.join('data', 'us', 'births_by_year.csv'), 'w') as f:
        writer = csv.writer(f)
        headers = [
            'year',
            'births_m',
            'births_f',
            'births_total'
        ]
        writer.writerow(headers)

        for row in table.find_all('tr'):
            tds = row.find_all('td')

            if len(tds) == 0:
                continue

            writer.writerow([int(td.text.replace(',', '')) for td in tds])


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
        self.extension = re.search(r'\.(xlsx?)$', self.filename).group(1)

        self.output_filename = f'{self.year}_{self.sex}.{self.extension}'

    def download_xls(self):
        if not os.path.exists(self.output_data_directory):
            os.makedirs(self.output_data_directory)

        if self.output_filename in os.listdir(self.output_data_directory):
            logger.warn(f'{self.output_filename} already exists')
            return

        r = requests.get(self.base_url + self.download_prefix + self.link)
        with open(os.path.join('data', 'uk', self.output_filename), 'wb') as f:
            f.write(r.content)


def download_uk_annual_records():
    archives = []
    for sex in ['boys', 'girls']:
        url = f'/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/' \
              f'datasets/babynamesenglandandwalesbabynamesstatistics{sex}'

        r = requests.get(UkArchive.base_url + url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug(r.headers)
            raise e

        soup = BeautifulSoup(r.content, 'lxml')
        links = soup.select('a.btn.btn--primary.btn--thick')

        for link in [l['href'] for l in links]:
            try:
                a = UkArchive(link)
                archives.append(a)
            except AttributeError as e:
                raise e

    for archive in archives:
        archive.download_xls()


def download_uk_summary_record():
    max_year = 2017
    url = 'https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/' \
          f'birthsdeathsandmarriages/livebirths/datasets/birthsummarytables/{max_year}/' \
          f'birthsummarytables{max_year}.xls'
    r = requests.get(url)

    with xlrd.open_workbook(file_contents=r.content) as book:
        pttrn = re.compile('table 1', re.IGNORECASE)
        index = [i for i, sht in enumerate(book.sheet_names()) if pttrn.search(sht)][0]
        sheet = book.sheet_by_index(index)
        start_row = [i for i in range(15) if sheet.row_values(i)[0] == max_year][0]

        years = []
        for i in range(start_row, sheet.nrows):
            if not all([c.ctype == 2 for c in sheet.row(i)[1:4]]):
                continue

            year, births_total, births_m, births_f = sheet.row_values(i)[0:4]
            years.append((int(year), int(births_m), int(births_f), int(births_total)))

    years.sort(key=lambda x: x[0])

    with open(os.path.join('data', 'uk', 'births_by_year.csv'), 'w') as f:
        writer = csv.writer(f)
        headers = [
            'year',
            'births_m',
            'births_f',
            'births_total'
        ]
        writer.writerow(headers)
        for y in years:
            writer.writerow(y)


if __name__ == '__main__':
    download_us_annual_records()
    download_us_summary_record()
    download_uk_annual_records()
    download_uk_summary_record()
