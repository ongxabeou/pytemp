import datetime
import json
from abc import abstractmethod

from flask_mongoengine import MongoEngine

from src.common import COLLECTION_PATH

db = MongoEngine()


# todo: create relationship based on JSON data. quick fix is to disable 'required' arg

class BaseDocument(db.Document):
    created_date = db.DateTimeField(required=True)
    updated_date = db.DateTimeField(required=True)

    meta = {'allow_inheritance': True, 'abstract': True}

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = datetime.datetime.now()
        self.updated_date = datetime.datetime.now()
        return super(BaseDocument, self).save(*args, **kwargs)

    @abstractmethod
    def init_data(self, file_name):
        file_path = COLLECTION_PATH + file_name
        with open(file_path, 'r', encoding='UTF-8') as f:
            print(file_path)
            data = json.load(f)
            for obj in data:
                self.__init__(**obj)  # json as input
                self.save()


class BaseCategory(BaseDocument):
    _id = db.IntField(required=True, primary_key=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)

    meta = {'allow_inheritance': True, 'abstract': True}


class Organization(BaseDocument):
    _id = db.StringField(required=True, primary_key=True)
    name = db.StringField(required=True, unique=True)

    def init_data(self, file_name='Organization.json'):
        super().init_data(file_name)


class Province(BaseDocument):
    _id = db.IntField(required=True, primary_key=True)
    name = db.StringField(required=True)
    level = db.IntField(required=True, choices=[0, 1])
    country_code = db.StringField(required=True)

    def init_data(self, file_name='Province.json'):
        super().init_data(file_name)


class Severity(BaseCategory):

    def init_data(self, file_name='Severity.json'):
        super().init_data(file_name)


class Category(BaseCategory):
    group = db.StringField()

    def init_data(self, file_name='Category.json'):
        super().init_data(file_name)


def init_all_data():
    collections = [Organization(), Province(), Severity(), Category()]
    for c in collections:
        c.init_data()
