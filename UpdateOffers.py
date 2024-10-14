import json

import numpy as np

from logic.GetOfferList import get_product_list
from utils import *
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Authenticate and return a Google Sheets API service."""
    creds = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_KEY_PATH'), scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service


### Wrapper functions to count requests
def get_sheet_data(service, sheet_id, range_name):
    """Get data from the Google Sheet."""
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])


def batch_update_csv_to_sheet(service, spreadsheet_id, sheet_name, csv_file_path):
    """Batch update a Google Sheet with data from a CSV file."""
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Replace NaN values with an empty string
    df = df.replace(np.nan, '', regex=True)

    # Extract the header
    header = df.columns.tolist()

    # Convert the DataFrame into a 2D list including the header
    data = [header] + df.values.tolist()

    # Format the data for the Google Sheets API
    formatted_data = []
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            formatted_data.append({
                'range': f"{sheet_name}!{chr(65 + col_index)}{row_index + 1}",
                'values': [[value]]
            })

    body = {
        'data': formatted_data,
        'valueInputOption': 'RAW'
    }

    # Batch update the Google Sheet
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def update_offers():
    load_dotenv('settings.env')
    get_product_list()

    # Flatten JSON and read into DataFrame
    flatten_json_file('storage/product_offer.json', 'storage/flattened_product_offer.json')
    offers = pd.read_json('storage/flattened_product_offer.json')

    # Save DataFrame to CSV and read it back
    offers.to_csv('storage/product_offers.csv', index=False)

    # Authenticate and get the Google Sheets service
    service = get_sheets_service()
    batch_update_csv_to_sheet(service, os.getenv('OFFERS_SHEET_ID'), os.getenv('OFFERS_SHEET_NAME'),
                              'storage/product_offers.csv')

update_offers()

