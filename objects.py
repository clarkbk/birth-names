from database import db

from peewee import CharField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import Model


class BaseModel(Model):
    class Meta:
        database = db


class Name(Model):
    def __eq__(self, other):
        return (self.name == other.name and self.sex == other.sex)

    name = CharField()
    sex = CharField()

    class Meta:
        database = db
        indexes = (
            (('name', 'sex'), True),
        )


class Year(BaseModel):
    year = IntegerField(primary_key=True)


class BirthRecord(BaseModel):
    name = ForeignKeyField(Name, backref='birth_records')
    year = ForeignKeyField(Year, backref='birth_records')
    births = IntegerField()
