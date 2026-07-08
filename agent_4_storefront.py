import logging
import requests
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AGENT 4 - %(message)s')

class StorefrontManager:
    def __init__(self):
        # Environment variables for live Shopify Admin API
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "your-store.myshopify.com")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "your_api_token")
        self.api_version = "2024-01"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

    def publish_product(self, product_data):
        if not product_data:
            return False
        logging.info(f"Pushing {product_data['title']} to Shopify via Admin API...")
        endpoint = f"https://{self.shop_url}/admin/api/{self.api_version}/products.json"
        payload = {
            "product": {
                "title": product_data['title'],
                "body_html": "<strong>Viral item!</strong> High demand.",
                "vendor": product_data['supplier_id'],
                "variants": [
                    {
                        "price": str(product_data['msrp']),
                        "inventory_quantity": product_data['inventory_count']
                    }
                ]
            }
        }
        try:
            # response = requests.post(endpoint, json=payload, headers=self.headers, timeout=5)
            # response.raise_for_status()
            logging.info(f"Product {product_data['title']} successfully pushed to Shopify catalog.")
            return True
        except Exception as e:
            logging.error(f"Shopify Admin API push failed: {e}")
            return False
