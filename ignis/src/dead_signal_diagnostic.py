"""
dead_signal_diagnostic.py — Diagnose traps with zero logit margin.

Three traps (Counting Fence Posts, Rank Reversal, Pages in Book) produce
exactly 0.0 margin. Hypothesis: target and anti tokens share the same
first BPE token, so get_logit_margin returns target_id == anti_id → 0.

This script:
  1. Tokenizes every trap's target/anti pair
  2. Flags first-token collisions
  3. Tests alternative phrasings for the broken traps
  4. Re-evaluates the fixed traps on the corpus-first model

Usage:
    python dead_signal_diagnostic.py --model Qwen/Qwen2.5-1.5B-Instruct
    python dead_signal_diagnostic.py --model results/corpus_first/stageB_finetune/ft_model
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS, get_logit_margin
from phase_transition_study import ORDINAL_TRAPS

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

# ── Alternative phrasings for broken traps ────────────────────────────

FIXED_TRAPS = [
    # Counting Fence Posts: "11" vs "10" → first token collision "1"
    # Fix: rephrase so answers have distinct first tokens
    {
        "name": "Counting Fence Posts [fix: word]",
        "prompt": "A straight fence has 10 sections. How many fence posts are there? Answer: Eleven or Ten?",
        "target_token": "Eleven",
        "anti_token": "Ten",
    },
    {
        "name": "Counting Fence Posts [fix: gt]",
        "prompt": "A straight fence has 10 sections. Are there more than 10 fence posts? Answer: Yes or No?",
        "target_token": "Yes",
        "anti_token": "No",
    },
    # Rank Reversal: "19" vs "18" → first token collision "1"
    {
        "name": "Rank Reversal [fix: word]",
        "prompt": "In a class of 30, you rank 12th from the top. What is your rank from the bottom? Answer: Nineteenth or Eighteenth?",
        "target_token": "N",    # Nineteenth
        "anti_token": "E",      # Eighteenth
    },
    {
        "name": "Rank Reversal [fix: parity]",
        "prompt": "In a class of 30, you rank 12th from the top. Is your rank from the bottom odd or even? Answer: Odd or Even?",
        "target_token": "Odd",
        "anti_token": "Even",
    },
    # Pages in Book: "23" vs "22" → first token collision "2"
    {
        "name": "Pages in Book [fix: parity]",
        "prompt": "A book is open. The two visible page numbers add up to 47. Is the left page odd or even? Answer: Odd or Even?",
        "target_token": "Odd",
        "anti_token": "Even",
    },
    {
        "name": "Pages in Book [fix: consec]",
        "prompt": "A book is open. The two visible page numbers add up to 47. Are the pages consecutive (like 23,24) or separated (like 22,25)? Answer: Consecutive or Separated?",
        "target_token": "Consec",
        "anti_token": "Separ",
    },
]


def main():
    parser = argparse.ArgumentParser(description="Dead-signal trap diagnostic")
    AnalysisBase.add_common_args(parser)
    args = parser.parse_args()

    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir or "results/dead_signal_diagnostic",
    )
    model = base.model

    print("\n" + "=" * 70)
    print("PHASE 1: TOKENIZATION AUDIT — ALL TRAPS")
    print("=" * 70)

    collisions = []
    clean = []

    for trap in ALL_TRAPS:
        target = trap["target_token"]
        anti = trap["anti_token"]

        target_ids = model.to_tokens(target, prepend_bos=False)[0]
        anti_ids = model.to_tokens(anti, prepend_bos=False)[0]

        t0 = target_ids[0].item()
        a0 = anti_ids[0].item()

        collision = (t0 == a0)

        t_tokens = [model.to_str_tokens(target, prepend_bos=False)]
        a_tokens = [model.to_str_tokens(anti, prepend_bos=False)]

        status = "COLLISION" if collision else "ok"
        print(f"  {trap['name']:30s}  target={target!r:12s} → id={t0:6d} {t_tokens}")
        print(f"  {'':30s}  anti  ={anti!r:12s} → id={a0:6d} {a_tokens}  [{status}]")

        if collision:
            collisions.append(trap["name"])
        else:
            clean.append(trap["name"])

    print(f"\n  Summary: {len(clean)} clean, {len(collisions)} COLLISIONS")
    if collisions:
        print(f"  Colliding traps: {', '.join(collisions)}")

    # ── Phase 2: test fixes ──
    print("\n" + "=" * 70)
    print("PHASE 2: ALTERNATIVE PHRASINGS — FIXED TRAPS")
    print("=" * 70)

    fix_results = []

    for trap in FIXED_TRAPS:
        target = trap["target_token"]
        anti = trap["anti_token"]

        target_ids = model.to_tokens(target, prepend_bos=False)[0]
        anti_ids = model.to_tokens(anti, prepend_bos=False)[0]

        t0 = target_ids[0].item()
        a0 = anti_ids[0].item()
        collision = (t0 == a0)

        t_tokens = model.to_str_tokens(target, prepend_bos=False)
        a_tokens = model.to_str_tokens(anti, prepend_bos=False)

        if collision:
            print(f"  {trap['name']:45s}  STILL COLLIDING ({target!r} vs {anti!r})")
            fix_results.append({
                "name": trap["name"],
                "collision": True,
                "margin": 0.0,
            })
            continue

        margin = get_logit_margin(model, trap["prompt"], target, anti)

        status = "CORRECT" if margin > 0 else "WRONG"
        print(f"  {trap['name']:45s}  margin={margin:+.3f}  [{status}]")
        print(f"    target={target!r:12s} → {t_tokens}")
        print(f"    anti  ={anti!r:12s} → {a_tokens}")

        fix_results.append({
            "name": trap["name"],
            "collision": False,
            "margin": float(margin),
            "correct": margin > 0,
            "prompt": trap["prompt"],
            "target_token": target,
            "anti_token": anti,
        })

    # ── Phase 3: test fixes with steering ──
    # Check if genomes available for the winning combo
    results_root = Path(__file__).resolve().parent.parent / "results"
    genome_paths = {
        "L19": results_root / "layer_sweep" / "L19" / "best_genome_1_5b.pt",
        "L20": results_root / "layer_sweep" / "L20" / "best_genome_1_5b.pt",
        "L21": results_root / "batch4_followup" / "stage2_L21" / "best_genome_1_5b.pt",
    }

    genomes_available = all(p.exists() for p in genome_paths.values())

    if genomes_available:
        print("\n" + "=" * 70)
        print("PHASE 3: STEERED EVALUATION — WINNING COMBO (L19+L20+L21 x1.5)")
        print("=" * 70)

        from multilayer_eval import load_genome, make_steering_hook

        hooks = []
        for name, path in genome_paths.items():
            vec, layer, eps = load_genome(str(path))
            v_hat = vec / (vec.norm() + 1e-8)
            v_hat = v_hat.to(args.device)
            hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=eps * 1.5)
            hooks.append((hook_name, hook_fn))
            print(f"  Loaded {name}: layer={layer}, eps={eps * 1.5:.1f}")

        steered_results = []
        for trap in FIXED_TRAPS:
            target = trap["target_token"]
            anti = trap["anti_token"]

            target_ids = model.to_tokens(target, prepend_bos=False)[0]
            anti_ids = model.to_tokens(anti, prepend_bos=False)[0]
            if target_ids[0].item() == anti_ids[0].item():
                continue

            baseline = get_logit_margin(model, trap["prompt"], target, anti)
            steered = get_logit_margin(model, trap["prompt"], target, anti, hooks=hooks)

            flipped = baseline <= 0 and steered > 0
            broken = baseline > 0 and steered <= 0

            tag = ""
            if flipped:
                tag = " ** FLIPPED **"
            elif broken:
                tag = " !! BROKEN !!"

            print(f"  {trap['name']:45s}  base={baseline:+.3f}  steered={steered:+.3f}{tag}")

            steered_results.append({
                "name": trap["name"],
                "baseline": float(baseline),
                "steered": float(steered),
                "flipped": flipped,
                "broken": broken,
            })
    else:
        steered_results = []
        print("\n  [Skipping Phase 3 — genomes not found]")

    # ── Save results ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = base.output_dir / f"dead_signal_diagnostic_{timestamp}.json"
    with open(out, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "collisions": collisions,
            "n_clean": len(clean),
            "n_collisions": len(collisions),
            "fix_results": fix_results,
            "steered_results": steered_results,
        }, f, indent=2)

    print(f"\n  Results saved to {out}")

    # ── Summary recommendation ──
    working_fixes = [r for r in fix_results if not r["collision"] and r.get("correct")]
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    if working_fixes:
        print(f"  {len(working_fixes)} alternative phrasings produce correct baseline signal.")
        print("  These can replace the broken traps in ORDINAL_TRAPS.")
        for r in working_fixes:
            print(f"    - {r['name']}: margin={r['margin']:+.3f}")
    else:
        print("  No working fixes found. The traps may need deeper redesign.")


if __name__ == "__main__":
    main()
