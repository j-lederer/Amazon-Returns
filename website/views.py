from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .database import engine, load_queue_from_db, load_all_return_details_from_db, load_tracking_id_to_search, delete_trackingID_from_queue_db, add_tracking_id_to_queue, refresh_all_return_data_in_db, load_current_return_to_display_from_db, add_current_return_to_display_to_db, delete_whole_tracking_id_queue, delete_current_return_to_display_from_db, delete_tracking_id_to_search, add_tracking_id_to_search, check_if_track_in_queue, delete_current_return_to_display_from_db, refresh_addresses_in_db, load_address_from_db, load_users_from_db, load_deleted_users_from_db, delete_user_from_db, delete_deleted_user_from_db, clear_all_users_from_db, clear_all_deleted_users_from_db, add_refresh_token, get_refresh_token, load_restricted, add_request_to_delete_user

from .amazonAPI import get_all_Returns_data, increaseInventory, checkInventory, checkInventoryIncrease, get_addresses_from_GetOrders

from flask import Blueprint, render_template, request, flash, jsonify, send_file, make_response
from flask_login import login_required, current_user
from .models import Stripecustomer
import stripe
from . import db
import json
from io import BytesIO
import os

from .download_pdf_queue import download_queue_data
from .download_pdf_inventoryChange import download_queue_and_inventory_change_data

views = Blueprint('views', __name__)



@views.route('/', methods=['POST', 'GET'])
@login_required
def home(): 
  # print(current_user)
  # print(current_user.id)  #returnDetails = load_returnDetails_from_db()
  All_Return_Details = load_all_return_details_from_db(current_user.id)
  tracking_id=None
  return_details_to_display=None
  Address='No Data'
  queueChecker = "NO"
  
 
  
  if load_tracking_id_to_search(current_user.id):
    tracking_id = load_tracking_id_to_search(current_user.id)
    if check_if_track_in_queue(tracking_id, current_user.id):
      queueChecker = "YES"
    
    addresses= load_address_from_db(current_user.id)

  
    add_current_return_to_display_to_db(tracking_id, current_user.id)
  return_details_to_display = load_current_return_to_display_from_db(current_user.id)
  queue = load_queue_from_db(current_user.id)

  customer = Stripecustomer.query.filter_by(user_id=current_user.id).order_by(Stripecustomer.id.desc()).first()
  subscription = None
  if customer:
        subscription = stripe.Subscription.retrieve(customer.stripeSubscriptionId)
        product = stripe.Product.retrieve(subscription.plan.product)
        context = {
            "subscription": subscription,
            "product": product,
        }
    
  if(not load_restricted(current_user.id)):
    if(get_refresh_token (current_user.id)):
      if (subscription and subscription.status=='active'):
        if (return_details_to_display and tracking_id and customer):  #if they exist
          print(return_details_to_display)
          orderID = return_details_to_display['order_id']
          for data in addresses:
            if data['OrderID'] == orderID:
              Address = data['Address']
              #print(Address)
          return render_template('home.html', tasks=queue, passed_value = return_details_to_display, tracking_id=tracking_id, queue_checker=queueChecker, address=Address,  user=current_user, **context)
        else: 
            return render_template('home.html', tasks=queue,  user=current_user)
      
      else:
        flash('Account not complete. You do not have access to this page. Your are not subscribed.', category='error')
        return redirect('/account')
    else: 
      flash('Account not complete. You do not have access to this page. Your AmazonSellerCentral account is not linked.', category='error')
      return redirect('/account')
  else:
    flash('Your account is Restricted. Please contact us for more information.', category='error')
    return redirect('/account')
      
@views.route('/refresh_returns_and_inventory')
@login_required
def refresh():
    #Get all the new return data with a call from amazonAPI.py
    #print(get_all_Returns_data())
    print("Refreshing Returns and Inventory data:")
    print("Getting returns data: ")
    all_return_data = get_all_Returns_data(current_user.refresh_token)
    print(all_return_data)
    inventory_data = checkInventory(current_user.refresh_token)
    addressData = get_addresses_from_GetOrders(current_user.refresh_token)
    refresh_all_return_data_in_db(all_return_data, inventory_data, current_user.id)
    refresh_addresses_in_db(addressData, current_user.id)
    try:
        #remove the previous return details from db
        #and add the new return details to db
        return redirect('/')
    except:
        return 'There was a problem refreshing your returns'



@views.route('/info_for_tracking_id', methods =[ 'POST', 'GET'])
@login_required
def get_info_on_track():
    trackingID = request.form['track']
    print(trackingID)
    delete_tracking_id_to_search(current_user.id)
    add_tracking_id_to_search(trackingID, current_user.id)
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
@login_required
def increase_inventory():
  #take the tracking id's in the queue and increase inventory by the return order amount for each
  Quantity_of_SKUS = checkInventory( current_user.refresh_token)
  result = increaseInventory(Quantity_of_SKUS, current_user.id,  current_user.refresh_token)
  print(type(result[1]))
  print(result[1])
  result = checkInventoryIncrease(Quantity_of_SKUS, result[1], current_user.refresh_token)
  print(result)
  if result == "Inventory Increased Successfully":
    delete_tracking_id_to_search(current_user.id)
    delete_current_return_to_display_from_db(current_user.id)
  
  return redirect('/')

@views.route('/delete/<tracking>')
@login_required
def delete(tracking):
    delete_trackingID_from_queue_db(tracking, current_user.id)
    return redirect('/')
  
    try:
        delete_trackingID_from_queue_db(tracking, current_user.id)
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@views.route('/add_trackingID', methods=['POST', 'GET'])
@login_required
def add_tracking_id():
    tracking_id = request.form
    print('test')
    #print(tracking_id)
    queue = load_queue_from_db(current_user.id) 
    for track in queue:
      if track['tracking'] == tracking_id:
        print("Tracking ID is already in queue")
        return redirect ('/')
    print("Successfully Added Tracking ID to Queue.")
    add_tracking_id_to_queue(tracking_id['added_track'], current_user.id)
    return redirect('/')
    
    try:
      add_tracking_id_to_queue(tracking_id['added_track'], current_user.id)
      return redirect('/')

    except:
      return 'There was a problem adding the Tracking ID to your queue'
@views.route('/add_to_queue_button', methods=['POST', 'GET'])
def add_to_queue():
  result=request.form
  print(result)
  tracking_id = load_tracking_id_to_search(current_user.id)
  return_data = load_current_return_to_display_from_db(current_user.id)
  quantity_of_return = return_data['return_quantity']
  sku = return_data['sku']
  queue = load_queue_from_db(current_user.id) 
  
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
  add_tracking_id_to_queue(tracking_id, sku, quantity_of_return, current_user.id)
  return redirect('/')

@views.route('/search', methods=['POST','GET'])
@login_required
def search():
  delete_tracking_id_to_search(current_user.id)
  delete_current_return_to_display_from_db(current_user.id)
  tracking_id = request.form
  add_tracking_id_to_search(tracking_id)
#add_current_return_to_display_to_db(tracking_id)
  return redirect('/')
@views.route('/clearSearch')
@login_required
def clearSearch():
  delete_tracking_id_to_search(current_user.id)
  delete_current_return_to_display_from_db(current_user.id)
  return redirect('/')
@views.route('/clearQueue')
@login_required
def clearQueue():
  delete_whole_tracking_id_queue(current_user.id)
  return redirect('/')


@views.route('/account')
@login_required
def account():
  stripe.billing_portal.Configuration.create(
  business_profile={
    "headline": "J&D Group partners with Stripe for simplified billing.",
  },
  features={"invoice_history": {"enabled": True}},
  metadata={'user_id': current_user.id}
)
  
  customer = Stripecustomer.query.filter_by(user_id=current_user.id).order_by(Stripecustomer.id.desc()).first() 
  if customer:
        subscription = stripe.Subscription.retrieve(customer.stripeSubscriptionId)
        product = stripe.Product.retrieve(subscription.plan.product)
        context = {
            "subscription": subscription,
            "product": product,
        }
    
  refresh_token = get_refresh_token(current_user.id)
  if (refresh_token and customer):
    return render_template('account.html', user=current_user, refresh_token=refresh_token, **context)
  elif customer:
    return render_template('account.html', user=current_user, **context)
  elif refresh_token:
    return render_template('account.html', user=current_user, refresh_token=refresh_token)

        
  return render_template('account.html', user=current_user)


@views.route('/admin')
@login_required
def admin():
  if(current_user.email=='admin@admin675463.com'): 
    users = load_users_from_db()
    deleted_users = load_deleted_users_from_db()
  
    return render_template('admin.html', users=users,  user=current_user, deleted_users = deleted_users)
  else:
    flash('Access Denied.', category='error')
    return redirect(url_for('views.home'))

@views.route('/request_delete_user/<user>')
@login_required
def request_delete_user(user):
  add_request_to_delete_user(user)
  flash('Request to Delete Account Sent.', category='success')
  return redirect('/account')

    
@views.route('/delete_user/<user>')
@login_required
def delete_user(user):
  if(current_user.email=='admin@admin675463.com'): 
    delete_user_from_db(user, current_user.id)
    return redirect('/admin')
  else:
    flash('Access Denied.', category='error')
    return redirect(url_for('views.home'))

@views.route('/delete_deleted_user/<deleted_user>')
@login_required
def delete_deleted_user(deleted_user):
  if(current_user.email=='admin@admin675463.com'): 
    delete_deleted_user_from_db(deleted_user, current_user.id)
    return redirect('/admin')
  else:
    flash('Access Denied.', category='error')
    return redirect(url_for('views.home'))
@views.route('/clear_all_users')
@login_required
def clear_users():
  if(current_user.email=='admin@admin675463.com'): 
    clear_all_users_from_db(current_user.id)
    return redirect('/admin')
  else:
    flash('Access Denied.', category='error')
    return redirect(url_for('views.home'))
@views.route('/clear_all_deleted_users')
@login_required
def clear_deleted_users():
  if(current_user.email=='admin@admin675463.com'): 
    clear_all_deleted_users_from_db(current_user.id)
    return redirect('/admin')
  else:
    flash('Access Denied.', category='error')
    return redirect(url_for('views.home'))



@views.route('/download-queue-pdf')
def download_queue():
    response = download_queue_data(current_user.id)
    # buffer = BytesIO()
    # with open('website/static/files/queue.pdf', 'rb') as f:
    #     buffer.write(f.read())
    # buffer.seek(0)
    # os.remove('website/static/files/queue.pdf')
    # response = make_response(buffer.getvalue())
  
      # Set the appropriate headers for a PDF file download
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=queue.pdf'
  
    return response


@views.route('/download-inventoryUpdate-pdf')
def download_queue_and_inventory_change():
    response = download_queue_and_inventory_change_data(current_user.id, current_user.refresh_token)
    # buffer = BytesIO()
    # with open('website/static/files/InventoryUpdate.pdf', 'rb') as f:
    #     buffer.write(f.read())
    # buffer.seek(0)
    # os.remove('website/static/files/InventoryUpdate.pdf')
    # response = make_response(buffer.getvalue())
  
      # Set the appropriate headers for a PDF file download
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=InventoryUpdate.pdf'
  
    return response
  
  #   return send_file(buffer, mimetype='application/pdf', as_attachment=True,
  # attachment_filename='queue.pdf'
  #           )

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)