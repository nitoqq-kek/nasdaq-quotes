# -*- coding: utf-8 -*-
from flask import Flask

from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from nasdaq_quotes.serializers import ApiJSONEncoder

app = Flask(__name__)
app.config.from_object('nasdaq_quotes.config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)
app.json_encoder = ApiJSONEncoder

def init_modules():
    import commands
    import models
    import views

init_modules()
