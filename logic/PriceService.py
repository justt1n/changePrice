from utils import *
from logic.SQLiteDB import *


class PriceService:
    def __init__(self):
        self.product_db = SQLiteDB('storage/products.db')
        self.offer_db = SQLiteDB('storage/product_offers.db')

    def get_order_id_by_product_id(self, product_id)-> int:
        query = f"SELECT id FROM product_offers WHERE product_id = {product_id}"
        result = self.offer_db.fetch_query(query)
        if result:
            return result[0][0]
        return None


# a = PriceService()
# print(a.get_order_id_by_product_id(176323))