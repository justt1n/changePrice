from datetime import datetime
from time import sleep

from google.oauth2 import service_account
from googleapiclient.discovery import build

from Payload import Payload
from logic.GamivoApiClient import *
from logic.PriceService import PriceService
from utils import *

# GLOBAL VARIABLES
service = None
price_service = None
BLACKLIST = None
PRICES = None
REQUEST_COUNT = 0  # Global counter for Google API requests

PAYLOADS = []
PAYLOAD = None

# TMP VARIABLES
TMP_BLACKLIST_RANGE = None
TMP_PRICE_RANGE = None

# Google Sheets API constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def increment_request_count():
    """Increments the global request counter."""
    global REQUEST_COUNT
    REQUEST_COUNT += 1


def get_sheets_service():
    """Authenticate and return a Google Sheets API service."""
    creds = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_KEY_PATH'), scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service


def onload():
    global service
    global price_service
    setup_logging()
    service = get_sheets_service()
    price_service = PriceService()


### Wrapper functions to count requests
def get_sheet_data(sheet_id, range_name):
    """Get data from the Google Sheet."""
    increment_request_count()  # Increment request count
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])


def update_sheet_data(sheet_id, sheet_name, range_name, values):
    """Update the Google Sheet."""
    increment_request_count()  # Increment request count
    body = {
        'values': values
    }
    full_range = f"{sheet_name}!{range_name}"
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=full_range,
        valueInputOption='RAW', body=body).execute()


def batch_update_sheet_data(sheet_id, data):
    """Batch update the Google Sheet."""
    increment_request_count()  # Increment request count
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={'data': data, 'valueInputOption': 'RAW'}
    ).execute()


def get_payload_min_max_price(payload: Payload):
    cell_min = f"{payload.SHEET_MIN}!{payload.CELL_MIN}"
    cell_max = f"{payload.SHEET_MAX}!{payload.CELL_MAX}"
    min_price = get_sheet_data(payload.IDSHEET_MIN, cell_min)[0][0]
    max_price = get_sheet_data(payload.IDSHEET_MAX, cell_max)[0][0]
    return float(min_price), float(max_price)


def get_final_price(current_price: float, target_price: float, min_change_price: float, max_change_price: float,
                    floating_point: int, min_price: float, max_price: float):
    if floating_point is None:
        floating_point = 2
    if current_price == 0:
        print("Current price is 0 so I return target price minus min change price")
        return round(target_price - min_change_price, floating_point)
    if current_price == target_price:
        print("Current price is equal to target price")
        return round(current_price - min_change_price, floating_point)
    if current_price < target_price:
        print("Current price is less than target price")
        if target_price > max_price:
            print("Target price is greater than max price, set current price to max price")
            return max_price
        else:
            while current_price + max_change_price < target_price:
                current_price += max_change_price
            while current_price + min_change_price < target_price:
                current_price += min_change_price
            print("Current price is less than target price, optimize the price, new price is: ", round(current_price, floating_point))
        return round(current_price, floating_point)
    if current_price > target_price:
        if target_price < min_price:
            print("Target price is less than min price, set current price to min price")
            return min_price
        else:
            while current_price - target_price >= max_change_price and current_price - max_change_price >= min_price:
                print("Current price is greater than target price and max change price")
                current_price -= max_change_price
            while current_price - target_price <= min_change_price and current_price - min_change_price >= min_price:
                print("Current price is greater than target price and min change price")
                current_price -= min_change_price
            return round(current_price, floating_point)


def write_log_cell(index, log_str, column='C'):
    cell_to_write = f'{column}{index + 1 + int(os.getenv("START_ROW"))}'
    spreadsheet_id = os.getenv('MAIN_SHEET_ID')
    sheet_name = os.getenv('MAIN_SHEET_NAME')
    update_sheet_data(spreadsheet_id, sheet_name, cell_to_write, [[log_str]])


def do_payload(index, payload, blacklist_cache=None):
    global TMP_BLACKLIST_RANGE, BLACKLIST
    global REQUEST_COUNT

    REQUEST_COUNT = 0  # Reset request count for each payload

    # Use cached blacklist if available, otherwise fetch once and cache it
    if blacklist_cache is not None:
        BLACKLIST = blacklist_cache
    else:
        TMP_BLACKLIST_RANGE = payload.CELL_BLACKLIST
        BLACKLIST = flatten_2d_array(get_sheet_data(payload.IDSHEET_BLACKLIST, TMP_BLACKLIST_RANGE))

    # Fetch min and max prices
    min_price, max_price = get_payload_min_max_price(payload)

    # Gather price and product info in a single API call
    _offer_id = price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE))
    offer_data = retrieve_offer_by_id(_offer_id, os.getenv('GAMIVO_API_KEY'))
    _current_price = offer_data['retail_price']
    _current_top_offer = get_product_offers(int(payload.PRODUCT_COMPARE), os.getenv('GAMIVO_API_KEY'))[0]
    _current_top_price = _current_top_offer['price']
    _current_top_seller = _current_top_offer['seller']

    # Calculate target price
    _min_change_price = payload.DONGIAGIAM_MIN
    _max_change_price = payload.DONGIAGIAM_MAX
    _current_top_price = calculate_seller_price(_offer_id, _current_top_price, os.getenv('GAMIVO_API_KEY')).get('seller_price')

    _target_price = get_final_price(float(_current_price), float(_current_top_price), float(_min_change_price),
                                    float(_max_change_price), int(payload.DONGIA_LAMTRON), float(min_price), float(max_price))


    # Skip if seller is in blacklist
    if _current_top_seller in BLACKLIST:
        print(f"Current top seller is in blacklist: {_current_top_seller}")
        return BLACKLIST

    # Log information
    log_data = []

    if _current_top_seller == "Cnlgaming":
        log_data.append((index, f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'D'))
        batch_write_log(log_data)
        # print(f"Requests made for this payload: {REQUEST_COUNT}")
        return BLACKLIST

    edit_offer_payload = price_service.convert_to_new_offer(offer_data, _target_price)
    # print(f"Edit offer payload: {edit_offer_payload}")
    status_code, res = put_edit_offer_by_id(edit_offer_payload, _offer_id, os.getenv('GAMIVO_API_KEY'))
    if status_code == 200:
        log_str = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Giá đã cập nhật thành công; Price = {_target_price}; Pricemin = {min_price}, Pricemax = {max_price}, GiaSosanh = {_current_top_price} - Seller: {_current_top_seller}"
        print(log_str)
        log_data.append((index, log_str, 'C'))

    # log_str = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Giá đã cập nhật thành công; Price = {_target_price}; Pricemin = {min_price}, Pricemax = {max_price}, GiaSosanh = {_current_top_price} - Seller: {_current_top_seller}"
    print(log_str)
    # Log the action
    log_data.append((index, f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'D'))

    # Batch write log data
    batch_write_log(log_data)

    # print(f"Requests made for this payload: {REQUEST_COUNT}")  # Print the request count after processing
    return BLACKLIST


def batch_write_log(log_data):
    """Batch write log data to reduce individual API requests."""
    cells_to_update = []
    for log in log_data:
        index, log_str, column = log
        cell_to_write = f'{column}{index + 1 + int(os.getenv("START_ROW"))}'
        cells_to_update.append({'range': cell_to_write, 'values': [[log_str]]})

    if cells_to_update:
        sheet_id = os.getenv('MAIN_SHEET_ID')
        batch_update_sheet_data(sheet_id, cells_to_update)


def process():
    sheet_id = os.getenv('MAIN_SHEET_ID')
    data = get_sheet_data(sheet_id, os.getenv('MAIN_SHEET_NAME'))
    data = data[int(os.getenv('START_ROW')):]
    for i in range(len(data)):
        try:
            PAYLOADS.append(Payload(data[i]))
        except:
            continue

    for index, payload in enumerate(PAYLOADS):
        if payload.CHECK == '':
            continue
        if int(payload.CHECK) != 1:
            continue
        for _ in range(2):  # Maximum of two attempts
            try:
                do_payload(index, payload)
                break  # If successful, break the loop
            except Exception as e:
                if "Quota exceeded for quota metric" in str(e):
                    print("Quota exceeded, sleeping for 60 seconds")
                    sleep(60)
                else:
                    log_str = f"Error processing payload at index {index}: {e}"
                    write_log_cell(index, log_str, column='E')
                    break  # If it's not a quota issue, break the loop


def process_with_retry(retries=3):
    retries = int(os.getenv('RETRIES_TIME', retries))
    for i in range(retries):
        try:
            process()
            break
        except Exception as e:
            sleep(30)
            print(f"Error processing payload: {e}. Retry {i + 1}/{retries}")
            continue


def main():
    load_dotenv('settings.env')
    onload()
    process_with_retry(os.getenv('RETRIES_TIME', 3))

main()
