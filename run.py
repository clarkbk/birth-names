import csv
import re
import os

from database import db
from objects import Name, Year, BirthRecord
from tqdm import tqdm

data_directory = 'data'

db.create_tables([Name, Year, BirthRecord])

files = os.listdir(data_directory)
files.remove('NationalReadMe.pdf')
files.sort(reverse=True)

with tqdm(total=len(files)) as pbar0:
    for file in files:
        pbar0.set_description(f'{file.ljust(16)}')
        pbar0.update(1)

        fname, fext = os.path.splitext(file)
        if fext != '.txt':
            continue

        year_num = int(re.search(r'(\d{4})$', fname).group(1))
        year = Year.create(year=year_num)

        with open(os.path.join(data_directory, file), 'r') as f:
            reader = csv.reader(f)

            rows = sum(1 for row in reader)
            f.seek(0)

            birthrecords = []

            with tqdm(total=rows) as pbar1, db.atomic():
                for row in reader:
                    name_str, sex, births = list(row)

                    pbar1.set_description(f'{name_str.ljust(16)}')
                    pbar1.update(1)

                    name, created = Name.get_or_create(name=name_str, sex=sex)
                    birthrecords.append(BirthRecord(name=name, year=year, births=births))

            with db.atomic():
                BirthRecord.bulk_create(birthrecords, batch_size=500)
