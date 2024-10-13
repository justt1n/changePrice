from logic.SQLiteDB import *


class PriceService:
    def __init__(self):
        self.product_db = SQLiteDB('storage/products.db')
        self.offer_db = SQLiteDB('storage/product_offers.db')

    def get_order_id_by_product_id(self, product_id) -> int:
        query = f"SELECT id FROM product_offers WHERE product_id = {product_id}"
        result = self.offer_db.fetch_query(query)
        if result:
            return result[0][0]
        return None

    def convert_to_new_offer(self, offer_data: dict, new_price: float, stock: int) -> dict:
        _tier_one_seller_price = offer_data.get('tier_one_seller_price', 0) or 0
        _tier_two_seller_price = offer_data.get('tier_two_seller_price', 0) or 0
        return {
            "wholesale_mode": offer_data.get('wholesale_mode', 0) or 0,
            "seller_price": new_price,
            "tier_one_seller_price": _tier_one_seller_price,
            "tier_two_seller_price": _tier_two_seller_price,
            "status": 1,
            "keys": offer_data.get("keys", stock),  # "keys": 2000,
            "is_preorder": offer_data['is_preorder']
        }
