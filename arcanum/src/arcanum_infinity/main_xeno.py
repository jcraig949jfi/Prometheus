import sys
import argparse
import torch
from pathlib import Path

from .xeno_config import XenoConfig
from .xeno_orchestrator import XenoOrchestrator
from .seti_logger import slog


def main():
    parser = argparse.ArgumentParser(description="Arcanum Infinity Discovery Pipeline")
    parser.add_argument("config", nargs="?", help="Path to YAML config file")
    parser.add_argument("--test", action="store_true", help="Run a single test generation and exit")
    
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    if config_path and not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    if torch.cuda.is_available():
        torch.cuda.set_device(0)
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    else:
        print("WARNING: No CUDA device detected. Running on CPU.")

    # Load config and initialize orchestrator
    config = XenoConfig.load(config_path)
    
    # If in test mode, override some config parameters to make it fast
    if args.test:
        print("  >> Running in TEST mode (1 generation, 1 cycle, small population)")
        config.generations = 1
        config.population_size = 2 # Smallest population for testing
        for m in config.models:
            m.generations_per_cycle = 1
        config.cycle_continuously = False

    orchestrator = XenoOrchestrator(config=config)
    
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n  >> User interrupt (Ctrl+C). Initiating graceful shutdown...")
    except Exception as e:
        slog.exception(f"Unhandled exception in main: {e}")
    finally:
        print("  >> Discovery pipeline shut down.")


if __name__ == "__main__":
    main()
