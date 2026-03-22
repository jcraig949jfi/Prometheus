import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import argparse
from pathlib import Path
from ignis_orchestrator import IgnisOrchestrator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ignis Latent Pipeline")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    args = parser.parse_args()
    
    config_path = Path(args.config) if args.config else None
    
    orchestrator = IgnisOrchestrator(config_path=config_path)
    orchestrator.run()
