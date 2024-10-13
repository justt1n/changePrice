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


def retrieve_offer_by_id(offer_id: int, api_key: str)-> dict:
    url = f"https://backend.gamivo.com/api/public/v1/offers/{offer_id}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    response = requests.get(url, headers=headers)
    return response.json()



def put_edit_offer_by_id(model: ChangePriceModel, offer_id: int, api_key: str):
    url = f"https://backend.gamivo.com/api/public/v1/offers/{offer_id}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    data = {
        "wholesale_mode": model.get('wholesale_mode', 0),
        "seller_price": model.get('seller_price', 0),
        "tier_one_seller_price": model.get('tier_one_seller_price', 0),
        "tier_two_seller_price": model.get('tier_two_seller_price', 0),
        "status": 1,
        "keys": model.get('keys', 10000),
        "is_preorder": model.get('is_preorder', False)
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response.status_code, response.json()


def calculate_seller_price(offer_id: int, price: float, api_key: str) -> dict:
    url = f"https://backend.gamivo.com/api/public/v1/offers/calculate-seller-price/{offer_id}?price={price}&tier_one_price=0&tier_two_price=0"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    response = requests.get(url, headers=headers)
    return response.json()
