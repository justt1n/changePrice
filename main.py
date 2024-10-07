from utils import *
from Payload import Payload

#GLOBAL VARIABLES
gs = None
BLACKLIST = None
PRICES = None

PAYLOADS = []
PAYLOAD = None

def onload():
    global gs
    global BLACKLIST
    global PRICES
    setup_logging()
    gs = get_gs_client()


def process():
    _price_sheet = gs.open_by_url(os.getenv('MAIN_SHEET_URL'))
    data = _price_sheet.worksheet(os.getenv('MAIN_SHEET_NAME')).get_all_values()
    data = data[int(os.getenv('START_ROW')):]
    for i in range(len(data)):
        PAYLOADS.append(Payload(data[i]))
    BLACKLIST = _price_sheet.worksheet('Price')
    PRICES = gs.open('prices').sheet1

def main():
    load_dotenv('settings.env')
    onload()
    process()
main()