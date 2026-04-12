"""
Xenolexicon Fast Screening — Entry Point

Rapidly screens a bank of provocation prompts to find the ones that push
the model into the most fertile regions of structured novelty.

Usage:
    # Basic: screen all prompts in a file
    python run_screen.py --prompt-bank prompts.txt

    # Tuned: 3 generations, 10 genomes, threshold 0.08
    python run_screen.py --prompt-bank prompts.txt \\
        --screen-generations 3 --screen-population 10 --screen-threshold 0.08

    # Split across machines: first 75 on machine A, rest on machine B
    python run_screen.py --prompt-bank prompts.txt --start-index 0 --max-prompts 75
    python run_screen.py --prompt-bank prompts.txt --start-index 75

    # Resume after interruption (skips already-screened prompts)
    python run_screen.py --prompt-bank prompts.txt --resume

    # Use a custom config file
    python run_screen.py --prompt-bank prompts.txt --config configs/xenolexicon.yaml
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arcanum_infinity.xeno_config import XenoConfig
from arcanum_infinity.xeno_screener import XenoScreener, ScreenConfig


def main():
    parser = argparse.ArgumentParser(
        description="Xenolexicon Fast Screening — Rapid Prompt Bank Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_screen.py --prompt-bank prompts.txt
  python run_screen.py --prompt-bank prompts.txt --screen-generations 3 --screen-threshold 0.08
  python run_screen.py --prompt-bank prompts.txt --start-index 0 --max-prompts 75
  python run_screen.py --prompt-bank prompts.txt --resume
        """,
    )

    # Required
    parser.add_argument("--prompt-bank", type=str, required=True,
                        help="Path to text file with provocation prompts (one per line or numbered)")

    # Screening parameters
    parser.add_argument("--screen-generations", type=int, default=2,
                        help="Generations per prompt burst (default: 2)")
    parser.add_argument("--screen-population", type=int, default=10,
                        help="Genomes per generation (default: 10, smaller = faster)")
    parser.add_argument("--screen-threshold", type=float, default=0.10,
                        help="Min best score to flag as HIT (default: 0.10)")
    parser.add_argument("--capture-threshold", type=float, default=0.20,
                        help="Min score to attempt specimen capture (default: 0.20)")

    # Range control (for splitting across machines)
    parser.add_argument("--start-index", type=int, default=0,
                        help="Start screening from this prompt index (default: 0)")
    parser.add_argument("--max-prompts", type=int, default=0,
                        help="Max prompts to screen (0 = all, default: 0)")

    # Resume
    parser.add_argument("--resume", action="store_true",
                        help="Skip prompts already in screening_results.csv")

    # Output
    parser.add_argument("--results-dir", type=str, default="results/screening",
                        help="Directory for screening results (default: results/screening)")

    # Base config
    parser.add_argument("--config", type=str, default="configs/xenolexicon.yaml",
                        help="Path to xenolexicon config file (default: configs/xenolexicon.yaml)")

    args = parser.parse_args()

    # Load base xenolexicon config
    xeno_config = XenoConfig.load(Path(args.config) if args.config else None)

    # Build screening config
    screen_config = ScreenConfig(
        prompt_bank_path=Path(args.prompt_bank),
        screen_generations=args.screen_generations,
        screen_population=args.screen_population,
        screen_threshold=args.screen_threshold,
        capture_threshold=args.capture_threshold,
        resume=args.resume,
        results_dir=Path(args.results_dir),
        start_index=args.start_index,
        max_prompts=args.max_prompts,
    )

    # Print config summary
    print(f"\n{'═' * 70}")
    print(f"  XENOLEXICON FAST SCREENING")
    print(f"{'═' * 70}")
    print(f"  Prompt bank:      {screen_config.prompt_bank_path}")
    print(f"  Generations/burst: {screen_config.screen_generations}")
    print(f"  Population/gen:    {screen_config.screen_population}")
    print(f"  Screen threshold:  {screen_config.screen_threshold}")
    print(f"  Capture threshold: {screen_config.capture_threshold}")
    print(f"  Results dir:       {screen_config.results_dir}")
    if args.start_index > 0 or args.max_prompts > 0:
        print(f"  Range:             [{args.start_index}:{args.start_index + args.max_prompts if args.max_prompts else '∞'}]")
    if args.resume:
        print(f"  Resume mode:       ON")
    print(f"{'═' * 70}\n")

    # Run screening
    screener = XenoScreener(xeno_config, screen_config)
    screener.run()


if __name__ == "__main__":
    main()
