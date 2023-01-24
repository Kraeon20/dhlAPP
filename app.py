import http.client
import urllib.parse
import json
import yaml
from pprint import pprint as pp



tracking_Number = urllib.parse.urlencode({'trackingNumber': input("ENTER TRACKING NUMBER:\n")})

headers = yaml.safe_load(open('db.yaml')).get('userAgent')


connection = http.client.HTTPSConnection("api-eu.dhl.com")
connection.request("GET", "/track/shipments?" + tracking_Number, "", headers)
response = connection.getresponse()



trackingData = yaml.safe_load(response.read())
trackingShipments = trackingData.get('shipments')
trackingError = response.status


# IF TRACKING NUMBER IS CORRECT 
if trackingError == 200:
    trackingStatus = trackingShipments[0]['status']
    trackingEvents = trackingShipments[0]['events']
    trackingID = trackingShipments[0]['id']
    print("TRACKING NUMBER: \n")
    pp(trackingID)
    print("_______________________________________")
    print("TRACKING STATUS: \n")
    pp(trackingStatus)
    print("_______________________________________")
    print("TRACKING EVENT: ")
    pp(trackingEvents)

# IF TRACKING NUMBER IS WRONG
elif trackingError != 200:
    errorTitle = trackingData['title']
    errorDetail = trackingData['detail']
    print(errorTitle)
    print(errorDetail)





connection.close()

