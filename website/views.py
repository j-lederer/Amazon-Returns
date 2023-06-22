from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from database import engine, load_queue_from_db, load_all_return_details_from_db, load_tracking_id_to_search, delete_trackingID_from_queue_db, add_tracking_id_to_queue, refresh_all_return_data_in_db, load_current_return_to_display_from_db, add_current_return_to_display_to_db, delete_whole_tracking_id_queue, delete_current_return_to_display_from_db, delete_tracking_id_to_search, add_tracking_id_to_search, check_if_track_in_queue, delete_current_return_to_display_from_db, refresh_addresses_in_db, load_address_from_db

from amazonAPI import get_all_Returns_data, increaseInventory, checkInventory, checkInventoryIncrease, get_addresses_from_GetOrders

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)






@views.route('/', methods=['POST', 'GET'])
@login_required
def home(): 
  #returnDetails = load_returnDetails_from_db()
  All_Return_Details = load_all_return_details_from_db()
  tracking_id=None
  return_details_to_display=None
  Address='No Data'
  queueChecker = "NO"
 
  
  if load_tracking_id_to_search():
    tracking_id = load_tracking_id_to_search()
    if check_if_track_in_queue(tracking_id):
      queueChecker = "YES"
    
    addresses= load_address_from_db()

  
    add_current_return_to_display_to_db(tracking_id)
  return_details_to_display = load_current_return_to_display_from_db()
  queue = load_queue_from_db()
  if (return_details_to_display and tracking_id):  #if they exist
    print(return_details_to_display)
    orderID = return_details_to_display['order_id']
    for data in addresses:
      if data['OrderID'] == orderID:
        Address = data['Address']
        #print(Address)
    return render_template('home.html', tasks=queue, passed_value = return_details_to_display, tracking_id=tracking_id, queue_checker=queueChecker, address=Address,  user=current_user)
        

  else: 
      return render_template('home.html', tasks=queue,  user=current_user)
      
@views.route('/refresh_returns_and_inventory')
def refresh():
    #Get all the new return data with a call from amazonAPI.py
    #print(get_all_Returns_data())
    print("Refreshing Returns and Inventory data:")
    print("Getting returns data: ")
    all_return_data = get_all_Returns_data()
    print(all_return_data)
    inventory_data = checkInventory()
    addressData = get_addresses_from_GetOrders()
    refresh_all_return_data_in_db(all_return_data, inventory_data)
    refresh_addresses_in_db(addressData)
    try:
        #remove the previous return details from db
        #and add the new return details to db
        return redirect('/')
    except:
        return 'There was a problem refreshing your returns'



@views.route('/info_for_tracking_id', methods =[ 'POST', 'GET'])
def get_info_on_track():
    trackingID = request.form['track']
    print(trackingID)
    delete_tracking_id_to_search()
    add_tracking_id_to_search(trackingID)
    return redirect('/')
    
    #task_to_delete = TrackingIDS.query.get_or_404(id)
    #update the database to include data for the return

    try:
        #db.session.delete(task_to_delete)
        #db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem getting the info for this return'

@views.route('/increase_inventory', methods =['POST', 'GET'])
def increase_inventory():
  #take the tracking id's in the queue and increase inventory by the return order amount for each
  Quantity_of_SKUS = checkInventory()
  result = increaseInventory(Quantity_of_SKUS)
  print(type(result[1]))
  print(result[1])
  result = checkInventoryIncrease(Quantity_of_SKUS, result[1])
  print(result)
  if result == "Inventory Increased Successfully":
    delete_tracking_id_to_search()
    delete_current_return_to_display_from_db()
  
  return redirect('/')

@views.route('/delete/<tracking>')
def delete(tracking):
    delete_trackingID_from_queue_db(tracking)
    return redirect('/')
  
    try:
        delete_trackingID_from_queue_db(tracking)
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@views.route('/add_trackingID', methods=['POST', 'GET'])
def add_tracking_id():
    tracking_id = request.form
    print('test')
    #print(tracking_id)
    queue = load_queue_from_db() 
    for track in queue:
      if track['tracking'] == tracking_id:
        print("Tracking ID is already in queue")
        return redirect ('/')
    print("Successfully Added Tracking ID to Queue.")
    add_tracking_id_to_queue(tracking_id['added_track'])
    return redirect('/')
    
    try:
      add_tracking_id_to_queue(tracking_id['added_track'])
      return redirect('/')

    except:
      return 'There was a problem adding the Tracking ID to your queue'
@views.route('/add_to_queue_button', methods=['POST', 'GET'])
def add_to_queue():
  result=request.form
  print(result)
  tracking_id = load_tracking_id_to_search()
  return_data = load_current_return_to_display_from_db()
  quantity_of_return = return_data['return_quantity']
  sku = return_data['sku']
  queue = load_queue_from_db() 
  
  print(return_data)
  if return_data['order_id'] == 'Not Found':
    print('Cannot add unknown tracking id to queue')
    return redirect('/')
  for track in queue:
      #print(track['tracking'])
      if track['tracking'] == tracking_id:
        print("Tracking ID is already in queue")
        return redirect ('/')
  print("Successfully Added Tracking ID to Queue.")
  add_tracking_id_to_queue(tracking_id, sku, quantity_of_return)
  return redirect('/')

@views.route('/search', methods=['POST','GET'])
def search():
  delete_tracking_id_to_search()
  delete_current_return_to_display_from_db()
  tracking_id = request.form
  add_tracking_id_to_search(tracking_id)
#add_current_return_to_display_to_db(tracking_id)
  return redirect('/')
@views.route('/clearSearch')
def clearSearch():
  delete_tracking_id_to_search()
  delete_current_return_to_display_from_db()
  return redirect('/')
@views.route('/clearQueue')
def clearQueue():
  delete_whole_tracking_id_queue()
  return redirect('/')

"""  
     
def inventoryCheck():
    run_script_checkInventoryIncrease(passed_valuefromHTML[Quantity_of_SKU], passed_valuefromHTML[return_quantity]):
    


    return render_template('Amazon.html', passed_value_inventoryCheck = output_data)
   """

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)