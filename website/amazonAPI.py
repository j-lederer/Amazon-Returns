from sp_api.api import Orders
from sp_api.base import SellingApiException
import os
#from dotenv import load_dotenv
#del os.environ['AWS_ENV']
import time
import xml.etree.ElementTree as ET
import csv
from io import StringIO
from sp_api.api import Feeds



from datetime import datetime, timedelta, date
from sp_api.base import Marketplaces
from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
import os

from .database import load_queue_from_db, delete_whole_tracking_id_queue




# credentials = dict(
#     refresh_token=os.environ['REFRESH_TOKEN'],
#     lwa_app_id=os.environ['LWA_APP_ID'],
#     lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
#     aws_access_key=os.environ['AWS_ACCESS_KEY'],
#     aws_secret_key=os.environ['AWS_SECRET_KEY'],  
#     #role_arn="arn:aws:iam::108760843519:role/New_Role"
# )



from sp_api.api import Reports
from sp_api.api import Feeds
from sp_api.base.reportTypes import ReportType




def get_all_Returns_data(refresh_token):
        credentials = dict(
          refresh_token=refresh_token,
          lwa_app_id=os.environ['LWA_APP_ID'],
          lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
          aws_access_key=os.environ['AWS_ACCESS_KEY'],
          aws_secret_key=os.environ['AWS_SECRET_KEY'],  
          #role_arn="arn:aws:iam::108760843519:role/New_Role"
      )
        import xml.etree.ElementTree as ET
        #report_types = ["GET_FLAT_FILE_OPEN_LISTINGS_DATA",]
        res = Reports(credentials=credentials).create_report(
            reportType="GET_XML_RETURNS_DATA_BY_RETURN_DATE",
            dataStartTime=(datetime.utcnow() - timedelta(days=50)).isoformat(),
            #**Looks like get an error (FATAL) if startTime is before account was opened or if bad example. I got error with year 2019
            #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
            marketplaceIds=[
                "ATVPDKIKX0DER",   #US
                
            ])
        #print(res)
        #print(res.payload)
        res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
        #print(res.payload)
        report_id = res.payload.get("reportId")
        #print(res)
        #print(report_id)
        processing_status = res.payload.get("processingStatus")
        while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
                    # Wait for a short duration before checking again
                    time.sleep(2)
                    
                    # Get the updated report status
                    response = Reports(credentials=credentials).get_report(report_id)
                    processing_status = response.payload.get("processingStatus")
                    print(processing_status)
        if processing_status == "DONE":
                    # Once the processing is done, retrieve the report document
                    document_id = response.payload.get("reportDocumentId")
                    #print(response)
                    #print(document_id)
                    response = Reports(credentials=credentials).get_report_document(document_id, download=True)
                    print(response.payload.get("document"))
                    #print(response.content)
                    myroot =ET.fromstring(response.payload.get("document")) #If response is a string
                    print(myroot.tag)
                    Returns_info = []
                    for x in myroot.iter("return_details"): #can also use myroot.findall("")
                        new_return={}
                        for y in x.iter("label_details"):
                            for z in y.iter("tracking_id"):
                                  print(z.text)
                                #if z.text = trackingID_Scanned then get the 
                                # 1. Reason for return
                                # 2. Quantity returned
                                # 3. SKU and increase inventory
                                #Ex tracking id: "1Z0V2Y989048009061
                                  tracking_id = z.text 
                                  print("Details for return order:")
                                  print(x.find("item_details").find("return_reason_code").text)
                                  reason_returned = x.find("item_details").find("return_reason_code").text
                                  print(x.find("item_details").find("item_name").text)
                                  item_name = x.find("item_details").find("item_name").text 
                                  print(x.find("item_details").find("merchant_sku").text)
                                  sku = x.find("item_details").find("merchant_sku").text
                                  print(x.find("item_details").find("return_quantity").text)
                                  return_quantity = x.find("item_details").find("return_quantity").text
                                  print(x.find("item_details").find("refund_amount").text)
                                  refund_amount = x.find("item_details").find("refund_amount").text
                                  print(x.find("order_id").text)
                                  order_id = x.find("order_id").text
                                  print(x.find("order_date").text)
                                  print(x.find("a_to_z_claim").text)
                                  print(x.find("order_quantity").text)
                                  order_quantity = x.find("order_quantity").text
                                  asin = x.find("item_details").find("asin").text
                                  new_return['tracking_id']= tracking_id
                                  new_return['item_name'] = item_name
                                  new_return['sku'] = sku
                                  new_return['return_quantity'] = return_quantity
                                  new_return['refund_amount'] = refund_amount
                                  new_return['order_id'] = order_id
                                  new_return['order_quantity'] = order_quantity
                                  new_return['asin'] = asin
                                  new_return['Inventory'] = "No Data"
                                  new_return['reason_returned'] = reason_returned

                                  Returns_info.append(new_return)
                                  
          
                    print(Returns_info)
                    output_data = Returns_info                
                        
        elif processing_status == "CANCELLED":
            print("Report processing was cancelled.")
            output_data= "CANCELLED"
        elif processing_status == "FATAL":
            print("An error occurred during report processing. (FATAL)")  
            output_data= "FATAL"
        
        return output_data



def checkInventory(refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)

#To get Report of Inventories
  print("Inventory Report:")
  Quantity_of_SKUS = {}
  res = Reports(credentials=credentials).create_report(

    reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA",
  #dataStartTime=(datetime.utcnow() - timedelta(days=7)).isoformat(),
  #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
  #marketplaceIds=["ATVPDKIKX0DER",   #US]
  )
  res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
  report_id = res.payload.get("reportId")

  processing_status = res.payload.get("processingStatus")
  while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
    # Wait for a short duration before checking again
    time.sleep(2)
                    
    # Get the updated report status
    response = Reports(credentials=credentials).get_report(report_id)
    processing_status = response.payload.get("processingStatus")
    print(processing_status)
    if processing_status == "DONE":
      # Once the processing is done, retrieve the report document
      document_id = response.payload.get("reportDocumentId")
      response = Reports(credentials=credentials).get_report_document(document_id, download=True)
    # print(response.payload.get("document"))
      s = response.payload.get("document")
      buff = StringIO(s)
      inventory_reader = csv.DictReader(buff, delimiter='\t' )
      #csv.reader                                    #next(inventory_reader) #skips the header
      for line in inventory_reader:
        #print("test")
        print(line['sku'], line['asin'], line['price'], line['quantity'])
        Quantity_of_SKUS[line['sku']]=line['quantity']
      print("Quantity left of skus is:")
      print(Quantity_of_SKUS)    
      return Quantity_of_SKUS

def increaseInventory(Quantity_of_SKUS, user_id, refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  #submitting feed to increase inventory   
  from io import BytesIO
  from sp_api.api import Feeds
  #from sp_api.auth import VendorCredentials
  import xml.etree.ElementTree as ET

  queue = load_queue_from_db(user_id)
  queue_to_increase= {}
  is_duplicate = False
  for track in queue:
      for sku in queue_to_increase.keys():
        if sku == track['SKU']:
          is_duplicate = True
      if is_duplicate:
        queue_to_increase[track['SKU']] = queue_to_increase[track['SKU']] + track['return_quantity']        
      else:
        queue_to_increase[track['SKU']]=track['return_quantity']
  print (queue_to_increase)
        #return queue_to_increase
  for sku in queue_to_increase.keys():
    # Initialize the Feeds API client
    feeds = Feeds(credentials=credentials)
    # Define the inventory update feed message
    message = {
            "MessageType": "Inventory",
            "MessageID": "1",
            "Inventory": {
                "SKU": sku,
                "Quantity": (int(Quantity_of_SKUS[sku])+int(queue_to_increase[sku])),
                "FulfillmentCenterID": "DEFAULT"
            },
            "Override": "false"
        }

    # Create the XML structure
    root = ET.Element("AmazonEnvelope")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
    header = ET.SubElement(root, "Header")
    document_version = ET.SubElement(header, "DocumentVersion")
    document_version.text = "1.02"
    merchant_identifier = ET.SubElement(header, "MerchantIdentifier")
    merchant_identifier.text = "A2RSMNCJSAU6P5"

    message_type = ET.SubElement(root, "MessageType")
    message_type.text = message["MessageType"]

    message_element = ET.SubElement(root, "Message")
    message_id = ET.SubElement(message_element, "MessageID")
    message_id.text = message["MessageID"]

    inventory = ET.SubElement(message_element, "Inventory")
    inventory_data = message["Inventory"]
    seller_sku = ET.SubElement(inventory, "SKU")
    seller_sku.text = inventory_data["SKU"]
    fulfillment_center_id = ET.SubElement(inventory, "FulfillmentCenterID")
    fulfillment_center_id.text = inventory_data["FulfillmentCenterID"]

    # Choice between Available, Quantity, or Lookup
    quantity = ET.SubElement(inventory, "Quantity")
    quantity.text = str(inventory_data["Quantity"])

    restock_date = ET.SubElement(inventory, "RestockDate")
    restock_date.text = "2023-05-26"  # Replace with a valid date
    fulfillment_latency = ET.SubElement(inventory, "FulfillmentLatency")
    fulfillment_latency.text = "1"  # Replace with a valid integer
    switch_fulfillment_to = ET.SubElement(inventory, "SwitchFulfillmentTo")   #I think can leave this and following line out
    switch_fulfillment_to.text = "MFN"  # Replace with either "MFN" or "AFN  

    # Convert the XML structure to a string
    xml_string = ET.tostring(root, encoding="utf-8", method="xml")

    # Submit the feed
    feeds = Feeds(credentials=credentials)
    feed = BytesIO(xml_string)
    feed.seek(0)


    # Submit the feed
    try:
      document_response, create_feed_response= feeds.submit_feed('POST_INVENTORY_AVAILABILITY_DATA', feed, 'text/xml')
      #print("RETURNED DOCUMENT RESOPONSE")
      #print(document_response)
      #print ("RETURNED CREATE FEED RESPONSE")
      #print(create_feed_response)
      response = create_feed_response
      print("Feed submitted...")

      #Check the processing status
      #print(response)
      feed_id = response.payload.get('feedId')   
      #print (feed_id)
        
      print("Inventory Feed Processing Status")
      while True:
          feed_response = feeds.get_feed(feed_id)
          #print(feed_response)
          processing_status = feed_response.payload.get('processingStatus')
          print(processing_status) 
          if processing_status in ["DONE", "IN_QUEUE", "IN_PROGRESS"]:
              #print(f"Processing status: {processing_status}")
              if processing_status in ["DONE", "DONE_NO_DATA"]:
                  print(feed_response)
                  print("Feed processing completed.")
                  document_id = feed_response.payload.get("resultFeedDocumentId")
                  feed_response = Feeds(credentials=credentials).get_feed_document(document_id) #download=true
                  print(feed_response)
                  break
  
          else:
              print("Feed processing encountered a fatal error.")
              break
          time.sleep(5)

    except Exception as e:
        print(f"Error submitting feed: {e}") 
      
  delete_whole_tracking_id_queue(user_id)
  return "Inventory Feeds submitted successfully", queue_to_increase
    

def produce_pdf(user_id, refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  Quantity_of_SKUS = checkInventory(refresh_token)
  
  queue = load_queue_from_db(user_id)
  queue_to_increase= {}
  is_duplicate = False
  for track in queue:
      for sku in queue_to_increase.keys():
        if sku == track['SKU']:
          is_duplicate = True
      if is_duplicate:
        queue_to_increase[track['SKU']] = queue_to_increase[track['SKU']] + track['return_quantity']        
      else:
        queue_to_increase[track['SKU']]=track['return_quantity']

  final_inventory={}
  for sku in queue_to_increase.keys():
    final_inventory[sku] =(int( Quantity_of_SKUS[sku]) + int( queue_to_increase[sku]) )

  return Quantity_of_SKUS, queue_to_increase, final_inventory
    
  
        
  
def checkInventoryIncrease(Initial_quantity_of_skus, skus_and_increases, refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  #Test to see if inventory update   

  
  
  
  while True:
    # print(skus_and_increases)
    counter = int(0)
    Updated_Inventory_Reading = checkInventory(refresh_token)
    if(skus_and_increases):
      for sku in skus_and_increases.keys():
        Quantity_of_SKU = skus_and_increases[sku] 
  
        print("Quantity left of sku")
        print(sku)
        print("is")
        print(skus_and_increases[sku])
        
        Initial_quantity_of_sku= Initial_quantity_of_skus[sku]
        print(Updated_Inventory_Reading[sku])
        print(int(Initial_quantity_of_sku) + int(skus_and_increases[sku]))
        print(counter)
        print(len(skus_and_increases))
        if (int(Updated_Inventory_Reading[sku]) == (int(Initial_quantity_of_sku) + int(skus_and_increases[sku]))): 
          counter+=1
          if counter == len(skus_and_increases):
            print('breaking')
            return "Inventory Increased Successfully"
    
      time.sleep(60)
    else:
      return ("No returns in queue detected")
  return "Inventory Increase Not Detected" 



def get_addresses_from_GetOrders(refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  res = Orders(credentials=credentials, marketplace=Marketplaces.US)
  result = res.get_orders(CreatedAfter='2021-05-20', CreatedBefore=date.today().isoformat()).payload
  #print(result)
  orders = result["Orders"]
  orders_Info = {}

  #print(orders)
  for order in orders:
    #print("PRINTING ORDER: ")
    #print(order)
    orderID = order["AmazonOrderId"]
    address = None
    for key in order.keys():
      if key=="ShippingAddress":
        address = order["ShippingAddress"]
    #print("PRINTING ORDERid AND ADDRESS:" )
    #print(orderID)
    #print(address)
    orders_Info[orderID] = address
    
  return orders_Info





























def run_script_getReturns(tracking_id, refresh_token):
        credentials = dict(
          refresh_token=refresh_token,
          lwa_app_id=os.environ['LWA_APP_ID'],
          lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
          aws_access_key=os.environ['AWS_ACCESS_KEY'],
          aws_secret_key=os.environ['AWS_SECRET_KEY'],  
          #role_arn="arn:aws:iam::108760843519:role/New_Role"
      )
        import xml.etree.ElementTree as ET
        print("running method for tracking_id : ")
        print(tracking_id)
        # Modify this function to include your script logic
        # You can use the tracking_id variable in your script
        #output_data = "Output data for tracking ID: " + tracking_id
        

        #report_types = ["GET_FLAT_FILE_OPEN_LISTINGS_DATA",]
        res = Reports(credentials=credentials).create_report(
            reportType="GET_XML_RETURNS_DATA_BY_RETURN_DATE",
            dataStartTime=(datetime.utcnow() - timedelta(days=40)).isoformat(),
            #**Looks like get an error (FATAL) if startTime is before account was opened or if bad example. I got error with year 2019
            #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
            marketplaceIds=[
                "ATVPDKIKX0DER",   #US
                
            ])
        #print(res)
        #print(res.payload)
        res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
        #print(res.payload)
        report_id = res.payload.get("reportId")
        #print(res)
        #print(report_id)
        processing_status = res.payload.get("processingStatus")
        while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
                    # Wait for a short duration before checking again
                    time.sleep(2)
                    
                    # Get the updated report status
                    response = Reports(credentials=credentials).get_report(report_id)
                    processing_status = response.payload.get("processingStatus")
                    print(processing_status)
        if processing_status == "DONE":
                    # Once the processing is done, retrieve the report document
                    document_id = response.payload.get("reportDocumentId")
                    #print(response)
                    #print(document_id)
                    response = Reports(credentials=credentials).get_report_document(document_id, download=True)
                    print(response.payload.get("document"))
                    #print(response.content)
                    myroot =ET.fromstring(response.payload.get("document")) #If response is a string
                    print(myroot.tag)
                    tracking_id_found = False
                    for x in myroot.iter("return_details"):   #can also use myroot.findall("")
                        for y in x.iter("label_details"):
                            for z in y.iter("tracking_id"):
                                print(z.text)
                                #if z.text = trackingID_Scanned then get the 
                                # 1. Reason for return
                                # 2. Quantity returned
                                # 3. SKU and increase inventory
                                #Ex tracking id: "1Z0V2Y989048009061"
                                if z.text == tracking_id:
                                    tracking_id_found = True
                                    print("Details for return order:")
                                    print(x.find("item_details").find("return_reason_code").text)
                                    reason_returned = x.find("item_details").find("return_reason_code").text
                                    output_data=reason_returned
                                    print(x.find("item_details").find("item_name").text)
                                    item_name = x.find("item_details").find("item_name").text 
                                    print(x.find("item_details").find("merchant_sku").text)
                                    sku = x.find("item_details").find("merchant_sku").text
                                    print(x.find("item_details").find("return_quantity").text)
                                    return_quantity = x.find("item_details").find("return_quantity").text
                                    print(x.find("item_details").find("refund_amount").text)
                                    refund_amount = x.find("item_details").find("refund_amount").text
                                    print(x.find("order_id").text)
                                    order_id = x.find("order_id").text
                                    print(x.find("order_date").text)
                                    print(x.find("a_to_z_claim").text)
                                    print(x.find("order_quantity").text)
                                    order_quantity = x.find("order_quantity").text
                                    asin = x.find("item_details").find("asin").text
                                   

                                    Quantity_of_SKU = -1
                                    #To get Report of Inventories
                                    print("Inventory Report:")
                                    res = Reports(credentials=credentials).create_report(
                                    reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA",
                                    # dataStartTime=(datetime.utcnow() - timedelta(days=7)).isoformat(),
                                    #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
                                    #marketplaceIds=["ATVPDKIKX0DER",   #US]
                                    )
                                    res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
                                    report_id = res.payload.get("reportId")

                                    processing_status = res.payload.get("processingStatus")
                                    while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
                                        # Wait for a short duration before checking again
                                        time.sleep(2)
                    
                                        # Get the updated report status
                                        response = Reports(credentials=credentials).get_report(report_id)
                                        processing_status = response.payload.get("processingStatus")
                                        print(processing_status)
                                    if processing_status == "DONE":
                                        # Once the processing is done, retrieve the report document
                                        document_id = response.payload.get("reportDocumentId")
                                        response = Reports(credentials=credentials).get_report_document(document_id, download=True)
                                    # print(response.payload.get("document"))

                                        s = response.payload.get("document")
                                        buff = StringIO(s)
                                        inventory_reader = csv.DictReader(buff, delimiter='\t' )
                                        #csv.reader
                                        
                                        #next(inventory_reader) #skips the header
                                        for line in inventory_reader:
                                    
                                            #print("test")
                                            print(line['sku'], line['asin'], line['price'], line['quantity'])
                                            if line['sku'] == sku:                 #line[0]
                                                Quantity_of_SKU = line['quantity']    #line[3]

                                        print("Qunatity left of sku")
                                        print(sku)
                                        print("is")
                                        print(Quantity_of_SKU)        
                    if(tracking_id_found == False):
                         print("Tracking id not found")   
                    Info = dict({'reasonReturned': reason_returned, 'merchantSKU': sku, 'returnQuantity': return_quantity, 'refundAmount': refund_amount, 'orderID': order_id, 'itemsBought':order_quantity, 'inventory': Quantity_of_SKU, 'itemName': item_name, 'ASIN':asin })
                    output_data = Info
                        
        elif processing_status == "CANCELLED":
            print("Report processing was cancelled.")
            output_data= "CANCELLED"
        elif processing_status == "FATAL":
            print("An error occurred during report processing. (FATAL)")  
            output_data= "FATAL"
        
        return output_data

def get_all_inventory_data(refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_APP_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  Quantity_of_SKU = -1
  #To get Report of Inventories
  print("Inventory Report:")
  res = Reports(credentials=credentials).create_report(
      reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA",
      # dataStartTime=(datetime.utcnow() - timedelta(days=7)).isoformat(),
      #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
      #marketplaceIds=["ATVPDKIKX0DER",   #US]
      )
  res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
  report_id = res.payload.get("reportId")
  processing_status = res.payload.get("processingStatus")
  while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
    # Wait for a short duration before checking again
    time.sleep(2)
                    
  # Get the updated report status
  response = Reports(credentials=credentials).get_report(report_id)
  processing_status = response.payload.get("processingStatus")
  print(processing_status)
  if processing_status == "DONE":
    # Once the processing is done, retrieve the report document
    document_id = response.payload.get("reportDocumentId")
    response = Reports(credentials=credentials).get_report_document(document_id, download=True)
    # print(response.payload.get("document"))

    s = response.payload.get("document")
    buff = StringIO(s)
    inventory_reader = csv.DictReader(buff, delimiter='\t' )
    #csv.reader
                                        
    #next(inventory_reader) #skips the header
    Inventory_info = []
    for line in inventory_reader:                     
      #print("test")
      print(line['sku'], line['asin'], line['price'], line['quantity'])
      #add data to Inventory_info
                             
    return Inventory_info            
def run_script_increaseInventory(sku_value, refresh_token):
        credentials = dict(
          refresh_token=refresh_token,
          lwa_app_id=os.environ['LWA_APP_ID'],
          lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
          aws_access_key=os.environ['AWS_ACCESS_KEY'],
          aws_secret_key=os.environ['AWS_SECRET_KEY'],  
          #role_arn="arn:aws:iam::108760843519:role/New_Role"
      )
        #submitting feed to increase inventory   
        from io import BytesIO
        from sp_api.api import Feeds
        #from sp_api.auth import VendorCredentials
        import xml.etree.ElementTree as ET




        # Initialize the Feeds API client
        feeds = Feeds(credentials=credentials)

        # Define the inventory update feed message
        message = {
            "MessageType": "Inventory",
            "MessageID": "1",
            "Inventory": {
                "SKU": sku,
                "Quantity": (int(Quantity_of_SKU)+int(return_quantity)),
                "FulfillmentCenterID": "DEFAULT"
            },
            "Override": "false"
        }

        # Create the XML structure
        root = ET.Element("AmazonEnvelope")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")

        header = ET.SubElement(root, "Header")
        document_version = ET.SubElement(header, "DocumentVersion")
        document_version.text = "1.02"
        merchant_identifier = ET.SubElement(header, "MerchantIdentifier")
        merchant_identifier.text = "A2RSMNCJSAU6P5"

        message_type = ET.SubElement(root, "MessageType")
        message_type.text = message["MessageType"]

        message_element = ET.SubElement(root, "Message")
        message_id = ET.SubElement(message_element, "MessageID")
        message_id.text = message["MessageID"]

        inventory = ET.SubElement(message_element, "Inventory")
        inventory_data = message["Inventory"]
        seller_sku = ET.SubElement(inventory, "SKU")
        seller_sku.text = inventory_data["SKU"]
        fulfillment_center_id = ET.SubElement(inventory, "FulfillmentCenterID")
        fulfillment_center_id.text = inventory_data["FulfillmentCenterID"]

        # Choice between Available, Quantity, or Lookup
        quantity = ET.SubElement(inventory, "Quantity")
        quantity.text = str(inventory_data["Quantity"])

        restock_date = ET.SubElement(inventory, "RestockDate")
        restock_date.text = "2023-05-26"  # Replace with a valid date
        fulfillment_latency = ET.SubElement(inventory, "FulfillmentLatency")
        fulfillment_latency.text = "1"  # Replace with a valid integer
        switch_fulfillment_to = ET.SubElement(inventory, "SwitchFulfillmentTo")   #I think can leave this and following line out
        switch_fulfillment_to.text = "MFN"  # Replace with either "MFN" or "AFN  

        # Convert the XML structure to a string
        xml_string = ET.tostring(root, encoding="utf-8", method="xml")

         # Submit the feed
        feeds = Feeds(credentials=credentials)
        feed = BytesIO(xml_string)
        feed.seek(0)


        # Submit the feed
        try:
            document_response, create_feed_response= feeds.submit_feed('POST_INVENTORY_AVAILABILITY_DATA', feed, 'text/xml')
            #print("RETURNED DOCUMENT RESOPONSE")
            #print(document_response)
            #print ("RETURNED CREATE FEED RESPONSE")
            #print(create_feed_response)
            response = create_feed_response
            print("Feed submitted...")

            #Check the processing status
            #print(response)
            feed_id = response.payload.get('feedId')   
            #print (feed_id)
        
            print("Inventory Feed Processing Status")
            while True:
                feed_response = feeds.get_feed(feed_id)
                #print(feed_response)
                processing_status = feed_response.payload.get('processingStatus')
                print(processing_status) 
                if processing_status in ["DONE", "IN_QUEUE", "IN_PROGRESS"]:
                    #print(f"Processing status: {processing_status}")
                    if processing_status in ["DONE", "DONE_NO_DATA"]:
                        print(feed_response)
                        print("Feed processing completed.")
                        document_id = feed_response.payload.get("resultFeedDocumentId")
                        feed_response = Feeds(credentials=credentials).get_feed_document(document_id) #download=true
                        print(feed_response)
                        break
                    time.sleep(5)  # Wait for 30 seconds before checking again
                else:
                    print("Feed processing encountered a fatal error.")
                    break
        except Exception as e:
            print(f"Error submitting feed: {e}") 

        return  "Inventory Feed submitted successfully"
def run_script_checkInventoryIncrease(Quantity_of_SKU, return_quantity, refresh_token):
        credentials = dict(
          refresh_token=refresh_token,
          lwa_app_id=os.environ['LWA_APP_ID'],
          lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
          aws_access_key=os.environ['AWS_ACCESS_KEY'],
          aws_secret_key=os.environ['AWS_SECRET_KEY'],  
          #role_arn="arn:aws:iam::108760843519:role/New_Role"
      )
     #Test to see if inventory update
        Initial_quantity_of_sku = Quantity_of_SKU
        Initail_return_quantity = return_quantity    
        while True:
                                print("Inventory Report:")
                                res = Reports(credentials=credentials).create_report(
                                reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA",
                                # dataStartTime=(datetime.utcnow() - timedelta(days=7)).isoformat(),
                                #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
                                #marketplaceIds=["ATVPDKIKX0DER",   #US]
                                )
                                res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
                                report_id = res.payload.get("reportId")

                                processing_status = res.payload.get("processingStatus")
                                while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
                                    # Wait for a short duration before checking again
                                    time.sleep(2)
                
                                    # Get the updated report status
                                    response = Reports(credentials=credentials).get_report(report_id)
                                    processing_status = response.payload.get("processingStatus")
                                    #print(processing_status)
                                if processing_status == "DONE":
                                    # Once the processing is done, retrieve the report document
                                    document_id = response.payload.get("reportDocumentId")
                                    response = Reports(credentials=credentials).get_report_document(document_id, download=True)
                                # print(response.payload.get("document"))

                                    s = response.payload.get("document")
                                    buff = StringIO(s)
                                    inventory_reader = csv.DictReader(buff, delimiter='\t' )
                                    #csv.reader
                                    
                                    #next(inventory_reader) #skips the header
                                    for line in inventory_reader:
                                
                                        #print("test")
                                        print(line['sku'], line['asin'], line['price'], line['quantity'])
                                        if line['sku'] == sku:                 #line[0]
                                            Quantity_of_SKU = line['quantity']    #line[3]

                                    print("Qunatity left of sku")
                                    print(sku)
                                    print("is")
                                    print(Quantity_of_SKU)           


                                    Updated_Inventory_Reading = Quantity_of_SKU
                                    print(Updated_Inventory_Reading)
                                    print(int(Initial_quantity_of_sku) + int(return_quantity))
                                    if (int(Updated_Inventory_Reading) == (int(Initial_quantity_of_sku) + int(return_quantity))):
                                        print("ready to break")
                                        break
                                    time.sleep(60)
                    
                                elif processing_status == "CANCELLED":
                                    print("Report processing was cancelled.")
                                elif processing_status == "FATAL":
                                    print("An error occurred during report processing. (FATAL)") 
        return "Inventory Increased Successfully"  