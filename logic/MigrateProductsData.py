import json
import sqlite3

output_file = '../storage/products.json'


def migrate_products_json_to_sqlite(json_file, sqlite_db):
    # Connect to SQLite (or create the database)
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Create the 'products' table without the 'description' field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        genres TEXT,           -- Store as a comma-separated string
        languages TEXT,        -- Store as a comma-separated string
        platform TEXT,
        notice TEXT,
        region TEXT,
        release_date TEXT,
        lowest_price REAL,
        minimal_selling_price REAL,
        is_preorder BOOLEAN
    )
    ''')

    # Load data from JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # The expected format is [[{},{},..{}],[{},{},..],...]
    # Loop through the outer list, assuming each inner list represents a batch of products
    for product_batch in data:
        for product in product_batch:
            cursor.execute('''
            INSERT INTO products (
                id, name, genres, languages, platform, notice, region, release_date, 
                lowest_price, minimal_selling_price, is_preorder
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['id'],
                product['name'],
                ','.join(product.get('genres', [])),  # Use empty list if 'genres' is missing
                ','.join(product.get('languages', [])),  # Use empty list if 'languages' is missing
                product.get('platform', ''),  # Use empty string if 'platform' is missing
                product.get('notice', ''),  # Use empty string if 'notice' is missing
                product.get('region', ''),  # Use empty string if 'region' is missing
                product.get('release_date', ''),  # Use empty string if 'release_date' is missing
                product.get('lowest_price', 0.0),  # Use 0.0 if 'lowest_price' is missing
                product.get('minimal_selling_price', 0.0),  # Use 0.0 if 'minimal_selling_price' is missing
                int(product.get('is_preorder', False))  # Use False if 'is_preorder' is missing
            ))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Data successfully migrated to {sqlite_db}")


# Example usage:
migrate_products_json_to_sqlite(output_file, '../storage/products.db')
