import sys
import os
import traceback

def main():
    print("[Pipeline Wrapper] Starting multi-agent retail swarm catalog sync...")
    try:
        # 1. Run Sourcing Agent
        print("[Pipeline Wrapper] [Step 1/3] Running Sourcing Agent (Agent 1)...")
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "agents", "agent1_sourcing")))
        import main as m1
        m1.build_sourcing_catalog()
        
        # Clean module cache
        sys.modules.pop("main", None)
        if "m1" in locals():
            del m1

        # 2. Run Competitor Analyst Agent
        print("[Pipeline Wrapper] [Step 2/3] Running Competitor Analyst Agent (Agent 10)...")
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "agents", "agent10_competitor_analyst")))
        import main as m10
        m10.scan_competitor_prices()
        
        # Clean module cache
        sys.modules.pop("main", None)
        if "m10" in locals():
            del m10

        # 3. Run Inventory Agent
        print("[Pipeline Wrapper] [Step 3/3] Running Inventory Agent (Agent 7)...")
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "agents", "agent7_inventory")))
        import main as m7
        m7.build_shopify_catalog()
        
        print("[Pipeline Wrapper] Multi-agent retail swarm catalog sync completed successfully!")
        
    except Exception as e:
        print("[Pipeline Wrapper] ERROR: Pipeline execution failed!", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        
        # Write traceback to a persistent/container log file for extra safety
        try:
            log_dir = "/idm/system/logs"
            if os.path.exists(log_dir):
                error_log_path = os.path.join(log_dir, "pipeline_error.log")
                with open(error_log_path, "a") as f:
                    f.write("\n=== PIPELINE RUN ERROR ===\n")
                    traceback.print_exc(file=f)
                print(f"[Pipeline Wrapper] Error traceback written to {error_log_path}")
        except Exception as log_err:
            print(f"[Pipeline Wrapper] Could not write error log file: {log_err}", file=sys.stderr)
            
        sys.exit(1)

if __name__ == "__main__":
    main()
