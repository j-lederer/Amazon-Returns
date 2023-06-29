from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
class Addresses(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  OrderID = db.Column(db.String(250))
  Address = db.Column(db.String(500))
  date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class All_return_details(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tracking_id = db.Column(db.String(250))
  item_name = db.Column(db.String(500))
  sku = db.Column(db.String(500))
  return_quantity = db.Column(db.String(500))
  refund_amount = db.Column(db.String(500))
  order_id = db.Column(db.String(500))
  order_quantity = db.Column(db.String(500))
  asin = db.Column(db.String(500))
  Inventory = db.Column(db.String(500))
  reason_returned = db.Column(db.String(500))
  date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class Current_return_to_display(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tracking_id = db.Column(db.String(250))
  item_name = db.Column(db.String(500))
  sku = db.Column(db.String(500))
  return_quantity = db.Column(db.String(500))
  refund_amount = db.Column(db.String(500))
  order_id = db.Column(db.String(500))
  order_quantity = db.Column(db.String(500))
  asin = db.Column(db.String(500))
  Inventory = db.Column(db.String(500))
  reason_returned = db.Column(db.String(500))
  date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class Tracking_id_to_search(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tracking_id = db.Column(db.String(250))
  date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class Tracking_ids(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tracking = db.Column(db.String(250))
  SKU = db.Column(db.String(250))
  return_quantity = db.Column(db.String(250))
  date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(150), unique=True)
  password = db.Column(db.String(150))
  first_name = db.Column(db.String(150))
  addresses = db.relationship('Addresses', backref='addresses_ref', passive_deletes=True)
  all_return_details = db.relationship('All_return_details',
                                       backref='all_return_details_ref', passive_deletes=True)
  current_return_to_display = db.relationship(
    'Current_return_to_display', backref='current_return_to_display_ref', passive_deletes=True)
  tracking_id_to_search = db.relationship('Tracking_id_to_search',
                                          backref='tracking_id_to_search_ref', passive_deletes=True )
  tracking_ids = db.relationship('Tracking_ids', backref='tracking_ids_ref', passive_deletes=True)
