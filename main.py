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
    return int(min_price)


def get_payload_max_price(payload: Payload):
    tmp_price_sheet = gs.open_by_key(payload.IDSHEET_MAX)
    max_price = tmp_price_sheet.worksheet(payload.SHEET_MAX).acell(payload.CELL_MAX).value
    return int(max_price)





def do_payload(payload):
    global TMP_BLACKLIST_RANGE
    TMP_BLACKLIST_RANGE = payload.CELL_BLACKLIST
    min_price = get_payload_min_price(payload)
    max_price = get_payload_max_price(payload)
    print(f"Min price: {min_price}")
    print(f"Max price: {max_price}")
    _offer_id = price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE))
    print(f"Offer ID: {_offer_id}")
    _current_price = retrieve_offer_by_id(price_service.get_order_id_by_product_id(int(payload.PRODUCT_COMPARE)), os.getenv('GAMIVO_API_KEY'))['retail_price']
    print(f"My price: {_current_price}")
    _current_top = get_product_offers(int(payload.PRODUCT_COMPARE), os.getenv('GAMIVO_API_KEY'))[0]
    _current_top_price = _current_top['price']
    _current_top_seller = _current_top['seller']
    print(f"Top price: {_current_top_price}")
    print(f"Top seller: {_current_top_seller}")

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
