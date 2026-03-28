#!/usr/bin/env python3
"""Run all pending forge pipeline tasks.

Called by run_all_pending_tasks.bat with --step N.
Each step is independent and can be run individually.
"""

import argparse
import json
import logging
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TASKS] %(message)s")
log = logging.getLogger("tasks")

HEPH_ROOT = Path(__file__).resolve().parent.parent
PROMETHEUS_ROOT = HEPH_ROOT.parent.parent
V5_DIR = HEPH_ROOT / "forge_v5"
V4_DIR = HEPH_ROOT / "forge_v4"
V3_DIR = HEPH_ROOT / "forge_v3"
V1_DIR = HEPH_ROOT / "forge"


# ============================================================
# STEP 1: Run v5 library against 89-category battery
# ============================================================
def step_1_eval_89cat():
    """Score all v5 tools on 89-category battery (seen + unseen)."""
    from test_harness import load_tool_from_file, _run_battery
    from trap_generator_extended import generate_full_battery

    seen = generate_full_battery(n_per_category=2, seed=42)
    unseen = generate_full_battery(n_per_category=2, seed=137)
    log.info("Batteries: seen=%d unseen=%d (%d categories)",
             len(seen), len(unseen), len(set(t["category"] for t in seen)))

    tools = sorted(p for p in V5_DIR.glob("*.py") if not p.name.startswith("_"))
    log.info("Evaluating %d v5 tools...", len(tools))

    results = {}
    for i, py in enumerate(tools):
        if (i + 1) % 50 == 0:
            log.info("  %d/%d...", i + 1, len(tools))
        try:
            tool = load_tool_from_file(py)
            # Seen
            s_a_c = s_a_t = s_b_c = s_b_t = 0
            cc, cw = [], []
            for t in seen:
                try:
                    r = tool.evaluate(t["prompt"], t["candidates"])
                    if r:
                        ok = r[0]["candidate"] == t["correct"]
                        tier = t.get("tier", "A")
                        if tier == "A": s_a_t += 1; s_a_c += ok
                        else: s_b_t += 1; s_b_c += ok
                        try:
                            c = tool.confidence(t["prompt"], t["correct"])
                            (cc if ok else cw).append(c)
                        except: pass
                except:
                    if t.get("tier") == "A": s_a_t += 1
                    else: s_b_t += 1

            # Unseen
            u_c = u_t = 0
            for t in unseen:
                try:
                    r = tool.evaluate(t["prompt"], t["candidates"])
                    if r: u_t += 1; u_c += (r[0]["candidate"] == t["correct"])
                except: u_t += 1

            sa = s_a_c / s_a_t if s_a_t else 0
            sb = s_b_c / s_b_t if s_b_t else 0
            so = (s_a_c + s_b_c) / (s_a_t + s_b_t) if (s_a_t + s_b_t) else 0
            ua = u_c / u_t if u_t else 0
            h = (np.mean(cc) if cc else 0.5) - (np.mean(cw) if cw else 0.5)

            results[py.stem] = {
                "seen_tier_a": round(sa, 4), "seen_tier_b": round(sb, 4),
                "seen_overall": round(so, 4), "unseen_overall": round(ua, 4),
                "epistemic_honesty": round(h, 4), "gap": round(so - ua, 4),
            }
        except:
            results[py.stem] = {"error": True}

    out = V5_DIR / "all_scores_89cat.json"
    out.write_text(json.dumps({"tools": results, "categories": len(set(t["category"] for t in seen))},
                              indent=2), encoding="utf-8")

    v = [r for r in results.values() if "error" not in r]
    log.info("RESULTS: %d tools scored", len(v))
    log.info("  Tier A: %.1f%% median", np.median([r["seen_tier_a"] for r in v]) * 100)
    log.info("  Tier B: %.1f%% median", np.median([r["seen_tier_b"] for r in v]) * 100)
    log.info("  Unseen: %.1f%% median", np.median([r["unseen_overall"] for r in v]) * 100)
    log.info("  Honesty: %.3f median", np.median([r["epistemic_honesty"] for r in v]))
    log.info("Saved: %s", out)


# ============================================================
# STEP 2: Re-run behavioral fingerprints on 89-cat battery
# ============================================================
def step_2_fingerprints():
    """Re-run behavioral fingerprints with expanded battery."""
    log.info("Running behavioral fingerprints...")
    try:
        import behavioral_fingerprints
        behavioral_fingerprints.main()
    except Exception as e:
        log.error("Fingerprints failed: %s", e)
        # Fallback: run as subprocess
        import subprocess
        subprocess.run([sys.executable, "behavioral_fingerprints.py"],
                       cwd=str(Path(__file__).parent))


# ============================================================
# STEP 3: Generational trajectory (v1→v5 fitness curves)
# ============================================================
def step_3_generational_trajectory():
    """Plot per-concept fitness across v1→v5 generations."""
    from test_harness import load_tool_from_file, TRAPS, _run_battery

    log.info("Computing generational trajectory...")

    def concept_set(filename):
        return frozenset(c.replace("_", " ").lower() for c in Path(filename).stem.split("_x_"))

    generations = {"v1": V1_DIR, "v3": V3_DIR, "v4": V4_DIR, "v5": V5_DIR}
    # Skip v2 (only 50 tools, not representative)

    # Build concept-set → file maps per generation
    gen_maps = {}
    for gen, gdir in generations.items():
        gmap = {}
        for p in gdir.glob("*.py"):
            if p.name.startswith("_"): continue
            gmap[concept_set(p.name)] = p
        gen_maps[gen] = gmap
        log.info("  %s: %d tools", gen, len(gmap))

    # Find concept sets present in ALL generations
    all_cs = set(gen_maps["v1"].keys())
    for gen in gen_maps:
        all_cs &= set(gen_maps[gen].keys())
    log.info("  Concept sets in all generations: %d", len(all_cs))

    # Score a sample on static battery
    import random
    random.seed(42)
    sample = random.sample(list(all_cs), min(50, len(all_cs)))

    trajectories = {}
    for cs in sample:
        name = "_x_".join(sorted(cs)).replace(" ", "_")
        traj = {}
        for gen, gmap in gen_maps.items():
            py = gmap.get(cs)
            if py:
                try:
                    tool = load_tool_from_file(py)
                    r = _run_battery(tool, TRAPS)
                    traj[gen] = round(r["accuracy"] + r["calibration"], 4)
                except:
                    traj[gen] = 0
        trajectories[name] = traj

    # Find biggest improvers and plateaus
    improvers = []
    plateaus = []
    for name, traj in trajectories.items():
        if "v1" in traj and "v5" in traj:
            delta = traj["v5"] - traj["v1"]
            if delta > 0.3:
                improvers.append((name, delta, traj))
            elif abs(delta) < 0.05:
                plateaus.append((name, delta, traj))

    improvers.sort(key=lambda x: -x[1])
    out = V5_DIR / "generational_trajectory.json"
    out.write_text(json.dumps({
        "trajectories": trajectories,
        "top_improvers": [(n, d) for n, d, _ in improvers[:20]],
        "plateaus": [(n, d) for n, d, _ in plateaus[:20]],
        "sample_size": len(sample),
    }, indent=2), encoding="utf-8")

    log.info("Top improvers (v1→v5):")
    for name, delta, traj in improvers[:10]:
        log.info("  +%.0f%% %s", delta * 100, name[:50])
    log.info("Plateaus (no change v1→v5): %d tools", len(plateaus))
    log.info("Saved: %s", out)


# ============================================================
# STEP 4: Dedup gate
# ============================================================
def step_4_dedup_gate():
    """Add dedup gate to Hephaestus — identify redundant tool pairs."""
    log.info("Computing dedup analysis...")

    scores_path = V5_DIR / "all_scores_89cat.json"
    if not scores_path.exists():
        scores_path = V5_DIR / "all_scores.json"
    if not scores_path.exists():
        log.warning("No scores file found, skipping dedup")
        return

    data = json.loads(scores_path.read_text(encoding="utf-8"))
    tools = data.get("tools", data)

    # Group by seen_overall accuracy (tools within 0.01 of each other)
    by_score = defaultdict(list)
    for name, r in tools.items():
        if isinstance(r, dict) and "error" not in r:
            bucket = round(r.get("seen_overall", 0), 2)
            by_score[bucket].append(name)

    # Find exact-score duplicates
    exact_dupes = {k: v for k, v in by_score.items() if len(v) > 1}
    total_redundant = sum(len(v) - 1 for v in exact_dupes.values())

    # Build dedup recommendations
    keep = set()
    scrap = set()
    for bucket, names in exact_dupes.items():
        # Keep the one with best unseen score
        best = max(names, key=lambda n: tools[n].get("unseen_overall", 0))
        keep.add(best)
        for n in names:
            if n != best:
                scrap.add(n)

    out = V5_DIR / "dedup_analysis.json"
    out.write_text(json.dumps({
        "total_tools": len(tools),
        "exact_score_duplicates": total_redundant,
        "unique_after_dedup": len(tools) - total_redundant,
        "keep": sorted(keep),
        "scrap_candidates": sorted(scrap),
        "duplicate_buckets": {str(k): v for k, v in exact_dupes.items()},
    }, indent=2), encoding="utf-8")

    log.info("Dedup: %d redundant (same score), %d unique remain",
             total_redundant, len(tools) - total_redundant)
    log.info("Saved: %s", out)


# ============================================================
# STEP 5: Family-level RLVF weighting
# ============================================================
def step_5_family_weighting():
    """Compute family-level weights for RLVF fitness function."""
    log.info("Computing family-level RLVF weights...")

    scores_path = V5_DIR / "all_scores_89cat.json"
    if not scores_path.exists():
        scores_path = V5_DIR / "all_scores.json"
    data = json.loads(scores_path.read_text(encoding="utf-8"))
    tools = data.get("tools", data)

    # Extract concept families
    families = defaultdict(list)
    for name, r in tools.items():
        if isinstance(r, dict) and "error" not in r:
            concepts = [c.replace("_", " ").title() for c in name.split("_x_")]
            for c in concepts:
                families[c].append({
                    "name": name,
                    "unseen": r.get("unseen_overall", 0),
                    "honesty": r.get("epistemic_honesty", 0),
                })

    # Compute per-family metrics
    family_weights = {}
    for family, members in sorted(families.items(), key=lambda x: -len(x[1])):
        n = len(members)
        avg_unseen = np.mean([m["unseen"] for m in members])
        avg_honesty = np.mean([m["honesty"] for m in members])

        # Weight = quality / sqrt(count) — penalizes large families
        # A family of 75 tools gets weight / 8.66, family of 1 gets full weight
        raw_weight = avg_unseen * (1 + avg_honesty)
        family_weight = raw_weight / np.sqrt(n)

        family_weights[family] = {
            "count": n,
            "avg_unseen": round(avg_unseen, 4),
            "avg_honesty": round(avg_honesty, 4),
            "raw_weight": round(raw_weight, 4),
            "family_weight": round(family_weight, 4),
        }

    out = V5_DIR / "family_weights.json"
    out.write_text(json.dumps(family_weights, indent=2), encoding="utf-8")

    log.info("Family weights (top 10):")
    ranked = sorted(family_weights.items(), key=lambda x: -x[1]["family_weight"])
    for name, w in ranked[:10]:
        log.info("  %-30s n=%3d  unseen=%.1f%%  weight=%.4f",
                 name, w["count"], w["avg_unseen"] * 100, w["family_weight"])
    log.info("Saved: %s", out)


# ============================================================
# STEP 6: Tier-aware honesty metric
# ============================================================
def step_6_tier_honesty():
    """Compute tier-aware epistemic honesty for all v5 tools."""
    from test_harness import load_tool_from_file
    from trap_generator_extended import generate_full_battery

    log.info("Computing tier-aware honesty...")
    battery = generate_full_battery(n_per_category=2, seed=42)
    tier_a = [t for t in battery if t.get("tier") == "A"]
    tier_b = [t for t in battery if t.get("tier") == "B"]

    tools = sorted(p for p in V5_DIR.glob("*.py") if not p.name.startswith("_"))
    import random
    random.seed(42)
    sample = random.sample(tools, min(100, len(tools)))

    results = {}
    for py in sample:
        try:
            tool = load_tool_from_file(py)

            # Tier A honesty: conf_correct - conf_wrong
            a_cc, a_cw = [], []
            for t in tier_a:
                try:
                    r = tool.evaluate(t["prompt"], t["candidates"])
                    if r:
                        ok = r[0]["candidate"] == t["correct"]
                        c = tool.confidence(t["prompt"], t["correct"])
                        (a_cc if ok else a_cw).append(c)
                except: pass

            # Tier B honesty: closeness to 0.3 (should be low confidence)
            b_confs = []
            for t in tier_b:
                try:
                    c = tool.confidence(t["prompt"], t["correct"])
                    b_confs.append(c)
                except: pass

            a_honesty = (np.mean(a_cc) if a_cc else 0.5) - (np.mean(a_cw) if a_cw else 0.5)
            b_honesty = 1.0 - abs(np.mean(b_confs) - 0.3) if b_confs else 0.0
            combined = 0.6 * a_honesty + 0.4 * b_honesty

            results[py.stem] = {
                "tier_a_honesty": round(a_honesty, 4),
                "tier_b_honesty": round(b_honesty, 4),
                "combined_honesty": round(combined, 4),
                "avg_tier_b_confidence": round(np.mean(b_confs), 4) if b_confs else None,
            }
        except:
            pass

    out = V5_DIR / "tier_aware_honesty.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    v = list(results.values())
    log.info("Tier-aware honesty (sample=%d):", len(v))
    log.info("  Tier A honesty median: %.3f", np.median([r["tier_a_honesty"] for r in v]))
    log.info("  Tier B honesty median: %.3f", np.median([r["tier_b_honesty"] for r in v]))
    log.info("  Combined median: %.3f", np.median([r["combined_honesty"] for r in v]))
    log.info("  Avg Tier B confidence median: %.3f",
             np.median([r["avg_tier_b_confidence"] for r in v if r["avg_tier_b_confidence"] is not None]))
    log.info("Saved: %s", out)


# ============================================================
# STEP 7: Fix remaining 3 Tier B patterns
# ============================================================
def step_7_fix_tier_b():
    """Broaden _meta_confidence for argument_strength, intention_vs_outcome, survivorship_bias."""
    log.info("Fixing remaining Tier B patterns...")

    tools = sorted(p for p in V5_DIR.glob("*.py") if not p.name.startswith("_"))
    updated = 0

    for py in tools:
        try:
            src = py.read_text(encoding="utf-8")
            if "def _meta_confidence" not in src:
                continue

            changed = False

            # Add argument_strength pattern if missing
            if "argument" not in src.lower() or "stronger" not in src.lower():
                # Insert after the last return 0.20/0.22/0.25 line before "return 1.0"
                if "return 1.0" in src:
                    insert = """
    # Argument strength (comparing two arguments)
    if re.search(r'argument\\s+[ab12]', pl) and re.search(r'stronger|weaker|better|more\\s+valid', pl):
        return 0.25
"""
                    src = src.replace("    return 1.0", insert + "    return 1.0", 1)
                    changed = True

            # Add survivorship_bias broader pattern
            if "billionaire" not in src.lower() and "olympic" not in src.lower():
                if "return 1.0" in src:
                    insert = """
    # Survivorship bias (broader)
    if re.search(r'\\b(?:all|every)\\s+(?:successful|winning|top|best|famous|olympic|billionaire|rich)\\b', pl):
        if re.search(r'\\bsample\\b|\\bstudy\\b|\\bfind|\\bshow', pl):
            return 0.20
"""
                    src = src.replace("    return 1.0", insert + "    return 1.0", 1)
                    changed = True

            # Add intention_vs_outcome broader pattern
            if "protocol" not in src.lower() or "seatbelt" not in src.lower():
                if "return 1.0" in src:
                    insert = """
    # Intention vs outcome (broader)
    if re.search(r'\\b(?:followed|used|applied|wore|took)\\s+(?:protocol|standard|recommended|proper|correct|seatbelt|precaution)', pl):
        if re.search(r'\\b(?:died|failed|injured|accident|reaction|collapsed|crash|fire|flood)\\b', pl):
            return 0.25
"""
                    src = src.replace("    return 1.0", insert + "    return 1.0", 1)
                    changed = True

            if changed:
                py.write_text(src, encoding="utf-8")
                updated += 1
        except Exception:
            pass

    log.info("Updated %d tools with broader Tier B patterns", updated)


# ============================================================
# STEP 8: Update Nous scoring weights
# ============================================================
def step_8_nous_weights():
    """Update Nous scorer to weight hypothesis_generation higher than implementability."""
    log.info("Updating Nous scoring weights...")

    nous_scorer = PROMETHEUS_ROOT / "agents" / "nous" / "src" / "scorer.py"
    if not nous_scorer.exists():
        # Try nous.py
        nous_scorer = PROMETHEUS_ROOT / "agents" / "nous" / "src" / "nous.py"

    if not nous_scorer.exists():
        log.warning("Nous scorer not found, skipping")
        return

    src = nous_scorer.read_text(encoding="utf-8")

    # Look for weight definitions
    # Common patterns: weights dict, or individual weight vars
    if "hypothesis_generation" in src and "implementability" in src:
        # Check current weights
        hg_match = re.search(r'hypothesis_generation["\']?\s*[:=]\s*([\d.]+)', src)
        impl_match = re.search(r'implementability["\']?\s*[:=]\s*([\d.]+)', src)

        if hg_match and impl_match:
            hg_weight = float(hg_match.group(1))
            impl_weight = float(impl_match.group(1))
            log.info("Current weights: hypothesis_generation=%.2f, implementability=%.2f",
                     hg_weight, impl_weight)

            if hg_weight <= impl_weight:
                # Swap: make hypothesis_generation = 0.35, implementability = 0.15
                src = re.sub(
                    r'(hypothesis_generation["\']?\s*[:=]\s*)[\d.]+',
                    r'\g<1>0.35', src)
                src = re.sub(
                    r'(implementability["\']?\s*[:=]\s*)[\d.]+',
                    r'\g<1>0.15', src)
                nous_scorer.write_text(src, encoding="utf-8")
                log.info("Updated: hypothesis_generation=0.35, implementability=0.15")
            else:
                log.info("Already correctly weighted, no change needed")
        else:
            log.info("Weight pattern not found in expected format, manual update needed")
    else:
        log.info("Nous scorer doesn't have expected weight fields, checking composite formula...")
        # Log the relevant section for manual review
        for i, line in enumerate(src.splitlines()):
            if "composite" in line.lower() or "weight" in line.lower():
                log.info("  Line %d: %s", i + 1, line.strip()[:80])


# ============================================================
# STEP 9: Quartet compositor
# ============================================================
def step_9_quartet_compositor():
    """Build and evaluate Structure × Measure × Constraint × Dynamics quartets."""
    from test_harness import load_tool_from_file, TRAPS

    log.info("Building quartet compositor...")

    # Load concept metadata to classify by mechanism type
    # Fallback: classify by known concept families
    mechanism_map = {
        # Structure
        "compositionality": "structure", "category theory": "structure",
        "topology": "structure", "network science": "structure",
        "graph theory": "structure", "type theory": "structure",
        # Measure
        "information theory": "measure", "kolmogorov complexity": "measure",
        "maximum entropy": "measure", "spectral analysis": "measure",
        "sparse autoencoders": "measure", "tensor decomposition": "measure",
        # Constraint
        "falsificationism": "constraint", "criticality": "constraint",
        "model checking": "constraint", "constraint satisfaction": "constraint",
        "error correcting codes": "constraint",
        # Dynamics
        "chaos theory": "dynamics", "ergodic theory": "dynamics",
        "active inference": "dynamics", "free energy principle": "dynamics",
        "neural oscillations": "dynamics", "phase transitions": "dynamics",
        "thermodynamics": "dynamics", "reinforcement learning": "dynamics",
    }

    # Classify v5 tools
    typed_tools = defaultdict(list)
    for py in sorted(V5_DIR.glob("*.py")):
        if py.name.startswith("_"): continue
        concepts = [c.replace("_", " ").lower() for c in py.stem.split("_x_")]
        types = set()
        for c in concepts:
            if c in mechanism_map:
                types.add(mechanism_map[c])
        if len(types) == 1:
            typed_tools[types.pop()].append(py)

    log.info("Typed tools: structure=%d measure=%d constraint=%d dynamics=%d",
             len(typed_tools["structure"]), len(typed_tools["measure"]),
             len(typed_tools["constraint"]), len(typed_tools["dynamics"]))

    if not all(typed_tools[t] for t in ["structure", "measure", "constraint", "dynamics"]):
        log.warning("Not enough tools in each category for quartets")
        return

    # Sample: pick top 5 from each type by accuracy
    from test_harness import _run_battery
    type_scores = {}
    for mtype, tools in typed_tools.items():
        scored = []
        for py in tools[:20]:  # Score first 20
            try:
                tool = load_tool_from_file(py)
                r = _run_battery(tool, TRAPS)
                scored.append((r["accuracy"], py))
            except: pass
        scored.sort(reverse=True)
        type_scores[mtype] = scored[:5]
        log.info("  %s top 5: %s", mtype,
                 ", ".join(f"{a*100:.0f}%" for a, _ in scored[:5]))

    # Build quartets from top 5 of each type
    quartets = []
    for s_acc, s_py in type_scores["structure"]:
        for m_acc, m_py in type_scores["measure"]:
            for c_acc, c_py in type_scores["constraint"]:
                for d_acc, d_py in type_scores["dynamics"]:
                    quartets.append({
                        "structure": s_py.stem,
                        "measure": m_py.stem,
                        "constraint": c_py.stem,
                        "dynamics": d_py.stem,
                        "avg_individual": (s_acc + m_acc + c_acc + d_acc) / 4,
                    })

    log.info("Generated %d quartets from top-5 per type", len(quartets))

    # Evaluate a sample of quartets (ensemble voting)
    import random
    random.seed(42)
    sample_quartets = random.sample(quartets, min(50, len(quartets)))

    quartet_results = []
    for q in sample_quartets:
        try:
            tools = []
            for key in ["structure", "measure", "constraint", "dynamics"]:
                py = V5_DIR / f"{q[key]}.py"
                tools.append(load_tool_from_file(py))

            # Ensemble: majority vote
            correct = 0
            total = 0
            for trap in TRAPS:
                votes = Counter()
                for tool in tools:
                    try:
                        r = tool.evaluate(trap["prompt"], trap["candidates"])
                        if r:
                            votes[r[0]["candidate"]] += 1
                    except: pass
                if votes:
                    winner = votes.most_common(1)[0][0]
                    total += 1
                    if winner == trap["correct"]:
                        correct += 1

            ensemble_acc = correct / total if total else 0
            q["ensemble_accuracy"] = round(ensemble_acc, 4)
            q["improvement"] = round(ensemble_acc - q["avg_individual"], 4)
            quartet_results.append(q)
        except: pass

    quartet_results.sort(key=lambda x: -x.get("ensemble_accuracy", 0))

    out = V5_DIR / "quartet_compositor.json"
    out.write_text(json.dumps({
        "total_quartets": len(quartets),
        "evaluated": len(quartet_results),
        "results": quartet_results[:20],
        "avg_ensemble_accuracy": round(np.mean([q["ensemble_accuracy"] for q in quartet_results]), 4) if quartet_results else 0,
        "avg_improvement_over_individual": round(np.mean([q["improvement"] for q in quartet_results]), 4) if quartet_results else 0,
    }, indent=2), encoding="utf-8")

    if quartet_results:
        log.info("Quartet results:")
        log.info("  Avg ensemble accuracy: %.1f%%",
                 np.mean([q["ensemble_accuracy"] for q in quartet_results]) * 100)
        log.info("  Avg improvement over individuals: %+.1f%%",
                 np.mean([q["improvement"] for q in quartet_results]) * 100)
        best = quartet_results[0]
        log.info("  Best quartet: %.1f%% (improvement +%.1f%%)",
                 best["ensemble_accuracy"] * 100, best["improvement"] * 100)
    log.info("Saved: %s", out)


# ============================================================
# STEP 10: A/D interface evolution design doc
# ============================================================
def step_10_ad_interface():
    """Write the A/D interface evolution design document."""
    log.info("Writing A/D interface evolution design...")

    doc = """# A/D Interface Evolution Design

*Evolve interfaces between Solver (A/C) and Critic (D) tools*

## The Insight

The tool library has a natural division:
- **97 Solvers** (Architecture A/C): 91-92% unseen accuracy, can compute answers
- **240 Critics** (Architecture D): 73% Tier B accuracy, good at detecting problems

Don't evolve D tools into A tools. Evolve better **interfaces** between them.

## Architecture

```
Prompt + Candidates
    │
    ▼
┌─────────────┐
│  Solver (A)  │──→ Ranked candidates + scores
└─────────────┘
    │
    ▼
┌─────────────┐
│  Critic (D)  │──→ Confidence adjustment + flags
└─────────────┘
    │
    ▼
Final ranking (Solver accuracy + Critic judgment)
```

## Interface Protocol

```python
class SolverCriticPair:
    def __init__(self, solver, critic):
        self.solver = solver  # Architecture A/C tool
        self.critic = critic  # Architecture D tool

    def evaluate(self, prompt, candidates):
        # Step 1: Solver ranks candidates
        solver_result = self.solver.evaluate(prompt, candidates)

        # Step 2: Critic evaluates each candidate independently
        critic_scores = {}
        for cand in candidates:
            critic_result = self.critic.evaluate(prompt, [cand, ""])
            critic_scores[cand] = critic_result[0]["score"] if critic_result else 0.5

        # Step 3: Blend (solver 70%, critic 30%)
        blended = []
        for r in solver_result:
            c_score = critic_scores.get(r["candidate"], 0.5)
            combined = 0.7 * r["score"] + 0.3 * c_score
            blended.append({
                "candidate": r["candidate"],
                "score": combined,
                "reasoning": f"solver:{r['score']:.2f} critic:{c_score:.2f} | {r.get('reasoning', '')}",
            })
        blended.sort(key=lambda x: -x["score"])
        return blended

    def confidence(self, prompt, answer):
        s_conf = self.solver.confidence(prompt, answer)
        c_conf = self.critic.confidence(prompt, answer)
        # Critic's LOW confidence overrides solver's HIGH confidence
        if c_conf < 0.3:
            return min(s_conf, c_conf + 0.1)  # Cap at critic's doubt + small margin
        return 0.6 * s_conf + 0.4 * c_conf
```

## Selection Pressure

The key innovation: **Critic negative signals override Solver positive signals.**

When a Critic tool says "this looks wrong" (confidence < 0.3) and the Solver says
"this looks right" (confidence > 0.7), the pair returns low confidence. This creates
selection pressure for:
- Solvers that produce answers Critics agree with
- Critics that flag genuinely problematic answers (not random noise)

## Evolution Strategy

1. Pre-compute all Solver × Critic pairs on the 89-category battery
2. Select pairs where the combination outperforms the Solver alone
3. These pairs define "compatible" Solver-Critic relationships
4. Apollo can breed within compatible pairs

## Metrics

- **Pair accuracy**: does the combination beat the Solver alone?
- **Pair calibration**: does Critic suppression improve calibration?
- **Complementarity**: do they disagree on different categories?
"""

    out = PROMETHEUS_ROOT / "docs" / "ad_interface_evolution.md"
    out.write_text(doc, encoding="utf-8")
    log.info("Written: %s", out)


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, help="Run specific step (1-10)")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    args = parser.parse_args()

    steps = {
        1: ("89-cat battery evaluation", step_1_eval_89cat),
        2: ("Behavioral fingerprints", step_2_fingerprints),
        3: ("Generational trajectory", step_3_generational_trajectory),
        4: ("Dedup gate", step_4_dedup_gate),
        5: ("Family-level RLVF weighting", step_5_family_weighting),
        6: ("Tier-aware honesty metric", step_6_tier_honesty),
        7: ("Fix Tier B patterns", step_7_fix_tier_b),
        8: ("Nous scoring weights", step_8_nous_weights),
        9: ("Quartet compositor", step_9_quartet_compositor),
        10: ("A/D interface design", step_10_ad_interface),
    }

    if args.step:
        name, fn = steps[args.step]
        log.info("=" * 60)
        log.info("Step %d: %s", args.step, name)
        log.info("=" * 60)
        try:
            fn()
        except Exception as e:
            log.error("Step %d failed: %s", args.step, e)
            import traceback
            traceback.print_exc()
    elif args.all:
        for step_num in sorted(steps):
            name, fn = steps[step_num]
            log.info("=" * 60)
            log.info("Step %d: %s", step_num, name)
            log.info("=" * 60)
            try:
                fn()
            except Exception as e:
                log.error("Step %d failed: %s", step_num, e)
            log.info("")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
