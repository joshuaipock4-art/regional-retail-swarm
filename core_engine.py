import logging
import time
import signal
import sys
from agent_0_trend import TrendScout
from agent_1_source import SourcingAgent
from agent_4_storefront import StorefrontManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORE DAEMON] - %(message)s')

class SwarmDaemon:
    def __init__(self):
        self.running = True
        self.trend_scout = TrendScout()
        self.sourcing_agent = SourcingAgent()
        self.storefront = StorefrontManager()
        # Signal handling for graceful shutdown by Supervisor
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False

    def run_cycle(self):
        try:
            logging.info("--- STARTING SALES PIPELINE CYCLE ---")
            trend = self.trend_scout.scrape_trends()
            if trend:
                source = self.sourcing_agent.source_item(trend)
                if source:
                    self.storefront.publish_product(source)
            logging.info("--- CYCLE COMPLETE ---")
        except Exception as e:
            logging.error(f"Cycle failed: {e}")
            # Backoff before retrying to prevent rapid error loops
            time.sleep(10)

    def start(self):
        logging.info("Swarm Engine Daemon started.")
        while self.running:
            self.run_cycle()
            # Heartbeat throttle to comply with API rate limits
            time.sleep(60)
        logging.info("Swarm Engine Daemon stopped safely.")

if __name__ == "__main__":
    daemon = SwarmDaemon()
    daemon.start()
