import json

import requests
import os

from dotenv import load_dotenv
from gspread import api_key

from entity import ChangePriceModel


#Get top 2 offer by products id
#/api/public/v1/products/{id}/offers
def get_product_offers(product_id: int, api_key: str)-> list:
    url = f"https://backend.gamivo.com/api/public/v1/products/{str(product_id)}/offers"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    results = [] # {price: 0, seller: ''}
    for i in data:
        results.append({
            'seller': i['seller_name'],
            'price': i['retail_price']
        })
    return results

def put_edit_offer_by_id(model: ChangePriceModel):


    pass



load_dotenv('../settings.env')
print(get_product_offers(176323, os.getenv('GAMIVO_API_KEY')))