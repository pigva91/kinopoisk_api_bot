from peewee import (
    SqliteDatabase,
    Model,
    TextField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    FloatField,
)
from datetime import datetime

db = SqliteDatabase("bot_history.db")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(primary_key=True)


class History(BaseModel):
    movie_name = TextField()
    description = TextField()
    rating = FloatField()
    year = IntegerField()
    genre = TextField()
    age_rating = TextField(null=True)
    poster_url = TextField(null=True)
    user = ForeignKeyField(User, backref="histories")
    timestamp = DateTimeField(default=datetime.now)
    search_type = TextField()


db.connect()
db.create_tables([User, History])