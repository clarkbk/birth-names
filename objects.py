import fuzzy
import os
import re
import requests

from urllib.parse import urlparse


soundex = fuzzy.Soundex(4)
dmeta = fuzzy.DMetaphone()


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
            print(f'{self.output_filename} already exists')
            return

        r = requests.get(self.base_url + self.download_prefix + self.link)
        with open(os.path.join('data', 'uk', self.output_filename), 'wb') as f:
            f.write(r.content)


class Name(object):
    def __init__(self, name):
        self.name = name
        self.soundex = soundex(name)
        self.dmeta = dmeta(name)[0]
