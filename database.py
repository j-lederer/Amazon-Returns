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
      queue.append(dict(row._asdict()))   #dict(row) It is a LegacyRow
    #print(queue)
    return queue
def delete_trackingID_from_queue_db(trackingID):
  with engine.connect() as conn:
    query = text("DELETE FROM tracking_ids WHERE tracking_ids.tracking = :tracking_id")

    #conn.execute(query, tracking_id=trackingID)
    conn.execute(query, {"tracking_id": trackingID})  
def delete_whole_tracking_id_queue():
   with engine.connect() as conn:
    conn.execute(text("DELETE FROM tracking_ids"))
def add_tracking_id_to_queue(trackingID):
  with engine.connect() as conn:
    query = text("INSERT INTO tracking_ids (tracking) VALUES (:tracking_id)")
    #conn.execute(query, tracking_id=trackingID)
    conn.execute(query, {"tracking_id": trackingID})
 
def load_all_return_details_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from all_return_details"))
    return_details=[]
    column_names = result.keys()
        
    for row in result:
            row_dict = dict(zip(column_names, row))
            return_details.append(row_dict)
    #print(return_details)  
    return return_details
    
def delete_current_return_to_display_from_db():
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM current_return_to_display"))
def add_current_return_to_display_to_db(trackingID):
   delete_current_return_to_display_from_db()
   with engine.connect() as conn:
    result = conn.execute(text("select * from all_return_details"))
    returnDatas = []
    column_names = result.keys()    
    for row in result:
            row_dict = dict(zip(column_names, row))
            if row_dict['tracking_id'] == trackingID:
              returnDatas.append(row_dict)
              for returnData in returnDatas:
                
                query = text("INSERT INTO current_return_to_display (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned)")
                conn.execute(query, {"tracking_id": returnData['tracking_id'], "item_name":returnData['item_name'], "sku":returnData['sku'], "return_quantity":returnData['return_quantity'], "refund_amount":returnData['refund_amount'], "order_id":returnData['order_id'], "order_quantity":returnData['order_quantity'], "asin":returnData['asin'], "reason_returned":returnData['reason_returned']  })
    if(load_current_return_to_display_from_db()==None):
      query = text("INSERT INTO current_return_to_display (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned)")
      conn.execute(query, {"tracking_id": "Not Found", "item_name":"Not Found", "sku":"Not Found", "return_quantity":"Not Found", "refund_amount":"Not Found", "order_id":"Not Found", "order_quantity":"Not Found", "asin":"Not Found", "reason_returned":"Not Found"  })
              
def load_current_return_to_display_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from current_return_to_display"))
    
    column_names = result.keys()
        
    for row in result:
            row_dict = dict(zip(column_names, row))
            return row_dict
    
   
  

def delete_tracking_id_to_search():
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM tracking_id_to_search"))
def add_tracking_id_to_search(trackingID):
  delete_tracking_id_to_search()
  with engine.connect() as conn:
    query = text("INSERT INTO tracking_id_to_search (trackingID) VALUES (:trackingID)")
    conn.execute(query, {"trackingID": trackingID})
def load_tracking_id_to_search():
  with engine.connect() as conn:
    result = conn.execute(text("select * from tracking_id_to_search"))
    for row in result.all():
      trackingID = row._asdict()
      return trackingID['trackingID']

  
def refresh_all_return_data_in_db(all_return_data):
  with engine.connect() as conn:
    #Delete all previous return data
    conn.execute(text("DELETE FROM all_return_details"))

    #Add all the new return data
    for return_details in all_return_data:
      print(return_details)
      query = text("INSERT INTO all_return_details (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned)")
      conn.execute(query, {"tracking_id": return_details['tracking_id'], "item_name":return_details['item_name'], "sku":return_details['sku'], "return_quantity":return_details['return_quantity'], "refund_amount":return_details['refund_amount'], "order_id":return_details['order_id'], "order_quantity":return_details['order_quantity'], "asin":return_details['asin'], "reason_returned":return_details['reason_returned']  })
    
    