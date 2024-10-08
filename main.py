import os

from utils import *
from Payload import Payload

#GLOBAL VARIABLES
gs = None
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
    setup_logging()
    gs = get_gs_client()


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


def process():
    _price_sheet = gs.open_by_url(os.getenv('MAIN_SHEET_URL'))
    data = _price_sheet.worksheet(os.getenv('MAIN_SHEET_NAME')).get_all_values()
    data = data[int(os.getenv('START_ROW')):]
    for i in range(len(data)):
        PAYLOADS.append(Payload(data[i]))

    for payload in PAYLOADS:
        do_payload(payload)


def main():
    load_dotenv('settings.env')
    onload()
    process()


main()
