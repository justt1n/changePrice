import json
import sqlite3

output_file = './storage/product_offer.json'

def migrate_offers_json_to_sqlite(json_file, sqlite_db):
    # Connect to SQLite (or create the database)
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Create the 'product_offers' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_offers (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        product_name TEXT,
        seller_name TEXT,
        completed_orders INTEGER,
        rating REAL,
        retail_price REAL,
        stock_available INTEGER,
        invoicable BOOLEAN,
        status INTEGER,
        wholesale_mode INTEGER,
        is_preorder BOOLEAN,
        seller_price REAL
    )
    ''')

    cursor.execute('DELETE FROM product_offers')

    # Load data from JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Loop through the JSON data and insert each product offer
    for product_batch in data:
        for product_offer in product_batch:
            cursor.execute('''
            INSERT INTO product_offers (
                id, product_id, product_name, seller_name, completed_orders, rating,
                retail_price, stock_available, invoicable, status, wholesale_mode,
                is_preorder, seller_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(product_offer['id']),
                product_offer['product_id'],
                product_offer['product_name'],
                product_offer['seller_name'],
                product_offer['completed_orders'],
                product_offer['rating'],
                product_offer['retail_price'],
                product_offer['stock_available'],
                int(product_offer['invoicable']),
                product_offer['status'],
                product_offer['wholesale_mode'],
                int(product_offer['is_preorder']),
                product_offer['seller_price']
            ))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Data successfully migrated to {sqlite_db}")

# Example usage:
# migrate_offers_json_to_sqlite(output_file, 'product_offers.db')