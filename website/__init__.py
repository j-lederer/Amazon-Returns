from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from sqlalchemy import URL
import sqlalchemy
import stripe

db = SQLAlchemy()


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
  # url_object = URL.create(
  # #sqlUrl = sqlalchemy.engine.url.URL(
  #   drivername="mysql+pymysql",
  #   username=os.getenv("DB_USER"),
  #   password=os.getenv("DB_PASSWORD"),
  #   host=os.getenv("DB_HOST"),
  #   database=os.getenv("DB_DATABASE"),
  #   query={
  #     "ssl_ca":"/etc/ssl/cert.pem"},
  # )
  app.config['SQLALCHEMY_DATABASE_URI'] =os.environ['RAILWAY_DB_CONNECTION_STRING']
  app.config['STRIPE_PUBLIC_KEY'] = os.environ['STRIPE_TEST_PUBLIC_KEY']
  app.config['STRIPE_SECRET_KEY'] = os.environ['STRIPE_TEST_SECRET_KEY'] 
  #os.environ[
  #   'DB2'] + '?ssl_ca=website/addedExtras/cacert-2023-05-30.pem'
  #/etc/ssl/cert.pem'
  # app.config['SQLALCHEMY_DATABASE_URI'] = url_object
  #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.init_app(app)
  migrate = Migrate(app, db)
  stripe.api_key = app.config['STRIPE_SECRET_KEY']
  from .views import views
  from .auth import auth
  from .stripePay import stripePay
  from .connectAmazon import connectAmazon

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')
  app.register_blueprint(stripePay, url_prefix='/')
  app.register_blueprint(connectAmazon, url_prefix='/')
  

  from .models import User
  #, Note

  with app.app_context():
    db.create_all()

  login_manager = LoginManager()
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(id):
    return User.query.get(int(id))

  return app
