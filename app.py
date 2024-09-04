from datetime import datetime, timedelta
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = '0de3b5f3277ec089a5f495872d29b560'

@app.template_filter('datetimeformat')
def datetimeformat(value, tz_offset):
    utc_time = datetime.utcfromtimestamp(value)
    local_time = utc_time + timedelta(seconds=tz_offset)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('timedelta')
def timedelta_format(value):
    total_seconds = int(value.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    if lat and lon:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            
            # Calculate time until sunrise and sunset
            current_time = datetime.utcfromtimestamp(weather_data['dt']) + timedelta(seconds=weather_data['timezone'])
            sunrise_time = datetime.utcfromtimestamp(weather_data['sys']['sunrise']) + timedelta(seconds=weather_data['timezone'])
            sunset_time = datetime.utcfromtimestamp(weather_data['sys']['sunset']) + timedelta(seconds=weather_data['timezone'])
            
            time_until_sunrise = sunrise_time - current_time
            time_until_sunset = sunset_time - current_time
            
            # Add calculated data to weather_data dictionary
            weather_data['time_until_sunrise'] = time_until_sunrise
            weather_data['time_until_sunset'] = time_until_sunset

            return render_template('weather.html', weather_data=weather_data)
        else:
            return render_template('weather.html', weather_data={'error': 'Weather data not found'})
    return render_template('weather.html', weather_data={'error': 'Invalid location'})

if __name__ == '__main__':
    app.run(debug=True)
