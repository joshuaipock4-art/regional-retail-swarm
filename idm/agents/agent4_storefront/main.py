from fastapi import FastAPI, HTTPException
import os
import time
import requests

app = FastAPI(
    title="9-State Regional Retail Swarm API",
    description="Interface for the multi-agent retail engine, compatible with IBM watsonx Orchestrate.",
    version="1.0.0",
    servers=[{"url": "https://online-retail-swarm-app.2aavgmo7wbf3.us-south.codeengine.appdomain.cloud"}]
)

class ShopifyClient:
    """
    Shopify Admin REST API connection client supporting Client Credentials Token Exchange
    """
    def __init__(self, client_id, client_secret, store_url):
        self.client_id = client_id
        self.client_secret = client_secret
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

    def verify_connection(self):
        if not self.access_token or not self.store_url:
            return False
        url = f"{self.store_url}/admin/api/2024-04/shop.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

# Initialize Shopify Admin API connection client using environment variables
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
SHOPIFY_URL = os.environ.get("SHOPIFY_STORE_URL", "")
shopify_client = ShopifyClient(client_id=SHOPIFY_CLIENT_ID, client_secret=SHOPIFY_CLIENT_SECRET, store_url=SHOPIFY_URL)

@app.get("/")
def read_root():
    # Show status of live API connectivity as well
    shopify_connected = shopify_client.verify_connection() if (shopify_client.access_token and SHOPIFY_URL) else False
    cj_key_set = bool(os.environ.get("CJ_DROPSHIPPING_API_KEY"))
    
    return {
        "status": "online", 
        "swarm": "active", 
        "agents": 9,
        "api_connectivity": {
            "shopify": "connected" if shopify_connected else "configured_offline" if (shopify_client.access_token and SHOPIFY_URL) else "disconnected",
            "cj_dropshipping": "configured" if cj_key_set else "disconnected"
        }
    }

@app.get("/scout-trends", operation_id="scoutTrends")
def scout_trends(region: str = "all"):
    """
    Triggers Agent 0 (Trend Scout) to analyze regional market data.
    """
    return {
        "agent": "agent0_trend_scout",
        "region": region,
        "findings": ["High demand for sustainable materials in Tokyo", "Rising trend in modular furniture"],
        "timestamp": time.time()
    }

@app.get("/check-inventory", operation_id="checkInventory")
def check_inventory(product_id: str):
    """
    Queries Agent 7 (Inventory) for current stock levels across the 9 states.
    """
    return {
        "agent": "agent7_inventory",
        "product_id": product_id,
        "stock_status": "adequate",
        "regional_availability": {
            "us-south-1": 450,
            "us-south-2": 120,
            "us-south": 890
        }
    }

@app.post("/process-order", operation_id="processOrder")
def process_order(order_id: str, region: str):
    """
    Coordinates Agent 5 (Fulfillment) to start the regional delivery pipeline.
    """
    return {
        "agent": "agent5_fulfillment",
        "order_id": order_id,
        "status": "processing",
        "estimated_delivery": "2-4 business days"
    }

@app.post("/process-payment", operation_id="processPayment")
def process_payment(order_id: str, amount: float, payment_method_id: str = "mock-card"):
    """
    Processes credit card payments for orders using Stripe.
    Falls back to a secure mockup payment processor if Stripe secret keys are not configured.
    """
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    
    if stripe_key:
        try:
            try:
                import stripe
            except ImportError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "stripe"])
                import stripe
            stripe.api_key = stripe_key
            
            # Amount is in dollars, convert to cents for Stripe
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                payment_method=payment_method_id,
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never"
                },
                metadata={"order_id": order_id}
            )
            
            if intent.status == "succeeded":
                return {
                    "payment_provider": "Stripe",
                    "status": "succeeded",
                    "transaction_id": intent.id,
                    "amount": amount,
                    "order_id": order_id
                }
            else:
                return {
                    "payment_provider": "Stripe",
                    "status": intent.status,
                    "transaction_id": intent.id,
                    "amount": amount,
                    "order_id": order_id
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Stripe Payment Failed: {str(e)}")
    else:
        # Secure simulation fallback
        print(f"[Simulated Payment] Processing payment of ${amount:.2f} for Order {order_id} using {payment_method_id}...")
        time.sleep(1.0) # simulate network latency
        
        # Simple simulated transaction ID
        simulated_tx_id = f"tx_mock_{int(time.time())}_{order_id[:8]}"
        
        return {
            "payment_provider": "Simulated Gateway",
            "status": "succeeded",
            "transaction_id": simulated_tx_id,
            "amount": amount,
            "order_id": order_id,
            "message": "Payment processed successfully via simulated gateway (Stripe not configured)."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
