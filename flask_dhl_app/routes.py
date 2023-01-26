import http.client
import urllib.parse
import yaml
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
        events = trackingData['shipments'][0]['events']

        for result in events:
            trackingProcesses = {
                'timestamp': result['timestamp'],
                'addressLocality': result['location']['address']['addressLocality'],
                'descriptions': result['description'],
            }
            process.append(trackingProcesses)
    else:
        return render_template('error.html')
    return render_template('tracking.html', process=process)
