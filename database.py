from sqlalchemy import create_engine, text
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca":"/etc/ssl/cert.pem"
    } 
  })




def load_queue_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from tracking_ids"))
    queue=[]
    
    for row in result.all():
      queue.append(dict(row._asdict()))   #dict(row)
    #print(queue)
    return queue

def delete_trackingID_from_queue_db(trackingID):
  with engine.connect() as conn:
    query = text("DELETE FROM tracking_ids WHERE tracking_ids.tracking = :tracking_id")

    #conn.execute(query, tracking_id=trackingID)
    conn.execute(query, {"tracking_id": trackingID})
    

def add_tracking_id_to_queue(trackingID):
  with engine.connect() as conn:
    query = text("INSERT INTO tracking_ids (tracking) VALUES (:tracking_id)")

    #conn.execute(query, tracking_id=trackingID)
    conn.execute(query, {"tracking_id": trackingID})
 
def load_returnDetails_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from all_return_details"))
    return_details=[]
    for row in result.all():
      return_details.append(dict(row))
    return return_details

def load_tracking_id_to_search():
  with engine.connect() as conn:
    result = conn.execute(text("select * from tracking_id_to_search"))
    trackingID=[]
    for row in result.all():
      trackingID.append(dict(row))
    return trackingID

def refresh_all_return_data_in_db(all_return_data):
  with engine.connect() as conn:
    #Delete all previous return data
    conn.execute(text("DELETE FROM all_return_details"))

    #Add all the new return data
    #query = 
    
    conn.execute(query)