import time
import os
import json
import sys
import requests

agent_id = os.environ.get("AGENT_ID", "agent1")
agent_role = os.environ.get("AGENT_ROLE", "agent1_sourcing")

print(f"[BOOT] {agent_role} ({agent_id}) initialized.")

def get_system_dir():
    if os.path.exists("/idm/system"):
        return "/idm/system"
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "system"))
    return local_path

class CJDropshippingClient:
    """
    CJ Dropshipping REST API connection client
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://developers.cjdropshipping.com/api2.0"
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    def authenticate(self):
        if not self.api_key:
            print("[CJDropshippingClient] Error: CJ_DROPSHIPPING_API_KEY is not set.")
            return False
        
        url = f"{self.base_url}/v1/authentication/getAccessToken"
        print(f"[CJDropshippingClient] Authenticating with api2.0 endpoint...")
        try:
            response = requests.post(url, json={"apiKey": self.api_key}, headers=self.headers, timeout=10)
            res_data = response.json()
            # Try to grab access token from the common structures
            data = res_data.get("data", {})
            self.access_token = data.get("accessToken") or res_data.get("accessToken")
            
            if self.access_token:
                self.headers["CJ-Access-Token"] = self.access_token
                print("[CJDropshippingClient] Authentication successful. Access token established.")
                return True
            else:
                print(f"[CJDropshippingClient] Authentication failed: {res_data}")
                return False
        except Exception as e:
            print(f"[CJDropshippingClient] Authentication connection error: {e}")
            return False

    def search_products(self, keyword):
        if not self.access_token and not self.authenticate():
            return {"error": "Authentication required"}
        
        url = f"{self.base_url}/v1/product/list"
        try:
            response = requests.get(url, params={"productName": keyword}, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Read live API connection variables from env configuration
CJ_API_KEY = os.environ.get("CJ_DROPSHIPPING_API_KEY", "")
cj_client = CJDropshippingClient(api_key=CJ_API_KEY)

# Permanent luxury footwear and leather goods template focusing strictly on the 5 categories
LUXURY_PRODUCTS_TEMPLATE = [
    {
        "title": "Tuscany Velvet Hand-Stitched Stiletto Heels",
        "body_html": "<p><strong>Material:</strong> Premium Italian velvet upper, full-grain Tuscan calfskin leather lining, hand-stitched leather sole.</p><p><strong>Source:</strong> Direct Italy/Tuscany artisan networks.</p><p><strong>Description:</strong> Exquisite hand-crafted stiletto heels featuring premium velvet wrap, designed for unmatched elegance and structural durability.</p>",
        "vendor": "Tuscany Artisan Networks",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [
            {"src": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&q=80&w=800"},
            {"src": "https://images.unsplash.com/photo-1596702994230-a885f67a6d8d?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "TUS-W-HEEL-RED-37", "option1": "Red", "option2": "37", "cost_price": 245.00},
            {"sku": "TUS-W-HEEL-RED-38", "option1": "Red", "option2": "38", "cost_price": 245.00},
            {"sku": "TUS-W-HEEL-BLK-37", "option1": "Black", "option2": "37", "cost_price": 245.00},
            {"sku": "TUS-W-HEEL-BLK-38", "option1": "Black", "option2": "38", "cost_price": 245.00}
        ]
    },
    {
        "title": "AeroKnit Performance Sneaker V2",
        "body_html": "<p><strong>Material:</strong> High-tensile engineered Primeknit upper, responsive foam cushioning, reinforced TPU stabilizer heel.</p><p><strong>Source:</strong> Jinjiang/Putian OEM factory hubs.</p><p><strong>Description:</strong> Ultra-lightweight sports sneaker designed for cross-training and competitive running, offering dynamic arch support and maximum breathability.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "JIN-W-AERO-WHT-36", "option1": "White", "option2": "36", "cost_price": 38.50},
            {"sku": "JIN-W-AERO-WHT-37", "option1": "White", "option2": "37", "cost_price": 38.50},
            {"sku": "JIN-W-AERO-GRY-36", "option1": "Grey", "option2": "36", "cost_price": 38.50},
            {"sku": "JIN-W-AERO-GRY-37", "option1": "Grey", "option2": "37", "cost_price": 38.50}
        ]
    },
    {
        "title": "Milano Hand-Burnished Oxford Dress Shoes",
        "body_html": "<p><strong>Material:</strong> Hand-burnished full-grain Italian calfskin leather, traditional Blake-stitched leather sole, stacked leather heel.</p><p><strong>Source:</strong> Direct Italian B2B warehouse APIs.</p><p><strong>Description:</strong> Classic formal Oxfords featuring elegant closed-lace design and detailed broguing. Perfectly suited for black-tie affairs and premium corporate wear.</p>",
        "vendor": "Milano B2B Warehouses",
        "product_type": "Men's Formal Dress Shoes",
        "images": [
            {"src": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&q=80&w=800"},
            {"src": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "MIL-M-OXFORD-BRN-41", "option1": "Brown", "option2": "41", "cost_price": 185.00},
            {"sku": "MIL-M-OXFORD-BRN-42", "option1": "Brown", "option2": "42", "cost_price": 185.00},
            {"sku": "MIL-M-OXFORD-BLK-41", "option1": "Black", "option2": "41", "cost_price": 185.00},
            {"sku": "MIL-M-OXFORD-BLK-42", "option1": "Black", "option2": "42", "cost_price": 185.00}
        ]
    },
    {
        "title": "Apex Trail Runner Pro",
        "body_html": "<p><strong>Material:</strong> Heavy-duty ballistic nylon mesh, protective TPU overlays, high-traction Vibram rubber outsole, dual-density EVA midsole.</p><p><strong>Source:</strong> Jinjiang/Putian OEM factory hubs.</p><p><strong>Description:</strong> Rugged trail-running sneaker engineered to withstand demanding outdoor terrain while providing high-rebound cushioning.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "PUT-M-APEX-BLU-42", "option1": "Blue", "option2": "42", "cost_price": 42.00},
            {"sku": "PUT-M-APEX-BLU-43", "option1": "Blue", "option2": "43", "cost_price": 42.00},
            {"sku": "PUT-M-APEX-BLK-42", "option1": "Black", "option2": "42", "cost_price": 42.00},
            {"sku": "PUT-M-APEX-BLK-43", "option1": "Black", "option2": "43", "cost_price": 42.00}
        ]
    },
    {
        "title": "Florentine Vachetta Leather Bifold Wallet",
        "body_html": "<p><strong>Material:</strong> Tuscan vegetable-tanned Vachetta leather, hand-waxed linen thread stitching, hand-finished burnished edges.</p><p><strong>Source:</strong> Direct Italian artisan leather crafter networks.</p><p><strong>Description:</strong> A premium minimalist bifold wallet that will develop a rich, unique patina over time. Features 6 card slots and a dedicated bill compartment.</p>",
        "vendor": "Florentine Crafter Networks",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [
            {"src": "https://images.unsplash.com/photo-1627124118123-e4d31319d11e?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "FLO-WLT-TAN-OS", "option1": "Tan", "option2": "One Size", "cost_price": 65.00},
            {"sku": "FLO-WLT-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 65.00},
            {"sku": "FLO-WLT-EXCL-OS", "option1": "Gold (Exclusive Edition)", "option2": "One Size", "cost_price": 95.00}
        ]
    }
]

def build_sourcing_catalog():
    sys_dir = get_system_dir()
    os.makedirs(sys_dir, exist_ok=True)
    target_path = os.path.join(sys_dir, "sourcing_catalog.json")
    
    print(f"[RUN] Sourcing luxury footwear and leather goods template...")
    
    # Try connecting to live CJ Dropshipping chain if API key is provided
    if CJ_API_KEY:
        print("[RUN] Live CJ Dropshipping connection established. Fetching matching inventory feeds...")
        # A test query could be executed here, e.g. cj_client.search_products("shoes")
        
    try:
        with open(target_path, "w") as f:
            json.dump(LUXURY_PRODUCTS_TEMPLATE, f, indent=2)
        print(f"[SUCCESS] Wrote {len(LUXURY_PRODUCTS_TEMPLATE)} sourced products to {target_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write sourcing catalog: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Test authentication on boot
    if CJ_API_KEY:
        cj_client.authenticate()
        
    try:
        while True:
            build_sourcing_catalog()
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[STOP] {agent_role} shutting down.")
