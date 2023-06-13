from flask import Flask, render_template, request, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from database import engine, load_queue_from_db, load_all_return_details_from_db, load_tracking_id_to_search, delete_trackingID_from_queue_db, add_tracking_id_to_queue, refresh_all_return_data_in_db, load_current_return_to_display_from_db, add_current_return_to_display_to_db, delete_whole_tracking_id_queue, delete_current_return_to_display_from_db, delete_tracking_id_to_search, add_tracking_id_to_search

from amazonAPI import get_all_Returns_data

app = Flask(__name__)






@app.route('/', methods=['POST', 'GET'])
def index(): 
  #returnDetails = load_returnDetails_from_db()
  All_Return_Details = load_all_return_details_from_db()
  tracking_id=None
  return_details_to_display=None
  
  if load_tracking_id_to_search():
    tracking_id = load_tracking_id_to_search()
    add_current_return_to_display_to_db(tracking_id)
  return_details_to_display = load_current_return_to_display_from_db()
  queue = load_queue_from_db()
  if (return_details_to_display and tracking_id):  #if they exist
    print(return_details_to_display)
    return render_template('home.html', tasks=queue, passed_value = return_details_to_display, tracking_id=tracking_id)
        

  else: 
      return render_template('home.html', tasks=queue)
      
@app.route('/refresh_returns_and_inventory')
def refresh():
    #Get all the new return data with a call from amazonAPI.py
    #print(get_all_Returns_data())
    all_return_data = get_all_Returns_data()
    print(all_return_data)
  
    refresh_all_return_data_in_db(all_return_data)
    try:
        #remove the previous return details from db
        #and add the new return details to db
        return redirect('/')
    except:
        return 'There was a problem refreshing your returns'

@app.route('/result', methods =['POST', 'GET'])
def result():
    tracking_id = request.form
    #output = request.form.to_dict()
    #tracking_id=output["track"]
    output_data = run_script_getReturns(tracking_id)
    return render_template('home.html', passed_value=output_data, tracking_id=tracking_id)
    #return render_template('result.html', output_data=output_data)

@app.route('/info_for_tracking_id', methods =[ 'POST', 'GET'])
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

@app.route('/increase_inventory', methods =['POST', 'GET'])
def increase_inventory():
  #take the tracking id's in the queue and increase inventory by the return order amount for each
   return redirect('/')

@app.route('/delete/<tracking>')
def delete(tracking):
    delete_trackingID_from_queue_db(tracking)
    return redirect('/')
  
    try:
        delete_trackingID_from_queue_db(tracking)
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/add_trackingID', methods=['POST', 'GET'])
def add_tracking_id():
    tracking_id = request.form
    add_tracking_id_to_queue(tracking_id['added_track'])
    return redirect('/')
    
    try:
      add_tracking_id_to_queue(tracking_id['added_track'])
      return redirect('/')

    except:
      return 'There was a problem adding the Tracking ID to your queue'
@app.route('/add_to_queue_button')
def add_to_queue():
  tracking_id = load_tracking_id_to_search()
  add_tracking_id_to_queue(tracking_id)
  return redirect('/')

@app.route('/search', methods=['POST','GET'])
def search():
  delete_tracking_id_to_search()
  delete_current_return_to_display_from_db()
  tracking_id = request.form
  add_tracking_id_to_search(tracking_id)
  #add_current_return_to_display_to_db(tracking_id)
  return redirect('/')
@app.route('/clearSearch')
def clearSearch():
  delete_tracking_id_to_search()
  delete_current_return_to_display_from_db()
  return redirect('/')
@app.route('/clearQueue')
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