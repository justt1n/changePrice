import os

from logic.PriceService import PriceService
from logic.GamivoApiClient import *
from utils import *
from Payload import Payload

#GLOBAL VARIABLES
gs = None
price_service = None
BLACKLIST = None
PRICES = None

PAYLOADS = []
PAYLOAD = None

#TMP VARIABLES
TMP_BLACKLIST_RANGE = None
TMP_PRICE_RANGE = None


def onload():
    global gs
    global BLACKLIST
    global PRICES
    global price_service
    setup_logging()
    gs = get_gs_client()
    price_service = PriceService()


def get_payload_min_price(payload: Payload):
    tmp_price_sheet = gs.open_by_key(payload.IDSHEET_MIN)
    min_price = tmp_price_sheet.worksheet(payload.SHEET_MIN).acell(payload.CELL_MIN).value
    return float(min_price)


def get_payload_max_price(payload: Payload):
    tmp_price_sheet = gs.open_by_key(payload.IDSHEET_MAX)
    max_price = tmp_price_sheet.worksheet(payload.SHEET_MAX).acell(payload.CELL_MAX).value
    return float(max_price)


def get_final_price(current_price: float, target_price:float,  min_change_price: float, max_change_price: float, floating_point: int, min_price: float, max_price: float):
    if current_price == 0:
        print("Current price is 0 so we return target price minus min change price")
        return target_price - min_change_price
    if current_price == target_price:
        print("Current price is equal to target price")
        return current_price - min_change_price
    if current_price < target_price:
        print("Current price is less than target price")
        if target_price > max_price:
            print("Target price is greater than max price, set current price to max price")
            return max_price
        else:
            while current_price < target_price:
                current_price += max_change_price
        return current_price
    if current_price > target_price:
        if target_price < min_price:
            print("Target price is less than min price, set current price to min price")
            return min_price
        else:
            while current_price - target_price >= max_change_price and current_price - max_change_price >= min_price:
                print("Current price is greater than target price and max change price")
                current_price -= max_change_price
            print(f"Current price: {current_price-target_price}")
            while current_price - target_price <= min_change_price and current_price - min_change_price >= min_price:
                print("Current price is greater than target price and min change price")
                current_price -= min_change_price
            return current_price



def do_payload(payload):
    global TMP_BLACKLIST_RANGE
    TMP_BLACKLIST_RANGE = payload.CELL_BLACKLIST
    min_price = get_payload_min_price(payload)
    max_price = get_payload_max_price(payload)
    _is_changed = False
    #init value from payload
    _offer_id = price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE))
    _current_price = retrieve_offer_by_id(price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE)), os.getenv('GAMIVO_API_KEY'))['retail_price']
    _current_top = get_product_offers(int(payload.PRODUCT_COMPARE), os.getenv('GAMIVO_API_KEY'))[0]
    _current_top_price = _current_top['price']
    _current_top_seller = _current_top['seller']
    _min_change_price = payload.DONGIAGIAM_MIN
    _max_change_price = payload.DONGIAGIAM_MAX
    _target_price = get_final_price(float(_current_price), float(_current_top_price), float(_min_change_price),
                                    float(_max_change_price), 2, float(min_price), float(max_price))
    print(f"Min price: {min_price}")
    print(f"Max price: {max_price}")
    print(f"Min change price: {_min_change_price}")
    print(f"Max change price: {_max_change_price}")
    print(f"Offer ID: {_offer_id}")
    print(f"My price: {_current_price}")
    print(f"Top price: {_current_top_price}")
    print(f"Top seller: {_current_top_seller}")
    print(f"Target price: {_target_price}")

    #TODO update price

    #TODO add result to sheet
    if not _is_changed:
        log_str = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Giá đã cập nhật thành công; Price = {_target_price}; Pricemin = {min_price}, Pricemax = {max_price}, GiaSosanh = {_current_top_price} - Seller: {_current_top_seller}"
        print(log_str)

def process():
    _price_sheet = gs.open_by_url(os.getenv('MAIN_SHEET_URL'))
    data = _price_sheet.worksheet(os.getenv('MAIN_SHEET_NAME')).get_all_values()
    data = data[int(os.getenv('START_ROW')):]
    for i in range(len(data)):
        PAYLOADS.append(Payload(data[i]))

    for payload in PAYLOADS:
        if int(payload.CHECK) != 1:
            continue
        do_payload(payload)



def main():
    load_dotenv('settings.env')
    onload()
    process()


main()
