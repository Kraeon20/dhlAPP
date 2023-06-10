import http.client
import urllib.parse
import datetime
from flask import Blueprint, render_template, request, current_app, redirect, url_for
import mysql.connector
import json
import pyodbc




with open(r"C:\Users\neczu\Documents\DHLAPP\flask_dhl_app\config\db_config.json", "r") as log:
    login_details = json.load(log)


conn_str =( 
    f"DRIVER={{{login_details ['driver']}}};"
    f"SERVER={login_details ['server']};"
    f"DATABASE={login_details ['database']};"
    "Trust_Connection=yes;"
)




home = Blueprint('home', __name__)

def create_table_and_connect():
    try:
        connection = pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        return
    cursor = connection.cursor()

    try:
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DHL_TRACKING_DATA')
            CREATE TABLE DHL_TRACKING_DATA (
                id INT IDENTITY(1,1) PRIMARY KEY,
                NUMBER VARCHAR(255) NOT NULL,
                STATUS VARCHAR(255),
                CODE VARCHAR(255),
                DEPARTURE VARCHAR(255),
                DELIVERY VARCHAR(255)
            );
        ''')
        connection.commit()
    except mysql.connector.Error as e:
        return
    finally:
        cursor.close()
        connection.close()

create_table_and_connect()



@home.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tracking_number = request.form.get('search')
        return redirect(url_for('home.tracking_number', tracking_number=tracking_number))

    return render_template('index.html', logo_path='../static/media/dhl.png', video_path='../static/media/video.mp4')


@home.route('/tracking_number/<tracking_number>', methods=['GET'])
def tracking_number(tracking_number):
    try:
        url = http.client.HTTPSConnection("api-eu.dhl.com")
    except Exception as e:
        return None
    
    
    process = []

    params = urllib.parse.urlencode({
        'trackingNumber': tracking_number,
    })

    headers = {
        'Accept': current_app.config['ACCEPT'],
        'DHL-API-Key': current_app.config['DHL_API_KEY']
    }

    url.request("GET", "/track/shipments?" + params, "", headers)
    response = url.getresponse()
    error = response.status
    
    
    if error == 200:
        try:
            trackingData = json.loads(response.read().decode('utf-8'))
        except json.JSONDecodeError as e:
            return render_template('error.html')
        
        trackNum = trackingData['shipments'][0].get('id')
        service = trackingData['shipments'][0].get('service')
        deliveryLocation = trackingData['shipments'][0]['status']['location']['address'].get('addressLocality')
        status = trackingData['shipments'][0]['status'].get('status')
        statusDescription =  trackingData['shipments'][0]['status'].get('description')
        statusCode = trackingData['shipments'][0]['status'].get('statusCode')
        packageStatus = trackingData['shipments'][0]['status'].get('status')
        statusTime_str = trackingData['shipments'][0]['status'].get('timestamp')
        statusDate = datetime.datetime.fromisoformat(statusTime_str).strftime("%B, %d %Y")
        statusTime = datetime.datetime.fromisoformat(statusTime_str).strftime("%I:%M%p").lower()
        trackingData["shipments"][0]["status"]["timestamp"] = statusTime
        events = trackingData['shipments'][0]['events']
        
        
        def insert_data(tracking_number, statusDescription, statusCode, sent_from_location, delivery_location):
            # Save tracking number, status, sent from location, and delivery location to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute('''
                            MERGE INTO DHL_TRACKING_DATA AS tgt
                            USING (SELECT ? AS NUMBER, ? AS STATUS, ? AS CODE, ? AS DEPARTURE, ? AS DELIVERY) AS src
                            ON (tgt.NUMBER = src.NUMBER)
                            WHEN MATCHED THEN
                                UPDATE SET tgt.STATUS = src.STATUS, tgt.CODE = src.CODE, tgt.DEPARTURE = src.DEPARTURE, tgt.DELIVERY = src.DELIVERY
                            WHEN NOT MATCHED THEN
                                INSERT (NUMBER, STATUS, CODE, DEPARTURE, DELIVERY)
                                VALUES (src.NUMBER, src.STATUS, src.CODE, src.DEPARTURE, src.DELIVERY);
                        ''', (tracking_number, statusDescription, statusCode, sent_from_location, delivery_location))
            conn.commit()
            cursor.close()
            conn.close()

        
        #gets the sent from address(city and country)
        #from the api regardless of the indice or location of the data
        #this is, it is able to get data from all TRACKING NUMBERS, irrespective 
        # of the country
        for shipment in trackingData['shipments']:
            last_address_Locality = None
            for event in shipment['events']:
                if 'address' in event.get('location', {}) and 'addressLocality' in event['location']['address']:
                    last_address_locality = event['location']['address']['addressLocality']
                    
        insert_data(trackNum, statusDescription, statusCode, last_address_locality, deliveryLocation)
        grouped_events = {}
        for result in events:
            timestamp = result.get('timestamp')
            eventDay = ''
            eventTime = ''
            eventDate = ''
            if timestamp:
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    eventDay = dt.strftime("%A")
                    eventTime= dt.strftime("%B, %d %Y")
                    eventDate = dt.strftime("%I:%M%p").lower()
                except ValueError:
                    None
            trackingProcesses = {
                'eventDay': eventDay,
                'timestamp': timestamp,
                'eventTime': eventTime,
                'eventDate': eventDate,
                'addressLocality': result.get('location', {}).get('address', {}).get('addressLocality', ''),
                'descriptions': result.get('description', ''),

            }
            
            key = f"{eventDay}|{eventTime}"
            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(trackingProcesses)
            
    else:
        return render_template('error.html')
    

    return render_template('tracking-data.html', grouped_events=grouped_events, process=process, van_path='../flask_dhl_app/static/media/delivery.png', logo_path='../static/media/dhl.png',
                        trackNum=trackNum, service=service, deliveryLocation=deliveryLocation, last_address_locality=last_address_locality,
                        status=status, statusCode=statusCode, statusDescription=statusDescription, statusTime=statusTime,
                        statusDate=statusDate)
