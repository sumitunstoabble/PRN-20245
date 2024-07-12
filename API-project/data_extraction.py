
from utils import camel_case_dict, get_data
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta

def extract_train_data(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    script_tag = soup.find('script', string=re.compile("var data ="))
    if not script_tag:
        return None

    script_content = script_tag.string
    pattern = re.compile(r"var data = ({.*?});", re.DOTALL)
    match = pattern.search(script_content)
    if not match:
        return None

    json_data = match.group(1)
    train_data = json.loads(json_data)

    station_codes = {}
    for stop in train_data['Schedule']:
        station_codes[stop['StationName']] = stop['StationCode']
        for intermediate in stop.get('intermediateStations', []):
            station_codes[intermediate['StationName']] = intermediate['StationCode']
    
    train_data['StationCodes'] = station_codes
    return train_data

def get_main_station_data(train_data, journey_date, html_data):
    main_stations = []
    journey_date_obj = datetime.strptime(journey_date, '%d-%b-%Y')
    soup = BeautifulSoup(html_data, 'html.parser')
    running_status_section = soup.find('div', class_='running-status')
    if not running_status_section:
        return None

    stations = running_status_section.find_all('div', class_='well well-sm')
    for i, stop in enumerate(train_data['Schedule']):
        station_name = stop['StationName']
        station_code = train_data['StationCodes'].get(station_name, 'Unknown')
        station_data = {
            'trainNumber': train_data['TrainNo'],
            'trainName': train_data['TrainName'],
            'journeyDate': journey_date,
            'stationName': f"{station_name} ({station_code})",
            'date': (journey_date_obj + timedelta(days=stop['Day'] - 1)).strftime('%d-%b-%Y'),
            'arrivalTime': stations[i].find_all('div', class_='col-xs-2')[0].text.strip() if i < len(stations) else 'No Information',
            'departureTime': stations[i].find_all('div', class_='col-xs-2')[1].text.strip() if i < len(stations) else 'No Information',
            'delay': get_delay_info(stations[i]) if i < len(stations) else 'No Information',
            'distanceKm': stop['Distance']
        }
        main_stations.append(camel_case_dict(station_data))
    return main_stations

def get_delay_info(station_div):
    delay_div = station_div.find('div', class_='rs__station-delay')
    return delay_div.text.strip() if delay_div else 'No Information'

def get_current_station(html_data, main_stations):
    soup = BeautifulSoup(html_data, 'html.parser')
    current_station_div = soup.find('div', class_='circle blink')
    if current_station_div:
        current_station = current_station_div.find_next('span', class_='rs__station-name').text.strip()
        return current_station
    return 'No Information'

def extract_available_dates(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    date_options = soup.find_all('option', attrs={'data-day': True})
    available_dates = []
    for option in date_options:
        day_text = option.get('data-day')
        date_value = option.get('value')
        available_dates.append(f"{day_text} {date_value}")
    return available_dates if available_dates else []
