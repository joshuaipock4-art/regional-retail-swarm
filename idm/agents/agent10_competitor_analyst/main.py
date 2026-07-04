import time
import os
import json
import sys

agent_id = os.environ.get("AGENT_ID", "agent10")
agent_role = os.environ.get("AGENT_ROLE", "agent10_competitor_analyst")

print(f"[BOOT] {agent_role} ({agent_id}) initialized.")

def get_system_dir():
    if os.path.exists("/idm/system"):
        return "/idm/system"
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "system"))
    return local_path

def load_sourcing_costs():
    sys_dir = get_system_dir()
    sourcing_path = os.path.join(sys_dir, "sourcing_catalog.json")
    costs = {}
    if os.path.exists(sourcing_path):
        try:
            with open(sourcing_path, "r") as sf:
                products = json.load(sf)
                for p in products:
                    for v in p.get("variants", []):
                        sku = v.get("sku")
                        cost = v.get("cost_price")
                        if sku and cost is not None:
                            costs[sku] = cost
        except Exception as e:
            print(f"[agent10_competitor_analyst] Error loading sourcing catalog: {e}", file=sys.stderr)
    return costs

# Mock competitor pricing database matching our catalog SKUs exactly
MOCK_COMPETITORS_DATA = {
    # Tuscany Velvet Stiletto Heels (Cost: 245.00)
    "TUS-W-HEEL-RED-37": [275.00, 260.00, 280.00],
    "TUS-W-HEEL-RED-38": [275.00, 265.00, 285.00],
    "TUS-W-HEEL-BLK-37": [270.00, 258.00, 275.00],
    "TUS-W-HEEL-BLK-38": [270.00, 262.00, 278.00],
    
    # AeroKnit Performance Sneaker V2 (Cost: 38.50)
    "JIN-W-AERO-WHT-36": [45.00, 42.00, 48.00], 
    "JIN-W-AERO-WHT-37": [52.00, 50.00, 55.00],
    "JIN-W-AERO-GRY-36": [48.00, 44.50, 49.00],
    "JIN-W-AERO-GRY-37": [54.00, 52.00, 56.00],
    
    # Milano Hand-Burnished Oxford Dress Shoes (Cost: 185.00)
    # Brown 41 has lowest competitor = 198.00.
    # Brown 42 has lowest competitor = 205.00.
    # Black 41 has lowest competitor = 195.00.
    # Black 42 has lowest competitor = 188.00.
    "MIL-M-OXFORD-BRN-41": [210.00, 198.00, 220.00],
    "MIL-M-OXFORD-BRN-42": [215.00, 205.00, 225.00],
    "MIL-M-OXFORD-BLK-41": [208.00, 195.00, 215.00],
    "MIL-M-OXFORD-BLK-42": [192.00, 188.00, 199.00],
    
    # Apex Trail Runner Pro (Cost: 42.00)
    # Blue 43 lowest competitor = 57.00.
    # Black 42 lowest competitor = 53.50.
    # Black 43 has a rogue competitor price anomaly! (530.00 > price_ceiling: 42.00 * 2.5 = 105.00)
    "PUT-M-APEX-BLU-42": [58.00, 55.00, 62.00],
    "PUT-M-APEX-BLU-43": [60.00, 57.00, 65.00],
    "PUT-M-APEX-BLK-42": [56.00, 53.50, 59.00],
    "PUT-M-APEX-BLK-43": [560.00, 530.00, 590.00], # Rogue listing anomaly
    
    # Florentine Vachetta Leather Bifold Wallet (Cost: 65.00)
    "FLO-WLT-TAN-OS": [85.00, 78.00, 89.00],
    "FLO-WLT-BLK-OS": [72.00, 68.00, 75.00]
}

def scan_competitor_prices():
    sys_dir = get_system_dir()
    os.makedirs(sys_dir, exist_ok=True)
    target_path = os.path.join(sys_dir, "competitor_prices.json")
    
    # Load cost prices for Price Ceiling Guardrail check
    costs = load_sourcing_costs()
    
    print(f"[RUN] Scanning competitor websites for product SKUs...")
    try:
        competitors_profile = {}
        for sku, prices in MOCK_COMPETITORS_DATA.items():
            lowest_price = min(prices)
            cost_val = costs.get(sku)
            
            is_exclusive = False
            # Rule 1: Price Ceiling Guardrail (cost_price * 2.5)
            if cost_val is not None:
                price_ceiling = cost_val * 2.5
                if lowest_price > price_ceiling:
                    print(f"[agent10_competitor_analyst] ROGUE LISTING ANOMALY DETECTED for SKU '{sku}' (Lowest competitor: {lowest_price} > Price ceiling: {price_ceiling}). Overwriting to exclusive fallback.")
                    lowest_price = None
                    is_exclusive = True
            
            competitors_profile[sku] = {
                "sku": sku,
                "lowest_price": lowest_price,
                "market_prices": prices,
                "region_scope": "United States",
                "exclusive": is_exclusive,
                "last_updated": time.time()
            }
            
        with open(target_path, "w") as f:
            json.dump(competitors_profile, f, indent=2)
        print(f"[SUCCESS] Wrote competitor intelligence data to {target_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write competitor prices: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        while True:
            scan_competitor_prices()
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[STOP] {agent_role} shutting down.")
