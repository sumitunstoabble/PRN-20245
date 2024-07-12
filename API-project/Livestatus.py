
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

def get_data(url):
    r = requests.get(url)
    return r.text

def extract_train_data(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    
    # Extracting the script containing the data
    script_tag = soup.find('script', string=re.compile("var data ="))
    if not script_tag:
        return None
    
    script_content = script_tag.string
    
    # Extracting JSON-like data using regex
    pattern = re.compile(r"var data = ({.*?});", re.DOTALL)
    match = pattern.search(script_content)
    if not match:
        return None
    
    json_data = match.group(1)
    
    # Parsing JSON data
    data = json.loads(json_data)
    return data

def get_main_station_data(train_data, journey_date, html_data):
    main_stations = []
    journey_date_obj = datetime.strptime(journey_date, '%d-%b-%Y')
    
    soup = BeautifulSoup(html_data, 'html.parser')
    running_status_section = soup.find('div', class_='running-status')
    if not running_status_section:
        return None
    
    stations = running_status_section.find_all('div', class_='well well-sm')
    if not stations:
        return None
    
    for i, stop in enumerate(train_data['Schedule']):
        station_data = {
            'Train Number': train_data['TrainNo'],
            'Train Name': train_data['TrainName'],
            'Journey Date': journey_date,
            'Station Name': stop['StationName'],
            'Date': (journey_date_obj + timedelta(days=stop['Day'] - 1)).strftime('%d-%b-%Y'),
            'Arrival Time': stop['ArrivalTime'],
            'Departure Time': stop['DepartureTime'],
            'Delay': get_delay_info(stations[i]),
            'Distance (km)': stop['Distance']
        }
        main_stations.append(station_data)
    return main_stations

def get_delay_info(station_div):
    delay_div = station_div.find('div', class_='rs__station-delay')
    if delay_div:
        return delay_div.text.strip()
    return 'No Information'

def get_current_station(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    running_status_section = soup.find('div', class_='running-status')
    if not running_status_section:
        return 'No Information'
    
    current_station_div = running_status_section.find('div', class_='circle blink')
    if current_station_div:
        current_station = current_station_div.find_next('span', class_='rs__station-name').text.strip()
        return current_station
    return 'No Information'

def extract_available_dates(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    date_options = soup.find_all('option', attrs={'data-day': True})
    if not date_options:
        return []
    available_dates = [option.get('value') for option in date_options]
    return available_dates

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        train_number = request.form['train_number']
        url = f"https://www.confirmtkt.com/train-running-status/{train_number}"
        html_data = get_data(url)
        train_data = extract_train_data(html_data)

        if train_data:
            today_date = datetime.now().strftime('%d-%b-%Y')
            main_station_data_today = get_main_station_data(train_data, today_date, html_data)
            if not main_station_data_today:
                return "Failed to extract train running status data.", 400
            
            available_dates = extract_available_dates(html_data)
            if not available_dates:
                return "No available journey dates found.", 400

            current_station = get_current_station(html_data)
            return render_template('result.html', train_data=main_station_data_today, available_dates=available_dates, current_station=current_station, train_number=train_number, train_name=train_data['TrainName'])
        else:
            return "The train with the given number is not available.", 400
    return render_template('index.html')

@app.route('/select_date', methods=['POST'])
def select_date():
    train_number = request.form['train_number']
    selected_date = request.form['selected_date']
    url = f"https://www.confirmtkt.com/train-running-status/{train_number}"
    html_data = get_data(url)
    train_data = extract_train_data(html_data)

    if train_data:
        main_station_data = get_main_station_data(train_data, selected_date, html_data)
        if not main_station_data:
            return "Failed to extract train running status data for the selected date.", 400

        available_dates = extract_available_dates(html_data)
        if not available_dates:
            return "No available journey dates found.", 400

        current_station = get_current_station(html_data)
        return render_template('result.html', train_data=main_station_data, available_dates=available_dates, current_station=current_station, train_number=train_number, train_name=train_data['TrainName'])
    else:
        return "The train with the given number is not available.", 400

if __name__ == '__main__':
    app.run(debug=True)
