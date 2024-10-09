import codecs
import logging
import os
import time
from datetime import datetime

import gspread
import wget
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import json


def flatten_json_file(input_file, output_file):
    # Load data from JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Initialize an empty list to store the flattened data
    flattened_data = []

    # Loop through the outer list and extend the flattened list with each inner list
    for inner_list in data:
        flattened_data.extend(inner_list)

    # Write the flattened list back to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(flattened_data, f, indent=4)

    print(f"Data successfully flattened and saved to {output_file}")

def setup_logging():
    # Load environment variables at the beginning of the script
    load_dotenv('settings.env')

    # Configure logging from environment variables
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(message)s')

    # Create log file based on the current date in the logs/ directory
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}_function_calls.log")

    logging.basicConfig(filename=log_file, level=log_level, format=log_format)


def print_function_name(func):
    def wrapper(*args, **kwargs):
        try:
            log_message = f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}"
            logging.info(log_message)
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in function {func.__name__}: {e}")
            raise

    return wrapper


def get_gs_client():
    # Load environment variables at the beginning of the script
    load_dotenv('settings.env')

    # Define the scope of the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    _key_path = os.getenv('GOOGLE_KEY_PATH')

    if not _key_path:
        raise ValueError("GOOGLE_KEY_PATH environment variable is not set")

    if not os.path.exists(_key_path):
        # download from link
        logging.info("Downloading Google Service Account Key...")
        wget.download(os.getenv('GOOGLE_KEY_URL'), _key_path)
        logging.info("Google Service Account Key downloaded")

    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_KEY_PATH"), scope)

    client = gspread.authorize(creds)

    return client


def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def read_json(path:str, encoding='utf-8'):
    with codecs.open(path, 'r', encoding) as file:
        data = json.load(file)
    return data


def write_json(path:str, data, encoding='utf-8'):
    #create if not exists
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with codecs.open(path, 'w', encoding) as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return True


def flatten_2d_array(two_d_array):
    flattened_list = []
    for sublist in two_d_array:
        flattened_list.extend(sublist)
    return flattened_list

# flatten_json_file('storage/product_offer.json', 'storage/flattened_product_offer.json')