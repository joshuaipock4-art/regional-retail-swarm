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

    def search_products(self, keyword, size=3):
        if not self.access_token and not self.authenticate():
            return {"error": "Authentication required"}
        
        url = f"{self.base_url}/v1/product/listV2"
        try:
            response = requests.get(url, params={"keyWord": keyword, "page": 1, "size": size}, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_variants(self, pid):
        if not self.access_token and not self.authenticate():
            return {"error": "Authentication required"}
        
        url = f"{self.base_url}/v1/product/variant/query"
        try:
            response = requests.get(url, params={"pid": pid}, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Read live API connection variables from env configuration
CJ_API_KEY = os.environ.get("CJ_DROPSHIPPING_API_KEY", "")
cj_client = CJDropshippingClient(api_key=CJ_API_KEY)

# Permanent luxury footwear and leather goods template focusing strictly on the 5 categories
LUXURY_PRODUCTS_TEMPLATE = [
    # ==========================================
    # --- WOMEN'S DRESS SHOES & LUXURY HEELS (5 Items) ---
    # ==========================================
    {
        "title": "Tuscany Crystal-Embellished Satin Stiletto Heels",
        "body_html": "<p><strong>Material:</strong> Premium Italian satin wrap, crystal-encrusted strap details, full-grain calfskin leather lining, hand-stitched leather sole.</p><p><strong>Description:</strong> Ultra-premium satin stiletto heels adorned with sparkling crystal trim, offering a stunning silhouette for luxury formal occasions.</p>",
        "vendor": "Tuscany Artisan Networks",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [{"src": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"TUS-W-HEEL-SLV-{sz}", "option1": "Silver", "option2": str(sz), "cost_price": 285.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "Venetian Lace Pointed-Toe Pumps",
        "body_html": "<p><strong>Material:</strong> Delicate Venetian lace overlay, premium satin underlay, padded leather insole, and classic leather outsole.</p><p><strong>Description:</strong> Exquisite pointed-toe pumps wrapped in hand-crafted lace, perfect for evening wear and special events.</p>",
        "vendor": "Veneto Artisan Ateliers",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [{"src": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"VEN-W-PUMP-BLK-{sz}", "option1": "Black", "option2": str(sz), "cost_price": 210.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "Amalfi Coast Leather Strappy Sandals",
        "body_html": "<p><strong>Material:</strong> Full-grain hand-dyed Italian calfskin straps, cushioned leather footbed, durable leather sole with non-slip rubber insert.</p><p><strong>Description:</strong> Elegant, lightweight strappy sandals designed for exceptional comfort and warm-weather sophistication.</p>",
        "vendor": "Campania Leather Crafters",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [{"src": "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"AMA-W-SAND-GLD-{sz}", "option1": "Gold", "option2": str(sz), "cost_price": 175.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "Florence Suede Ankle Strap Block Heels",
        "body_html": "<p><strong>Material:</strong> Soft Italian goat suede upper, block heel design, calfskin leather lining, adjustable ankle strap with brass buckle.</p><p><strong>Description:</strong> Chic ankle strap block heels combining daily wear stability with high-end Tuscan styling.</p>",
        "vendor": "Florence Artisan Networks",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [{"src": "https://images.unsplash.com/photo-1596702994230-a885f67a6d8d?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"FLO-W-BLOCK-TAN-{sz}", "option1": "Tan", "option2": str(sz), "cost_price": 190.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "Milan Velvet Pointed-Toe D'Orsay Flats",
        "body_html": "<p><strong>Material:</strong> Luxurious silk velvet upper, D'Orsay cut pattern, breathable leather lining, cushioned leather footbed.</p><p><strong>Description:</strong> Elegant slip-on flats in rich velvet, presenting a perfect blend of high-fashion refinement and casual comfort.</p>",
        "vendor": "Milano B2B Warehouses",
        "product_type": "Women's Dress Shoes & Luxury Heels",
        "images": [{"src": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"MIL-W-FLAT-BLK-{sz}", "option1": "Black", "option2": str(sz), "cost_price": 155.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },

    # ==========================================
    # --- WOMEN'S PREMIUM ATHLETIC SNEAKERS (5 Items) ---
    # ==========================================
    {
        "title": "AeroKnit Performance Sneaker V2 (Women)",
        "body_html": "<p><strong>Material:</strong> High-tensile engineered Primeknit upper, responsive foam cushioning, reinforced TPU stabilizer heel.</p><p><strong>Description:</strong> Ultra-lightweight sports sneaker designed for running and cross-training, offering dynamic arch support.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"JIN-W-AERO-WHT-{sz}", "option1": "White", "option2": str(sz), "cost_price": 38.50} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "NovaGlide Cushioned Trainer (Women)",
        "body_html": "<p><strong>Material:</strong> Multi-layered mesh upper for ventilation, ultra-soft nitrogen-infused cushioning midsole, high-wear rubber outsole.</p><p><strong>Description:</strong> Premium athletic sneakers offering maximum impact protection and a secure, cushioned ride.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"NOV-W-TRAIN-PNK-{sz}", "option1": "Pink", "option2": str(sz), "cost_price": 45.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "FlexKnit Lightweight Jogger (Women)",
        "body_html": "<p><strong>Material:</strong> Flexible knit textile upper, memory foam footbed, lightweight EVA traction sole.</p><p><strong>Description:</strong> Ultra-light minimalist athletic shoe designed for day-to-day wear and light jogging.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"FLE-W-JOG-GRY-{sz}", "option1": "Grey", "option2": str(sz), "cost_price": 35.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "Apex Trail Runner Pro (Women)",
        "body_html": "<p><strong>Material:</strong> Heavy-duty ballistic nylon mesh, protective TPU overlays, high-traction Vibram rubber outsole, dual-density EVA midsole.</p><p><strong>Description:</strong> Rugged trail-running sneaker engineered to withstand demanding outdoor terrain.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"PUT-W-APEX-BLU-{sz}", "option1": "Blue", "option2": str(sz), "cost_price": 42.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },
    {
        "title": "VaporMax Performance Runner (Women)",
        "body_html": "<p><strong>Material:</strong> Engineered warp-knit upper, full-length responsive air cushion unit, high-grip carbon rubber pods.</p><p><strong>Description:</strong> High-performance athletic sneaker focused on energy return, joint comfort, and dynamic speed.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Women's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"VAP-W-RUN-RED-{sz}", "option1": "Red", "option2": str(sz), "cost_price": 55.00} for sz in [35, 36, 37, 38, 39, 40, 41]
        ]
    },

    # ==========================================
    # --- MEN'S FORMAL DRESS SHOES (5 Items) ---
    # ==========================================
    {
        "title": "Milano Hand-Burnished Oxford Dress Shoes",
        "body_html": "<p><strong>Material:</strong> Hand-burnished full-grain Italian calfskin leather, traditional Blake-stitched leather sole, stacked leather heel.</p><p><strong>Description:</strong> Classic formal Oxfords featuring elegant closed-lace design and detailed broguing. Perfectly suited for black-tie affairs.</p>",
        "vendor": "Milano B2B Warehouses",
        "product_type": "Men's Formal Dress Shoes",
        "images": [{"src": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"MIL-M-OXFORD-BRN-{sz}", "option1": "Brown", "option2": str(sz), "cost_price": 185.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "Tuscan Calfskin Double Monk Strap Shoes",
        "body_html": "<p><strong>Material:</strong> Select Tuscan calfskin upper, brass buckle hardware, durable Goodyear-welted leather sole.</p><p><strong>Description:</strong> Striking double monk strap shoes offering a sophisticated profile for formal, business, or premium social attire.</p>",
        "vendor": "Florence Artisan Networks",
        "product_type": "Men's Formal Dress Shoes",
        "images": [{"src": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"TUS-M-MONK-BRN-{sz}", "option1": "Brown", "option2": str(sz), "cost_price": 195.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "Roma Hand-Stitched Leather Loafers",
        "body_html": "<p><strong>Material:</strong> Soft hand-stitched pebbled calfskin leather, leather lining, flexible rubber driving sole.</p><p><strong>Description:</strong> Luxurious driving loafers combining classic Italian style with casual, slip-on convenience.</p>",
        "vendor": "Lazio Shoe Workshops",
        "product_type": "Men's Formal Dress Shoes",
        "images": [{"src": "https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"ROM-M-LOAF-TAN-{sz}", "option1": "Tan", "option2": str(sz), "cost_price": 160.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "Venetian Patent Leather Tuxedo Shoes",
        "body_html": "<p><strong>Material:</strong> High-gloss Italian patent leather upper, satin ribbon laces, padded calfskin lining, dress leather sole.</p><p><strong>Description:</strong> The ultimate dress shoe for formal galas and weddings, built for absolute luxury and brilliant luster.</p>",
        "vendor": "Veneto Artisan Ateliers",
        "product_type": "Men's Formal Dress Shoes",
        "images": [{"src": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"VEN-M-TUX-BLK-{sz}", "option1": "Black", "option2": str(sz), "cost_price": 200.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "Florence Wingtip Brogue Derby Shoes",
        "body_html": "<p><strong>Material:</strong> Antiqued calfskin leather upper, detailed wingtip broguing, Goodyear welted double leather sole.</p><p><strong>Description:</strong> Full brogue Derby shoes showcasing traditional Florentine leather staining and heavy-duty welted soles.</p>",
        "vendor": "Florence Artisan Networks",
        "product_type": "Men's Formal Dress Shoes",
        "images": [{"src": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"FLO-M-BROGUE-BRN-{sz}", "option1": "Brown", "option2": str(sz), "cost_price": 190.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },

    # ==========================================
    # --- MEN'S PREMIUM ATHLETIC SNEAKERS (5 Items) ---
    # ==========================================
    {
        "title": "Apex Trail Runner Pro (Men)",
        "body_html": "<p><strong>Material:</strong> Heavy-duty ballistic nylon mesh, protective TPU overlays, high-traction Vibram rubber outsole, dual-density EVA midsole.</p><p><strong>Description:</strong> Rugged trail-running sneaker engineered to withstand demanding outdoor terrain.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"PUT-M-APEX-BLU-{sz}", "option1": "Blue", "option2": str(sz), "cost_price": 42.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "VaporMax Performance Runner (Men)",
        "body_html": "<p><strong>Material:</strong> Engineered warp-knit upper, full-length responsive air cushion unit, high-grip carbon rubber pods.</p><p><strong>Description:</strong> High-performance athletic sneaker focused on energy return, joint comfort, and speed.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"VAP-M-RUN-BLK-{sz}", "option1": "Black", "option2": str(sz), "cost_price": 55.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "TerraGrip Trail Hiking Sneaker",
        "body_html": "<p><strong>Material:</strong> Waterproof ripstop textile upper, reinforced rubber toe cap, multi-directional lugged outsole.</p><p><strong>Description:</strong> Versatile outdoor trail hiking shoe offering superior protection, stability, and wet-weather traction.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"TER-M-HIKE-GRN-{sz}", "option1": "Green", "option2": str(sz), "cost_price": 48.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "NovaGlide Carbon Fiber Racer (Men)",
        "body_html": "<p><strong>Material:</strong> Monofilament carbon fiber mesh upper, dynamic full-length carbon flight plate, super-critical foam cushioning.</p><p><strong>Description:</strong> Elite marathon racing shoes built for speed, weight minimization, and maximum energy response.</p>",
        "vendor": "Putian OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"NOV-M-CARBON-WHT-{sz}", "option1": "White", "option2": str(sz), "cost_price": 95.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },
    {
        "title": "FlexKnit Lightweight Trainer (Men)",
        "body_html": "<p><strong>Material:</strong> Flexible knit textile upper, memory foam footbed, lightweight EVA traction sole.</p><p><strong>Description:</strong> Lightweight athletic cross-trainer shoe designed for daily workouts and road running comfort.</p>",
        "vendor": "Jinjiang OEM Factory Hub",
        "product_type": "Men's Premium Athletic Sneakers",
        "images": [{"src": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": f"FLE-M-TRAIN-GRY-{sz}", "option1": "Grey", "option2": str(sz), "cost_price": 35.00} for sz in [40, 41, 42, 43, 44, 45]
        ]
    },

    # ==========================================
    # --- HANDMADE ITALIAN LEATHER WALLETS & ACCESSORIES (3 Items) ---
    # ==========================================
    {
        "title": "Florentine Vachetta Leather Bifold Wallet",
        "body_html": "<p><strong>Material:</strong> Tuscan vegetable-tanned Vachetta leather, hand-waxed linen thread stitching, hand-finished burnished edges.</p><p><strong>Description:</strong> A premium minimalist bifold wallet that will develop a rich, unique patina over time. Features 6 card slots.</p>",
        "vendor": "Florentine Crafter Networks",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [{"src": "https://images.unsplash.com/photo-1627124118123-e4d31319d11e?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "FLO-WLT-TAN-OS", "option1": "Tan", "option2": "One Size", "cost_price": 65.00},
            {"sku": "FLO-WLT-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 65.00}
        ]
    },
    {
        "title": "Siena Zippered Leather Travel Wallet",
        "body_html": "<p><strong>Material:</strong> Heavy-grain Saffiano leather, secure polished metal zip-around closure, multiple inner document slots.</p><p><strong>Description:</strong> Secure and spacious zippered travel wallet, built to organize passports, multiple currencies, and credit cards during travel.</p>",
        "vendor": "Siena Workshop Collectives",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "SIE-WLT-ZIP-BRN-OS", "option1": "Brown", "option2": "One Size", "cost_price": 85.00},
            {"sku": "SIE-WLT-ZIP-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 85.00}
        ]
    },
    {
        "title": "San Gimignano Slim Leather Cardholder",
        "body_html": "<p><strong>Material:</strong> Vegetable-tanned Tuscan leather, RFID blocking lining, ultra-slim stitched profile.</p><p><strong>Description:</strong> Modern minimalist cardholder featuring 4 exterior card slots and a middle cash pocket, keeping pockets sleek and light.</p>",
        "vendor": "San Gimignano Artisan Guild",
        "product_type": "Handmade Italian Leather Wallets & Small Leather Goods",
        "images": [{"src": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "SGI-CARD-TAN-OS", "option1": "Tan", "option2": "One Size", "cost_price": 35.00},
            {"sku": "SGI-CARD-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 35.00}
        ]
    },
    # ==========================================
    # --- HANDMADE ITALIAN LEATHER PURSES & HANDBAGS (5 Items) ---
    # ==========================================
    {
        "title": "Florence Calfskin Classica Handbag",
        "body_html": "<p><strong>Material:</strong> Full-grain hand-burnished Tuscan calfskin leather, structured carry handle, detachable shoulder strap, soft lambskin lining.</p><p><strong>Description:</strong> A timeless luxury handbag showcasing classical Florentine leather craftsmanship and elegant structured carry handle.</p>",
        "vendor": "Florence Artisan Networks",
        "product_type": "Handmade Italian Leather Purses & Handbags",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "FLO-PURSE-BRN-OS", "option1": "Sienna Brown", "option2": "One Size", "cost_price": 350.00},
            {"sku": "FLO-PURSE-BLK-OS", "option1": "Midnight Black", "option2": "One Size", "cost_price": 350.00},
            {"sku": "FLO-PURSE-TAN-OS", "option1": "Tuscan Tan", "option2": "One Size", "cost_price": 350.00}
        ]
    },
    {
        "title": "Siena Woven Leather Tote Bag",
        "body_html": "<p><strong>Material:</strong> Hand-woven strips of premium Saffiano calfskin, spacious open compartment, interior zip pocket.</p><p><strong>Description:</strong> Large luxury tote featuring beautiful hand-woven panels and highly durable calfskin, perfect for daily business or travel.</p>",
        "vendor": "Siena Workshop Collectives",
        "product_type": "Handmade Italian Leather Purses & Handbags",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "SIE-TOTE-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 290.00},
            {"sku": "SIE-TOTE-BRN-OS", "option1": "Tan Brown", "option2": "One Size", "cost_price": 290.00}
        ]
    },
    {
        "title": "Venetian Patent Leather Shoulder Bag",
        "body_html": "<p><strong>Material:</strong> High-gloss patent leather upper, polished gold-tone metal chain shoulder strap, secure interlocking clasp.</p><p><strong>Description:</strong> Elegant Venetian evening shoulder bag with a brilliant patent finish and iconic gold-tone hardware detail.</p>",
        "vendor": "Veneto Artisan Ateliers",
        "product_type": "Handmade Italian Leather Purses & Handbags",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "VEN-BAG-RED-OS", "option1": "Ruby Red", "option2": "One Size", "cost_price": 310.00},
            {"sku": "VEN-BAG-BLK-OS", "option1": "Midnight Black", "option2": "One Size", "cost_price": 310.00}
        ]
    },
    {
        "title": "Amalfi Coast Canvas Travel Duffel",
        "body_html": "<p><strong>Material:</strong> Heavyweight waterproof cotton canvas, full-grain leather base and trim support, heavy duty brass zippers.</p><p><strong>Description:</strong> Lightweight yet rugged weekend travel bag designed for coastal excursions and elegant getaways.</p>",
        "vendor": "Campania Leather Crafters",
        "product_type": "Handmade Italian Leather Purses & Handbags",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "AMA-DUFFEL-BEG-OS", "option1": "Beige", "option2": "One Size", "cost_price": 220.00},
            {"sku": "AMA-DUFFEL-OLV-OS", "option1": "Olive", "option2": "One Size", "cost_price": 220.00}
        ]
    },
    {
        "title": "Roma Hand-Stitched Leather Envelope Clutch",
        "body_html": "<p><strong>Material:</strong> Soft hand-stitched nappa calfskin, envelope flap closure, magnetic button clasp, interior card slots.</p><p><strong>Description:</strong> Sleek and minimalist envelope clutch bag designed for night events, formal dinners, and wedding parties.</p>",
        "vendor": "Lazio Shoe Workshops",
        "product_type": "Handmade Italian Leather Purses & Handbags",
        "images": [{"src": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&q=80&w=800"}],
        "variants": [
            {"sku": "ROM-CLUTCH-GLD-OS", "option1": "Champagne Gold", "option2": "One Size", "cost_price": 180.00},
            {"sku": "ROM-CLUTCH-SLV-OS", "option1": "Silver", "option2": "One Size", "cost_price": 180.00},
            {"sku": "ROM-CLUTCH-BLK-OS", "option1": "Black", "option2": "One Size", "cost_price": 180.00}
        ]
    }
]

def build_sourcing_catalog():
    sys_dir = get_system_dir()
    os.makedirs(sys_dir, exist_ok=True)
    target_path = os.path.join(sys_dir, "sourcing_catalog.json")
    
    print(f"[RUN] Sourcing luxury footwear and leather goods...")
    
    fetched_products = []
    
    # Try connecting to live CJ Dropshipping chain if API key is provided
    if CJ_API_KEY and cj_client.authenticate():
        print("[RUN] Live CJ Dropshipping connection established. Fetching matching inventory feeds...")
        
        categories = [
            {"type": "Women's Dress Shoes & Luxury Heels", "keyword": "luxury stiletto heels"},
            {"type": "Women's Premium Athletic Sneakers", "keyword": "women premium athletic sneakers"},
            {"type": "Men's Formal Dress Shoes", "keyword": "men formal dress shoes oxford"},
            {"type": "Men's Premium Athletic Sneakers", "keyword": "men premium athletic sneakers running"},
            {"type": "Handmade Italian Leather Wallets & Small Leather Goods", "keyword": "handmade leather wallet bifold"},
            {"type": "Handmade Italian Leather Purses & Handbags", "keyword": "handmade leather purse handbag"}
        ]
        
        for cat in categories:
            print(f"[RUN] Fetching CJ products for keyword: '{cat['keyword']}'...")
            search_res = cj_client.search_products(cat["keyword"], size=3)
            
            list_data = None
            if isinstance(search_res, dict):
                result_obj = search_res.get("result") or search_res.get("data")
                if isinstance(result_obj, dict):
                    list_data = result_obj.get("list")
            
            if list_data and isinstance(list_data, list):
                for p in list_data:
                    pid = p.get("productId")
                    title = p.get("productNameEn") or p.get("productName")
                    image_url = p.get("productImage")
                    product_sku = p.get("productSku")
                    
                    if not pid or not title:
                        continue
                        
                    print(f"[RUN] Fetching variants for CJ Product ID: {pid} ('{title}')")
                    var_res = cj_client.get_variants(pid)
                    
                    variants_list = None
                    if isinstance(var_res, dict):
                        variants_list = var_res.get("result") or var_res.get("data")
                        
                    shopify_variants = []
                    if variants_list and isinstance(variants_list, list):
                        for v in variants_list:
                            v_sku = v.get("variantSku") or f"{product_sku}-{v.get('productId')}"
                            cost = float(v.get("totalPrice") or 10.00)
                            
                            variant_key = v.get("variantKey") or v.get("variantNameEn") or ""
                            key_parts = variant_key.split("-")
                            opt1 = key_parts[0] if len(key_parts) > 0 and key_parts[0] else "Default Color"
                            opt2 = key_parts[1] if len(key_parts) > 1 and key_parts[1] else "One Size"
                            
                            shopify_variants.append({
                                "sku": v_sku,
                                "option1": opt1,
                                "option2": opt2,
                                "cost_price": cost
                            })
                            
                    if not shopify_variants:
                        shopify_variants.append({
                            "sku": product_sku or f"CJ-MOCK-{pid}",
                            "option1": "Default Color",
                            "option2": "One Size",
                            "cost_price": 45.00
                        })
                        
                    fetched_products.append({
                        "title": title,
                        "body_html": f"<p>Sourced dynamically from CJ Dropshipping (Product ID: {pid}).</p>",
                        "vendor": "CJ Dropshipping",
                        "product_type": cat["type"],
                        "images": [{"src": image_url}] if image_url else [],
                        "variants": shopify_variants
                    })
            else:
                print(f"[WARN] No CJ products found for keyword: '{cat['keyword']}' (Response: {search_res})")
                
    if len(fetched_products) > 0:
        products_payload = fetched_products
        print(f"[SUCCESS] Successfully retrieved {len(products_payload)} live products from CJ Dropshipping API.")
    else:
        products_payload = LUXURY_PRODUCTS_TEMPLATE
        print(f"[WARN] Live CJ Dropshipping fetch returned no items. Falling back to the {len(products_payload)} built-in templates.")
        
    try:
        with open(target_path, "w") as f:
            json.dump(products_payload, f, indent=2)
        print(f"[SUCCESS] Wrote sourcing catalog to {target_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write sourcing catalog: {e}", file=sys.stderr)

if __name__ == "__main__":
    if CJ_API_KEY:
        cj_client.authenticate()
        
    try:
        while True:
            build_sourcing_catalog()
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[STOP] {agent_role} shutting down.")
