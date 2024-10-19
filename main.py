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
    call_stock = f"{payload.SHEET_STOCK}!{payload.CELL_STOCK}"
    min_price = get_sheet_data(payload.IDSHEET_MIN, cell_min)[0][0]
    max_price = get_sheet_data(payload.IDSHEET_MAX, cell_max)[0][0]
    stock = get_sheet_data(payload.IDSHEET_STOCK, call_stock)[0][0]
    return float(min_price), float(max_price), int(stock)


def get_final_price(current_price: float, target_price: float, min_change_price: float, max_change_price: float,
                    floating_point: int, min_price: float, max_price: float):
    if floating_point is None:
        floating_point = 2

    if current_price == 0:
        print("Current price is 0 so I return target price minus min change price")
        return round(max(min_price, target_price - min_change_price), floating_point)

    if current_price == target_price:
        print("Current price is equal to target price")
        while round(current_price, floating_point) >= target_price:
            current_price -= min_change_price
        return round(max(min_price, current_price - min_change_price), floating_point)

    if current_price < target_price:
        print("Current price is less than target price")
        new_price = target_price - min_change_price
        if new_price < min_price:
            print("New price is less than min price, set current price to min price")
            return min_price
        else:
            return round(new_price, floating_point)

    if current_price > target_price:
        if target_price < min_price:
            print("Target price is less than min price, set current price to min price")
            return min_price
        else:
            while round(current_price - target_price, floating_point) >= max_change_price and round(
                    current_price - max_change_price, floating_point) >= min_price:
                current_price -= max_change_price

            while round(current_price - target_price, floating_point) >= min_change_price and round(
                    current_price - min_change_price, 2) >= min_price:
                current_price -= min_change_price

            if current_price >= min_price - min_change_price:
                current_price -= min_change_price

            return round(max(current_price, min_price), floating_point)


def write_log_cell(index, log_str, column='C'):
    cell_to_write = f'{column}{index + 1 + int(os.getenv("START_ROW"))}'
    spreadsheet_id = os.getenv('MAIN_SHEET_ID')
    sheet_name = os.getenv('MAIN_SHEET_NAME')
    update_sheet_data(spreadsheet_id, sheet_name, cell_to_write, [[log_str]])


def get_target_to_compare(payload: Payload):
    _current_top_offers = get_product_offers(int(payload.PRODUCT_COMPARE), os.getenv('GAMIVO_API_KEY'))
    _current_top_offer = _current_top_offers[0]
    _current_top_price = _current_top_offer['price']
    _current_top_seller = _current_top_offer['seller']

    target_seller = _current_top_seller
    target_price = _current_top_price

    # if _current_top_seller in BLACKLIST and len(_current_top_offers) > 1:
    #     _current_second_offer = _current_top_offers[1]
    #     _current_second_price = _current_second_offer['price']
    #     _current_second_seller = _current_second_offer['seller']
    #
    #
    #
    # if _current_top_seller in BLACKLIST:
    #     target_seller = _current_second_seller
    #     target_price = _current_second_price
    #     if _current_second_seller in BLACKLIST:
    #         target_seller = _current_second_seller
    #         target_price = _current_second_price

    return target_seller, target_price, len(_current_top_offers)


def do_payload(index, payload, blacklist_cache=None):
    global TMP_BLACKLIST_RANGE, BLACKLIST
    global REQUEST_COUNT
    _second_current_top_price = None
    _second_current_top_seller = None
    _third_current_top_price = None
    _third_current_top_seller = None
    _fourth_current_top_price = None
    _fourth_current_top_seller = None
    _compare_price = None
    _compare_seller = None
    REQUEST_COUNT = 0  # Reset request count for each payload

    # Use cached blacklist if available, otherwise fetch once and cache it
    if blacklist_cache is not None:
        BLACKLIST = blacklist_cache
    else:
        TMP_BLACKLIST_RANGE = payload.CELL_BLACKLIST
        # append sheet_blacklist with range
        TMP_BLACKLIST_RANGE = f"{payload.SHEET_BLACKLIST}!{TMP_BLACKLIST_RANGE}"
        BLACKLIST = flatten_2d_array(get_sheet_data(os.getenv("MAIN_SHEET_ID"), TMP_BLACKLIST_RANGE))

    # Fetch min and max prices
    min_price, max_price, stock = get_payload_min_max_price(payload)

    # Gather price and product info in a single API call
    _offer_id = price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE))
    offer_data = retrieve_offer_by_id(_offer_id, os.getenv('GAMIVO_API_KEY'))
    _current_price = offer_data['retail_price']
    _current_top_seller, _current_top_price, num_of_offer = get_target_to_compare(payload)

    # set compare price and seller

    # Calculate target price
    _min_change_price = payload.DONGIAGIAM_MIN
    _max_change_price = payload.DONGIAGIAM_MAX
    _current_price = calculate_seller_price(_offer_id, _current_price, os.getenv('GAMIVO_API_KEY')).get(
        'seller_price')
    _current_top_price = calculate_seller_price(_offer_id, _current_top_price, os.getenv('GAMIVO_API_KEY')).get(
        'seller_price')
    _compare_price = _current_top_price
    _compare_seller = _current_top_seller
    log_data = []
    log_str = ''
    _current_top_offers = get_product_offers(int(payload.PRODUCT_COMPARE), os.getenv('GAMIVO_API_KEY'))

    if len(_current_top_offers) >= 2:
        _second_current_top_price = _current_top_offers[1]['price']
        _second_current_top_seller = _current_top_offers[1]['seller']
        _second_current_top_price = calculate_seller_price(_offer_id, _second_current_top_price,
                                                           os.getenv('GAMIVO_API_KEY')).get(
            'seller_price')

    if len(_current_top_offers) >= 3:
        _third_current_top_price = _current_top_offers[2]['price']
        _third_current_top_seller = _current_top_offers[2]['seller']
        _third_current_top_price = calculate_seller_price(_offer_id, _third_current_top_price,
                                                          os.getenv('GAMIVO_API_KEY')).get(
            'seller_price')
    if len(_current_top_offers) >= 4:
        _fourth_current_top_price = _current_top_offers[3]['price']
        _fourth_current_top_seller = _current_top_offers[3]['seller']
        _fourth_current_top_price = calculate_seller_price(_offer_id, _fourth_current_top_price,
                                                           os.getenv('GAMIVO_API_KEY')).get(
            'seller_price')

    if _current_top_price < min_price:
        _compare_price = _second_current_top_price
        _compare_seller = _second_current_top_seller
        if _second_current_top_price < min_price:
            _compare_price = _third_current_top_price
            _compare_seller = _third_current_top_seller
            if _third_current_top_price < min_price:
                _compare_price = _fourth_current_top_price
                _compare_seller = _fourth_current_top_seller

                # if _compare_price < min_price:
    #     _compare_price = _second_current_top_price
    #     _compare_seller = _second_current_top_seller
    #     if _compare_price < min_price:
    #         _compare_price = _third_current_top_price
    #         _compare_seller = _third_current_top_seller
    #         if _compare_price < min_price:
    #             _compare_price = _fourth_current_top_price
    #             _compare_seller = _fourth_current_top_seller

    # Skip if seller is in blacklist
    if _current_top_seller in BLACKLIST:
        price = _current_price
        if len(_current_top_offers) == 1:
            print(
                f"Current top seller is in blacklist and it the only offer then set to max price: {_current_top_seller}")
            price = max_price
        elif len(_current_top_offers) == 2:
            _second_current_top_seller = _current_top_offers[1]['seller']
            _second_current_top_price = _current_top_offers[1]['price']
            _second_current_top_price = calculate_seller_price(_offer_id, _second_current_top_price,
                                                               os.getenv('GAMIVO_API_KEY')).get(
                'seller_price')
            if _second_current_top_seller in BLACKLIST:
                print(f"2nd top seller is in blacklist and set to max price: {_current_top_seller}")
                price = max_price
            else:
                price = get_final_price(float(_current_price), float(_second_current_top_price),
                                        float(_min_change_price),
                                        float(_max_change_price), int(payload.DONGIA_LAMTRON), float(min_price),
                                        float(max_price))

        edit_offer_payload = price_service.convert_to_new_offer(offer_data, price, stock)
        print(("offer_data", offer_data))
        print(f"Set {payload.Product_name} to {price}")
        status_code, res = put_edit_offer_by_id(edit_offer_payload, _offer_id, os.getenv('GAMIVO_API_KEY'))
        if status_code == 200:
            log_str = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Giá đã cập nhật thành công; Price = {price}; Pricemin = {min_price}, Pricemax = {max_price}, GiaSosanh = {_current_top_price} - Seller: {_current_top_seller}"
            log_str += f"\n----Top Sellers----\n - 1st Seller: {_current_top_seller} - Price: {_current_top_price}"
            if (_second_current_top_seller is not None) and (_second_current_top_price is not None):
                log_str += f" \n- 2nd Seller: {_second_current_top_seller} - Price: {_second_current_top_price}"
            log_data.append((index, log_str, 'C'))
        log_data.append((index, f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'D'))
        print(log_str)
        batch_write_log(log_data)
        return BLACKLIST

    _target_price = get_final_price(float(_current_price), float(_compare_price), float(_min_change_price),
                                    float(_max_change_price), int(payload.DONGIA_LAMTRON), float(min_price),
                                    float(max_price))

    edit_offer_payload = price_service.convert_to_new_offer(offer_data, _target_price, stock)
    print(("offer_data", offer_data))
    print(f"Set {payload.Product_name} to {_target_price}")
    status_code, res = put_edit_offer_by_id(edit_offer_payload, _offer_id, os.getenv('GAMIVO_API_KEY'))
    if status_code == 200:
        log_str = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Giá đã cập nhật thành công; Price = {_target_price}; Pricemin = {min_price}, Pricemax = {max_price}, GiaSosanh = {_compare_price} - Seller: {_compare_seller}"
        log_str += f"\n----Top Sellers----\n- 1st Seller: {_current_top_seller} - Price: {_current_top_price}"
        if (_second_current_top_seller is not None) and (_second_current_top_price is not None):
            log_str += f"\n- 2nd Seller: {_second_current_top_seller} - Price: {_second_current_top_price}"
        if (_third_current_top_seller is not None) and (_third_current_top_price is not None):
            log_str += f"\n- 3rd Seller: {_third_current_top_seller} - Price: {_third_current_top_price}"
        if (_fourth_current_top_seller is not None) and (_fourth_current_top_price is not None):
            log_str += f"\n- 4th Seller: {_fourth_current_top_seller} - Price: {_fourth_current_top_price}"
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
    global BLACKLIST
    sheet_id = os.getenv('MAIN_SHEET_ID')
    data = get_sheet_data(sheet_id, os.getenv('MAIN_SHEET_NAME'))
    data = data[int(os.getenv('START_ROW')):]
    for i in range(len(data)):
        try:
            PAYLOADS.append(Payload(data[i]))
        except:
            continue

    for index, payload in enumerate(PAYLOADS):
        BLACKLIST = []
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
    global PAYLOADS
    load_dotenv('settings.env')
    onload()
    while True:
        PAYLOADS = []
        process_with_retry(os.getenv('RETRIES_TIME', 3))


main()
