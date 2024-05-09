from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
# from flask_restful import Api, Resource
# import os
# from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required
# import datetime

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get(
#     "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'hospital.db')}")

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = '49b77a70efb919bcf7d37b1b05c7d149'
# app.config['JWT_ACCESS_TOKEN_EXPIRES']=datetime.timedelta(minutes=5)
# app.config['JWT_COOKIE_SECURE']=False
app.json.compact = False

db = SQLAlchemy(app) 
migrate = Migrate(app, db)  

# api = Api(app)
# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)