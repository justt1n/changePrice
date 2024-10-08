import os

import requests
import json
from MigrateProductsData import migrate_products_json_to_sqlite

def fetch_product_list(output_file : str):
    # API base URL and headers
    base_url = "https://backend.gamivo.com/api/public/v1/products"
    headers = {
        "accept": "application/json",
        "Authorization": os.getenv('GAMIVO_API_KEY')
    }

    # Parameters for pagination
    offset = 0
    limit = 100
    batch_size = 1000  # Number of records to collect before writing to file
    all_products = []

    # JSON file to store the results

    # Open the file in append mode
    with open(output_file, 'w') as f:
        f.write('[\n')  # Start the JSON array

    # Fetch and write products in batches
    while True:
        # Request URL with offset and limit
        url = f"{base_url}?offset={offset}&limit={limit}"
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        # Extract the JSON data
        data = response.json()

        # If no more products are returned, break the loop
        if not data:
            break

        # Append the fetched products to the list
        all_products.extend(data)

        # Check if the batch size is reached
        if len(all_products) >= batch_size:
            # Write the current batch to the JSON file
            with open(output_file, 'a') as f:
                json.dump(all_products, f, indent=4)
                f.write(',\n')  # Separate batches by a comma in the JSON array

            # Reset the list to save memory
            all_products = []

        # Print status
        print(f"Fetched {len(data)} products (offset={offset})")

        # Increment offset for next page
        offset += limit

    # Write any remaining products (if less than batch_size)
    if all_products:
        with open(output_file, 'a') as f:
            json.dump(all_products, f, indent=4)
            f.write('\n')

    # Close the JSON array in the file
    with open(output_file, 'a') as f:
        f.write(']')

    # Print completion message
    print(f"Data fetching complete. Results saved in {output_file}")


def get_product_list():
    fetch_product_list(os.getenv('OUTPUT_FILE', '../storage/products.json'))
    migrate_products_json_to_sqlite(os.getenv('OUTPUT_FILE', '../storage/products.json'), os.getenv('SQLITE_DB',
                                                                                         '../storage/products.db'))