import inflection
import os

from datetime import datetime
from logger import logger
from peewee import Check, Model, SQL
from peewee import CharField, DateTimeField, ForeignKeyField, IntegerField
from peewee import PostgresqlDatabase
from phonetics import dmetaphone, soundex


db = PostgresqlDatabase(os.environ['DB_NAME'],
                        user=os.environ['DB_USER'],
                        password=os.environ['DB_PASSWORD'],
                        host=os.environ['DB_URL'],
                        port=5432,)


def make_table_name(model_class):
    return inflection.underscore(model_class.__name__.replace('Db', ''))


class BaseModel(Model):
    class Meta:
        database = db
        table_function = make_table_name


class DbName(BaseModel):
    name = CharField(index=True, unique=True)
    soundex = CharField(max_length=20)
    dmeta = CharField(max_length=20)
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    def __eq__(self, other):
        return (self.name.lower() == other.name.lower())


class DbYear(BaseModel):
    year = IntegerField(primary_key=True,
                        constraints=[Check('year between 1800 and 2100')])
    births_us_m = IntegerField(null=True)
    births_us_f = IntegerField(null=True)
    births_uk_m = IntegerField(null=True)
    births_uk_f = IntegerField(null=True)
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class DbBirthRecord(BaseModel):
    country = CharField(max_length=2)
    year = ForeignKeyField(DbYear, backref='birth_records')
    name = ForeignKeyField(DbName, backref='birth_records')
    sex = CharField(max_length=1, constraints=[Check("sex in ('M', 'F')")])
    births = IntegerField()
    updated_at = DateTimeField(default=datetime.now)


class MyBirthRecord(object):
    def __init__(self, country, year, name, sex, births):
        self.country = country
        self.year = year
        self.name = name.strip()
        self.sex = sex
        self.births = births

        phonetic_str = self.name.lower()
        for r in (('-', ''), ('\'', ''), ('.', '')):
            phonetic_str = phonetic_str.replace(*r)

        try:
            self.soundex = soundex(phonetic_str)
            self.dmeta = dmetaphone(phonetic_str)[0]
        except IndexError as e:
            logger.debug(phonetic_str)
            raise e

    def make_db_record(self):
        with db.atomic():
            year, created = DbYear.get_or_create(year=self.year)

            name, created = DbName.get_or_create(name=self.name,
                                                 soundex=self.soundex,
                                                 dmeta=self.dmeta)

            return DbBirthRecord(country=self.country,
                                 year=year,
                                 name=name,
                                 sex=self.sex,
                                 births=self.births)


if __name__ == '__main__':
    db.create_tables([DbName, DbYear, DbBirthRecord])
