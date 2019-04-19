import os

from peewee import CharField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import Model
from peewee import PostgresqlDatabase


db = PostgresqlDatabase(os.environ['DB_NAME'],
                        user=os.environ['DB_USER'],
                        password=os.environ['DB_PASSWORD'],
                        host=os.environ['DB_URL'],
                        port=5342,)


class BaseModel(Model):
    class Meta:
        database = db


class DbName(BaseModel):
    def __eq__(self, other):
        return (self.name.lower() == other.name.lower())

    name = CharField()
    # soundex = CharField(max_length=4)
    # dmeta = CharField(max_length=4)

    class Meta:
        indexes = (
            (('name'), True),
        )
        table_name = 'name'


class DbYear(BaseModel):
    year = IntegerField(primary_key=True)
    # us_births = IntegerField()
    # uk_births = IntegerField()

    class Meta:
        table_name = 'year'


class DbBirthRecord(BaseModel):
    country = CharField(max_length=2)
    year = ForeignKeyField(DbYear, backref='birth_records')
    name = ForeignKeyField(DbName, backref='birth_records')
    sex = CharField(max_length=1)
    births = IntegerField()

    class Meta:
        table_name = 'birth_record'
