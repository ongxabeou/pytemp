import datetime
import json

from flask_mongoengine import MongoEngine

from src.common import COLLECTION_PATH, SECTION, MONGO_CONFIG
from src.common.system_config import SystemConfig

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

    def init_data(self, file_name=None):
        if file_name:
            file_path = "{path}{name}.json".format(path=COLLECTION_PATH, name=file_name)
        else:
            file_path = "{path}{name}.json".format(path=COLLECTION_PATH, name=self.__class__.__name__)
        with open(file_path, 'r', encoding='UTF-8') as f:
            SystemConfig().logger.info('init collection from file: %s' % file_path)
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


class Province(BaseDocument):
    _id = db.IntField(required=True, primary_key=True)
    name = db.StringField(required=True)
    level = db.IntField(required=True, choices=[0, 1])
    country_code = db.StringField(required=True)


class Severity(BaseCategory):
    pass


class Category(BaseCategory):
    group = db.StringField()


def init_all_data():
    SystemConfig().logger.info(
        'init database: %s' % SystemConfig().get_section_map(SECTION.MONGODB_SETTINGS)[MONGO_CONFIG.DB])
    collections = [Organization(), Province(), Severity(), Category()]
    for c in collections:
        c.init_data()
