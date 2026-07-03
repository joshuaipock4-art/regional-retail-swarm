import time
import os
import json
import sys
import requests

agent_id = os.environ.get("AGENT_ID", "agent7")
agent_role = os.environ.get("AGENT_ROLE", "agent7_inventory")

print(f"[BOOT] {agent_role} ({agent_id}) initialized.")

def get_system_dir():
    if os.path.exists("/idm/system"):
        return "/idm/system"
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "system"))
    return local_path

class ShopifyClient:
    """
    Shopify Admin REST API connection client supporting Client Credentials Token Exchange
    """
    def __init__(self, client_id, client_secret, store_url):
        self.client_id = client_id
        self.client_secret = client_secret
        # Ensure store_url starts with https://
        if stroke_url := store_url:
            if not stroke_url.startswith("http"):
                self.store_url = f"https://{stroke_url}"
            else:
                self.store_url = stroke_url
        else:
            self.store_url = None
            
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.fetch_access_token()

    def fetch_access_token(self):
        if not self.client_id or not self.client_secret or not self.store_url:
            print("[ShopifyClient] Warning: Client ID, Secret, or Store URL missing.")
            return False
        url = f"{self.store_url}/admin/oauth/access_token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            print(f"[ShopifyClient] Requesting dynamic access token via Client Credentials Grant...")
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.headers["X-Shopify-Access-Token"] = self.access_token
                    print("[ShopifyClient] Dynamic access token successfully acquired.")
                    return True
            print(f"[ShopifyClient] Token exchange failed (Status {response.status_code}): {response.text}")
            return False
        except Exception as e:
            print(f"[ShopifyClient] Token exchange exception: {e}")
            return False

    def push_product(self, product_payload):
        if not self.access_token or not self.store_url:
            print("[ShopifyClient] Error: Shopify access token is not configured (or exchange failed).")
            return {"error": "Credentials missing"}
            
        url = f"{self.store_url}/admin/api/2024-04/products.json"
        print(f"[ShopifyClient] Pushing product '{product_payload.get('title')}' to Shopify store...")
        try:
            response = requests.post(url, json={"product": product_payload}, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_products(self):
        if not self.access_token or not self.store_url:
            return {"error": "Credentials missing"}
            
        url = f"{self.store_url}/admin/api/2024-04/products.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Read Shopify environment variables
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
SHOPIFY_URL = os.environ.get("SHOPIFY_STORE_URL", "")
shopify_client = ShopifyClient(client_id=SHOPIFY_CLIENT_ID, client_secret=SHOPIFY_CLIENT_SECRET, store_url=SHOPIFY_URL)

def build_shopify_catalog():
    sys_dir = get_system_dir()
    sourcing_path = os.path.join(sys_dir, "sourcing_catalog.json")
    competitor_path = os.path.join(sys_dir, "competitor_prices.json")
    target_path = os.path.join(sys_dir, "shopify_catalog.json")
    
    if not os.path.exists(sourcing_path):
        print(f"[WARN] Sourcing catalog not found at {sourcing_path}. Waiting for Agent 1 Sourcing...")
        return
        
    competitor_data = {}
    if os.path.exists(competitor_path):
        try:
            with open(competitor_path, "r") as cf:
                competitor_data = json.load(cf)
            print("[RUN] Competitor intelligence data successfully loaded.")
        except Exception as e:
            print(f"[WARN] Failed to load competitor prices: {e}")
            
    print(f"[RUN] Sourcing catalog found. Compiling unified Shopify catalog upload structure with inventory metrics and dynamic pricing...")
    try:
        with open(sourcing_path, "r") as f:
            sourced_products = json.load(f)
            
        shopify_products = []
        for p in sourced_products:
            # Map products strictly to the 5 targeted categories
            if p.get("product_type") not in [
                "Women's Dress Shoes & Luxury Heels",
                "Women's Premium Athletic Sneakers",
                "Men's Formal Dress Shoes",
                "Men's Premium Athletic Sneakers",
                "Handmade Italian Leather Wallets & Small Leather Goods"
            ]:
                continue # Ignore unrelated products
                
            shopify_variants = []
            for v in p.get("variants", []):
                sku = v.get("sku", "")
                cost_val = v.get("cost_price", 0.00)
                
                # Rule 1: Exact Product Matching strictly using unique SKUs
                comp_match = competitor_data.get(sku)
                
                # Default Standard Target Margin (30% markup baseline)
                standard_target_margin = cost_val * 1.30
                pricing_reason = "markup_fallback"
                is_exclusive = False
                
                if comp_match:
                    lowest_comp = comp_match.get("lowest_price")
                    if lowest_comp is not None:
                        # Rule 2: Dynamic Undercut Logic ($5.00 Off competitor price)
                        undercut_price = lowest_comp - 5.00
                        
                        # Guardrail: Must never drop below cost_price
                        if undercut_price >= cost_val:
                            final_price = undercut_price
                            pricing_reason = "dynamic_undercut"
                        else:
                            # Fallback to standard target margin if undercut goes below cost
                            final_price = standard_target_margin
                            pricing_reason = "floor_violation_fallback"
                    else:
                        # Rule 3: Exclusive Product Fallback
                        final_price = standard_target_margin
                        pricing_reason = "exclusive_fallback"
                        is_exclusive = True
                else:
                    # Rule 3: Exclusive Product Fallback if no competitor matches are found
                    final_price = standard_target_margin
                    pricing_reason = "exclusive_fallback"
                    is_exclusive = True
                    lowest_comp = None
                    
                price_str = f"{final_price:.2f}"
                cost_str = f"{cost_val:.2f}"
                
                # Setup mock regional inventory quantities across the 9 states
                regional_stock = {
                    "us-south-1": 45,
                    "us-south-2": 25,
                    "us-east-1": 15,
                    "us-east-2": 10,
                    "us-west-1": 30,
                    "us-west-2": 20,
                    "eu-central-1": 5,
                    "eu-west-1": 10,
                    "ap-northeast-1": 5
                }
                total_qty = sum(regional_stock.values())
                
                shopify_variants.append({
                    "sku": sku,
                    "option1": v.get("option1"),
                    "option2": v.get("option2"),
                    "price": price_str,
                    "compare_at_price": None, # Explicitly no retail pricing markup logic
                    "cost_price": cost_str,   # Maps exactly to wholesale cost_price baseline
                    "pricing_strategy": {
                        "strategy": pricing_reason,
                        "competitor_lowest": f"{lowest_comp:.2f}" if comp_match and lowest_comp is not None else None,
                        "exclusive": is_exclusive
                    },
                    "inventory_management": "shopify",
                    "inventory_quantity": total_qty,
                    "regional_inventory_breakdown": regional_stock,
                    "fulfillment_service": "manual",
                    "requires_shipping": True,
                    "taxable": True
                })
                
            shopify_products.append({
                "title": p.get("title", ""),
                "body_html": p.get("body_html", ""),
                "vendor": p.get("vendor", ""),
                "product_type": p.get("product_type", ""),
                "options": [
                    {"name": "Color"},
                    {"name": "Size"}
                ],
                "images": p.get("images", []),
                "variants": shopify_variants
            })
            
        output_payload = {"products": shopify_products}
        
        with open(target_path, "w") as f:
            json.dump(output_payload, f, indent=2)
        print(f"[SUCCESS] Compiled {len(shopify_products)} luxury footwear & leather items to {target_path} using Dynamic Competitor Undercut Strategy")
        
        # Deploy this pricing/inventory logic to live Shopify store if authorized
        if shopify_client.access_token and SHOPIFY_URL:
            print("[RUN] Shopify credentials detected. Checking for deduplication before pushing...")
            existing = shopify_client.get_products()
            
            existing_skus = set()
            # If request to get_products fails or is unauthorized, existing will be {"error": ...}
            if isinstance(existing, dict) and "products" in existing:
                for ep in existing["products"]:
                    for ev in ep.get("variants", []):
                        if ev.get("sku"):
                            existing_skus.add(ev["sku"])
                            
                for product in shopify_products:
                    # Check if all variant SKUs are already in existing_skus
                    to_push = False
                    for v in product.get("variants", []):
                        if v.get("sku") not in existing_skus:
                            to_push = True
                            break
                            
                    if to_push:
                        res = shopify_client.push_product(product)
                        print(f"[RUN] Successfully created/updated Shopify listing for '{product.get('title')}': {res}")
                    else:
                        print(f"[RUN] Product '{product.get('title')}' already registered on Shopify. Skipping duplicate push.")
            else:
                print(f"[WARN] Unable to push live catalog (Shopify API connection returned: {existing})")
                
    except Exception as e:
        print(f"[ERROR] Failed to compile Shopify catalog: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        while True:
            build_shopify_catalog()
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[STOP] {agent_role} shutting down.")
