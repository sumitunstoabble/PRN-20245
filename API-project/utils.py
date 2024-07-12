
import random
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import json

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
]

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_case_dict(d):
    return {to_camel_case(k): v for k, v in d.items()}

def get_fake_user_agent_response(url):
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    try:
        response = requests.get(url, headers=headers)
        return response
    except requests.RequestException as e:
        print("An error occurred:", e)
        return None

def get_data(url):
    response = get_fake_user_agent_response(url)
    if response and response.status_code == 200:
        return response.text
    print(f"Request failed with status code: {response.status_code}")
    return None
