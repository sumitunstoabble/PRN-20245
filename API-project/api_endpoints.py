from flask import jsonify, request
from utils import get_data, camel_case_dict
from data_extraction import extract_train_data, get_main_station_data, get_current_station, extract_available_dates
from datetime import datetime

def register_endpoints(app, limiter):
    @app.route('/api/v1/train_status', methods=['POST'])
    @limiter.limit("120 per minute")
    def train_status():
        if not request.json or 'trainNumber' not in request.json:
            return jsonify(camel_case_dict({'errorMessage': 'Invalid input: trainNumber is required'})), 400

        train_number = request.json['trainNumber']
        url = f"https://www.confirmtkt.com/train-running-status/{train_number}"
        html_data = get_data(url)
        if not html_data:
            return jsonify(camel_case_dict({'errorMessage': 'Failed to retrieve data from the server'})), 500

        train_data = extract_train_data(html_data)
        if train_data:
            today_date = datetime.now().strftime('%d-%b-%Y')
            main_station_data_today = get_main_station_data(train_data, today_date, html_data)
            if not main_station_data_today:
                return jsonify(camel_case_dict({'errorMessage': 'Failed to extract train running status data'})), 500

            available_dates = extract_available_dates(html_data)
            if not available_dates:
                return jsonify(camel_case_dict({'errorMessage': 'No available journey dates found'})), 500

            current_station = get_current_station(html_data, main_station_data_today)
            response_data = {
                'trainData': main_station_data_today,
                'availableDates': available_dates,
                'currentStation': current_station,
                'trainNumber': train_number,
                'trainName': train_data['TrainName'],
                'selectedDate': today_date
            }
            return jsonify(camel_case_dict(response_data)), 200

        return jsonify(camel_case_dict({'errorMessage': 'The train with the given number is not available'})), 404

    @app.route('/api/v1/select_date', methods=['POST'])
    @limiter.limit("120 per minute")
    def select_date():
        if not request.json or 'trainNumber' not in request.json or 'selectedDate' not in request.json:
            return jsonify(camel_case_dict({'errorMessage': 'Invalid input: trainNumber and selectedDate are required'})), 400

        train_number = request.json['trainNumber']
        selected_date = request.json['selectedDate']
        url = f"https://www.confirmtkt.com/train-running-status/{train_number}?Date={selected_date}"
        html_data = get_data(url)
        if not html_data:
            return jsonify(camel_case_dict({'errorMessage': 'Failed to retrieve data from the server'})), 500

        train_data = extract_train_data(html_data)
        if train_data:
            main_station_data = get_main_station_data(train_data, selected_date, html_data)
            if not main_station_data:
                return jsonify(camel_case_dict({'errorMessage': 'No data found for that given date'})), 500

            current_station = get_current_station(html_data, main_station_data)
            available_dates = extract_available_dates(html_data)
            response_data = {
                'trainData': main_station_data,
                'availableDates': available_dates,
                'currentStation': current_station,
                'trainNumber': train_number,
                'trainName': train_data['TrainName'],
                'selectedDate': selected_date
            }
            return jsonify(camel_case_dict(response_data)), 200

        return jsonify(camel_case_dict({'errorMessage': 'The train with the given number is not available'})), 404
