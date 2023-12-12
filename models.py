from mongoengine import Document, StringField, IntField, ListField


class Employee(Document):
    name = StringField()
    age = IntField()
    teams = ListField()
    emp_id = IntField()


class User(Document):
    username = StringField()
    password = StringField()