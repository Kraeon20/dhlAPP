import http.client
import urllib.parse
import yaml
import datetime
from flask import Blueprint, render_template, request, current_app, redirect, url_for


home = Blueprint('home', __name__)

@home.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tracking_number = request.form.get('search')
        return redirect(url_for('home.tracking', tracking_number=tracking_number))

    return render_template('phoenix.html', logo_path='../static/media/dhl.png', video_path='../static/media/video.mp4')


@home.route('/tracking/<tracking_number>', methods=['GET'])
def tracking(tracking_number):
    url = http.client.HTTPSConnection("api-eu.dhl.com")

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
        trackingData = yaml.safe_load(response.read())
        trackNum = trackingData['shipments'][0]['id']
        service = trackingData['shipments'][0]['service']
        deliveryLocation = trackingData['shipments'][0]['status']['location']['address']['addressLocality']
        status = trackingData['shipments'][0]['status']['status']
        statusDescription =  trackingData['shipments'][0]['status']['description']
        statusCode = trackingData['shipments'][0]['status']['statusCode']
        statusTime_str = trackingData['shipments'][0]['status']['timestamp']
        statusDate = datetime.datetime.fromisoformat(statusTime_str).strftime("%B, %d %Y")
        statusTime = datetime.datetime.fromisoformat(statusTime_str).strftime("%I:%M%p").lower()

        trackingData["shipments"][0]["status"]["timestamp"] = statusTime
        events = trackingData['shipments'][0]['events']
        
        
        #gets the sent from address(city and country)
        #from the api regardless of the indice or location of the data
        #this is, it is able to get data from all TRACKING NUMBERS, irrespective 
        # of the country
        for shipment in trackingData['shipments']:
            last_address_Locality = None
            for event in shipment['events']:
                if 'address' in event.get('location', {}) and 'addressLocality' in event['location']['address']:
                    last_address_locality = event['location']['address']['addressLocality']
                
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
                'descriptions': result['description'],
            }
            
            key = f"{eventDay}|{eventTime}"
            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(trackingProcesses)
            
    else:
        return render_template('error.html')
    return render_template('progress.html',grouped_events=grouped_events, process=process, van_path='../flask_dhl_app/static/media/delivery.png', logo_path='../static/media/dhl.png',
                        trackNum=trackNum, service=service, deliveryLocation=deliveryLocation, last_address_locality=last_address_locality,
                        status=status, statusCode=statusCode, statusDescription=statusDescription, statusTime=statusTime,
                        statusDate=statusDate)


