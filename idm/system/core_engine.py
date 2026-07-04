#!/usr/bin/env python3
"""
Robust long-running Swarm core engine.
- Runs the live sales pipeline repeatedly on an interval.
- Handles SIGTERM/SIGINT for graceful shutdown.
- Catches and logs exceptions with exponential backoff.
- Writes a heartbeat file for health checks.
"""
import logging
import os
import signal
import sys
import time
import traceback

# Add parent directory to path so imports of agent modules resolve correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import live agent modules
from agent_0_trend import TrendScout
from agent_1_source import SourcingAgent
from agent_4_storefront import StorefrontManager

INTERVAL = int(os.getenv("CORE_INTERVAL_SECONDS", "10"))
HEARTBEAT_FILE = os.getenv("CORE_HEARTBEAT_FILE", "/idm/system/logs/core_engine.heartbeat")
LOG_PATH = os.getenv("CORE_LOG_FILE", "/idm/system/logs/core_engine.log")

logger = logging.getLogger("core_engine")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - [CORE] - %(levelname)s - %(message)s")

fh = logging.FileHandler(LOG_PATH)
fh.setFormatter(formatter)
logger.addHandler(fh)

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

running = True

def handle_signal(signum, frame):
    global running
    logger.info("Received signal %s, shutting down...", signum)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

class SwarmEngine:
    def __init__(self):
        logger.info("Initializing live Swarm Engine integration.")
        self.trend_scout = TrendScout()
        self.sourcing_agent = SourcingAgent()
        self.storefront = StorefrontManager()

    def execute_sales_pipeline(self):
        logger.info("--- TRIGGERING AUTOMATED SALES PIPELINE ---")
        viral_item = self.trend_scout.scrape_trends()
        if viral_item:
            sourced_item = self.sourcing_agent.source_item(viral_item)
            if sourced_item:
                self.storefront.publish_product(sourced_item)
        logger.info("--- PIPELINE CYCLE COMPLETE ---")

def write_heartbeat():
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        logger.exception("Failed to write heartbeat file")

def main_loop():
    engine = SwarmEngine()
    backoff = 1
    max_backoff = 60
    while running:
        try:
            start = time.time()
            engine.execute_sales_pipeline()
            backoff = 1
            write_heartbeat()
            
            elapsed = time.time() - start
            to_sleep = max(0, INTERVAL - elapsed)
            if to_sleep:
                logger.debug("Sleeping for %.1fs until next cycle", to_sleep)
                time.sleep(to_sleep)
        except Exception as e:
            logger.error("Unhandled exception in pipeline: %s", e)
            logger.error(traceback.format_exc())
            sleep_for = min(backoff, max_backoff)
            logger.info("Backing off for %s seconds before retrying", sleep_for)
            expiry = time.time() + sleep_for
            while running and time.time() < expiry:
                time.sleep(1)
            backoff = min(backoff * 2, max_backoff)
    logger.info("Main loop exiting, cleaning up and shutting down gracefully.")

if __name__ == "__main__":
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    except Exception:
        pass
    logger.info("Starting core engine (interval=%s s)", INTERVAL)
    main_loop()
    logger.info("Core engine stopped.")
