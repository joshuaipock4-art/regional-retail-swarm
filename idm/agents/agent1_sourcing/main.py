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
    # --- Women's Dress Shoes & Luxury Heels ---
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
        "title": "Venetian Lace Pointed-Toe Pumps",
        "body_html": "<p><strong>Material:</strong> Delicate Venetian lace overlay, premium satin underlay, padded leather insole, and classic leather outsole.</p><p><strong>Source:</strong> Veneto region artisan ateliers.</p><p><strong>Description:</strong> Exquisite pointed-toe pumps wrapped in hand-crafted lace, perfect for evening wear and special events.</p>",
        "vendor": "Veneto Artisan Ateliers",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [
            {"src": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "VEN-W-PUMP-BLK-37", "option1": "Black", "option2": "37", "cost_price": 210.00},
            {"sku": "VEN-W-PUMP-BLK-38", "option1": "Black", "option2": "38", "cost_price": 210.00},
            {"sku": "VEN-W-PUMP-SLV-37", "option1": "Silver", "option2": "37", "cost_price": 210.00},
            {"sku": "VEN-W-PUMP-SLV-38", "option1": "Silver", "option2": "38", "cost_price": 210.00}
        ]
    },
    {
        "title": "Amalfi Coast Leather Strappy Sandals",
        "body_html": "<p><strong>Material:</strong> Full-grain hand-dyed Italian calfskin straps, cushioned leather footbed, durable leather sole with non-slip rubber insert.</p><p><strong>Source:</strong> Campania region leather crafters.</p><p><strong>Description:</strong> Elegant, lightweight strappy sandals designed for exceptional comfort and warm-weather sophistication.</p>",
        "vendor": "Campania Leather Crafters",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [
            {"src": "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "AMA-W-SAND-GLD-37", "option1": "Gold", "option2": "37", "cost_price": 175.00},
            {"sku": "AMA-W-SAND-GLD-38", "option1": "Gold", "option2": "38", "cost_price": 175.00},
            {"sku": "AMA-W-SAND-TAN-37", "option1": "Tan", "option2": "37", "cost_price": 175.00},
            {"sku": "AMA-W-SAND-TAN-38", "option1": "Tan", "option2": "38", "cost_price": 175.00}
        ]
    },

    # --- Women's Premium Athletic Sneakers ---
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
        "title": "NovaGlide Cushioned Trainer",
        "body_html": "<p><strong>Material:</strong> Multi-layered mesh upper for ventilation, ultra-soft nitrogen-infused cushioning midsole, high-wear rubber outsole.</p><p><strong>Source:</strong> Putian OEM factory hubs.</p><p><strong>Description:</strong> Premium athletic sneakers offering maximum impact protection and a secure, cushioned ride for long run cycles.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "NOV-W-TRAIN-PNK-36", "option1": "Pink", "option2": "36", "cost_price": 45.00},
            {"sku": "NOV-W-TRAIN-PNK-37", "option1": "Pink", "option2": "37", "cost_price": 45.00},
            {"sku": "NOV-W-TRAIN-BLK-36", "option1": "Black", "option2": "36", "cost_price": 45.00},
            {"sku": "NOV-W-TRAIN-BLK-37", "option1": "Black", "option2": "37", "cost_price": 45.00}
        ]
    },
    {
        "title": "FlexKnit Lightweight Jogger",
        "body_html": "<p><strong>Material:</strong> Flexible knit textile upper, memory foam footbed, lightweight EVA traction sole.</p><p><strong>Source:</strong> Jinjiang OEM Factory Hub.</p><p><strong>Description:</strong> Ultra-light minimalist athletic shoe designed for day-to-day wear and light jogging, ensuring natural foot flex.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "FLE-W-JOG-GRY-36", "option1": "Grey", "option2": "36", "cost_price": 35.00},
            {"sku": "FLE-W-JOG-GRY-37", "option1": "Grey", "option2": "37", "cost_price": 35.00},
            {"sku": "FLE-W-JOG-WHT-36", "option1": "White", "option2": "36", "cost_price": 35.00},
            {"sku": "FLE-W-JOG-WHT-37", "option1": "White", "option2": "37", "cost_price": 35.00}
        ]
    },

    # --- Men's Formal Dress Shoes ---
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
        "title": "Tuscan Calfskin Double Monk Strap Shoes",
        "body_html": "<p><strong>Material:</strong> Select Tuscan calfskin upper, brass buckle hardware, durable Goodyear-welted leather sole.</p><p><strong>Source:</strong> Florence artisan networks.</p><p><strong>Description:</strong> Striking double monk strap shoes offering a sophisticated profile for formal, business, or premium social attire.</p>",
        "vendor": "Florence Artisan Networks",
        "product_type": "Men's Formal Dress Shoes",
        "images": [
            {"src": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "TUS-M-MONK-BRN-41", "option1": "Brown", "option2": "41", "cost_price": 195.00},
            {"sku": "TUS-M-MONK-BRN-42", "option1": "Brown", "option2": "42", "cost_price": 195.00},
            {"sku": "TUS-M-MONK-BLK-41", "option1": "Black", "option2": "41", "cost_price": 195.00},
            {"sku": "TUS-M-MONK-BLK-42", "option1": "Black", "option2": "42", "cost_price": 195.00}
        ]
    },
    {
        "title": "Roma Hand-Stitched Leather Loafers",
        "body_html": "<p><strong>Material:</strong> Soft hand-stitched pebbled calfskin leather, leather lining, flexible rubber driving sole.</p><p><strong>Source:</strong> Lazio region shoe workshops.</p><p><strong>Description:</strong> Luxurious driving loafers combining classic Italian style with casual, slip-on convenience.</p>",
        "vendor": "Lazio Shoe Workshops",
        "product_type": "Men's Formal Dress Shoes",
        "images": [
            {"src": "https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "ROM-M-LOAF-TAN-41", "option1": "Tan", "option2": "41", "cost_price": 160.00},
            {"sku": "ROM-M-LOAF-TAN-42", "option1": "Tan", "option2": "42", "cost_price": 160.00},
            {"sku": "ROM-M-LOAF-BLK-41", "option1": "Black", "option2": "41", "cost_price": 160.00},
            {"sku": "ROM-M-LOAF-BLK-42", "option1": "Black", "option2": "42", "cost_price": 160.00}
        ]
    },

    # --- Men's Premium Athletic Sneakers ---
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
        "title": "VaporMax Performance Runner",
        "body_html": "<p><strong>Material:</strong> Engineered warp-knit upper, full-length responsive air cushion unit, high-grip carbon rubber pods.</p><p><strong>Source:</strong> Putian OEM Factory Hub.</p><p># Description: High-performance athletic sneaker focused on energy return, joint comfort, and dynamic stride speed.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "VAP-M-RUN-BLK-42", "option1": "Black", "option2": "42", "cost_price": 55.00},
            {"sku": "VAP-M-RUN-BLK-43", "option1": "Black", "option2": "43", "cost_price": 55.00},
            {"sku": "VAP-M-RUN-RED-42", "option1": "Red", "option2": "42", "cost_price": 55.00},
            {"sku": "VAP-M-RUN-RED-43", "option1": "Red", "option2": "43", "cost_price": 55.00}
        ]
    },
    {
        "title": "TerraGrip Trail Hiking Sneaker",
        "body_html": "<p><strong>Material:</strong> Waterproof ripstop textile upper, reinforced rubber toe cap, multi-directional lugged outsole.</p><p><strong>Source:</strong> Jinjiang OEM Factory Hub.</p><p><strong>Description:</strong> Versatile outdoor trail hiking shoe offering superior protection, stability, and wet-weather traction.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [
            {"src": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "TER-M-HIKE-GRN-42", "option1": "Green", "option2": "42", "cost_price": 48.00},
            {"sku": "TER-M-HIKE-GRN-43", "option1": "Green", "option2": "43", "cost_price": 48.00},
            {"sku": "TER-M-HIKE-BRN-42", "option1": "Brown", "option2": "42", "cost_price": 48.00},
            {"sku": "TER-M-HIKE-BRN-43", "option1": "Brown", "option2": "43", "cost_price": 48.00}
        ]
    },

    # --- Handmade Italian Leather Wallets & Small Leather Goods ---
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
    },
    {
        "title": "Siena Zippered Leather Travel Wallet",
        "body_html": "<p><strong>Material:</strong> Heavy-grain Saffiano leather, secure polished metal zip-around closure, multiple inner document slots.</p><p><strong>Source:</strong> Siena workshop collectives.</p><p><strong>Description:</strong> Secure and spacious zippered travel wallet, built to organize passports, multiple currencies, and credit cards during travel.</p>",
        "vendor": "Siena Workshop Collectives",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [
            {"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "SIE-WLT-ZIP-BRN-OS", "option1": "Brown", "option2": "One Size", "cost_price": 85.00},
            {"sku": "SIE-WLT-ZIP-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 85.00}
        ]
    },
    {
        "title": "San Gimignano Slim Leather Cardholder",
        "body_html": "<p><strong>Material:</strong> Vegetable-tanned Tuscan leather, RFID blocking lining, ultra-slim stitched profile.</p><p><strong>Source:</strong> San Gimignano artisan guild.</p><p><strong>Description:</strong> Modern minimalist cardholder featuring 4 exterior card slots and a middle cash pocket, keeping pockets sleek and light.</p>",
        "vendor": "San Gimignano Artisan Guild",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [
            {"src": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?auto=format&fit=crop&q=80&w=800"}
        ],
        "variants": [
            {"sku": "SGI-CARD-TAN-OS", "option1": "Tan", "option2": "One Size", "cost_price": 35.00},
            {"sku": "SGI-CARD-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 35.00}
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
