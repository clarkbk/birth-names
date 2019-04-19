import csv
import os
import re
import xlrd

from database import db, DbName, DbYear, DbBirthRecord
from objects import UkArchive
from utils import Utils
# from tqdm import tqdm


def process_us_files():

    data_directory = os.path.join('data', 'us')

    files = os.listdir(data_directory)
    files.sort(reverse=True)

    files = filter(Utils.US.is_valid_file, files)

    for file in files:
        year_num = int(re.search(r'(\d{4})', file).group(1))
        year = DbYear.get_or_create(year=year_num)

        with open(os.path.join(data_directory, file), 'r') as f:
            reader = csv.reader(f)

            birthrecords = []
            with db.atomic():
                for row in reader:
                    name_str, sex, births = list(row)

                    name, created = DbName.get_or_create(name=name_str,
                                                         soundex=soundex,
                                                         dmeta=dmeta)

                    birthrecords.append(DbBirthRecord(country='us',
                                                      year=year,
                                                      name=name,
                                                      sex=sex,
                                                      births=births))

            with db.atomic():
                DbBirthRecord.bulk_create(birthrecords, batch_size=500)


def process_uk_files():

    data_directory = UkArchive.output_data_directory

    files = os.listdir(data_directory)
    files.sort(reverse=True)

    files = filter(Utils.UK.is_valid_file, files)

    for file in files:
        year_num, sex = Utils.UK.extract_data_from_filename(file)
        year = DbYear.get_or_create(year=year_num)

        with xlrd.open_workbook(os.path.join(data_directory, file)) as book:
            sheet_idx = Utils.UK.find_correct_worksheet(book)
            sheet = book.sheet_by_index(sheet_idx)
            start_row = Utils.UK.find_start_row(sheet)

            birthrecords = []
            with db.atomic():
                for i in range(sheet.nrows):
                    if i <= start_row:
                        continue

                    row = [c for c in sheet.row(i) if not Utils.UK.cell_is_empty(c)]
                    if not Utils.UK.is_valid_row(row):
                        continue

                    name_str, births = row[1:2]
                    name, created = DbName.get_or_create(name=name_str,
                                                         soundex=soundex,
                                                         dmeta=dmeta)

                    birthrecords.append(DbBirthRecord(country='uk',
                                                      year=year,
                                                      name=name,
                                                      sex=sex,
                                                      births=births))

                    # TODO: use fuzzy to generate soundex & dmetaphone values
                    # TODO: check that refactored code still works/runs
                    # TODO: write code to commit UK records to db via peewee model
                    # TODO: re-add command line progress meter via tqdm (?)
                    # TODO: truncate tables and re run everything
                    # TODO: update README
                    # TODO: push to remote


if __name__ == '__main__':
    # db.create_tables([Name, Year, BirthRecord])

    process_us_files()
    # process_uk_files()
