from flask import Flask, request, make_response, jsonify, jsonify
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, current_user, get_jwt, set_access_cookies
import datetime
from dotenv import load_dotenv
load_dotenv()

app=Flask(__name__)
metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hiresynth.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://hiresynth_database_user:pLLTZ2OZASn2nWI8aKUv1XSVV0Ia9A17@dpg-cp5nlsq1hbls73fiu8sg-a.oregon-postgres.render.com/hiresynth_app_db"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://hiresynth_database_user:pLLTZ2OZASn2nWI8aKUv1XSVV0Ia9A17@dpg-cp5nlsq1hbls73fiu8sg-a.oregon-postgres.render.com/hiresynth_database"
app.config['JWT_SECRET_KEY'] = "381f65bc3f98ae33c4e3ae5b0dfe21a0fbe616800031657af772a6d961723ab9"
app.config['SQLALCHEMY_TRACK_MODIFICATONS'] = False
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=5)

db.init_app(app)
migrate=Migrate(app,db)
bcrypt=Bcrypt(app)
api=Api(app)
jwt = JWTManager(app)