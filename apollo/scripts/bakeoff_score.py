"""Score one bake-off run from its apollo_run.jsonl log file.

Usage:
    python bakeoff_score.py <run_dir> [start_gen] [end_gen]

Examples:
    python bakeoff_score.py D:\\Prometheus\\apollo\\run_v2d2b 1491 1590
    python bakeoff_score.py D:\\Prometheus\\apollo\\run_v2d2b_phi4mini 1491 1590

Outputs: gens/hr, mean gen_time, llm_alive trajectory, AOS distribution,
best/median accuracy delta, mutation operator survival, monoculture events.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from statistics import mean


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    run_dir = Path(sys.argv[1])
    start_gen = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end_gen = int(sys.argv[3]) if len(sys.argv) > 3 else 999_999

    log_path = run_dir / "logs" / "apollo_run.jsonl"
    if not log_path.exists():
        print(f"NO LOG: {log_path}")
        sys.exit(1)

    # In-window metrics
    gen_times = []
    best_accs = []
    median_accs = []
    llm_alive_samples = []
    health_samples = []
    aos_snapshots = []
    mutation_op_counts = Counter()
    mutation_op_survival = defaultdict(lambda: [0, 0])  # [survivors, total]
    monoculture_events = 0
    hybrid_batch_calls = 0
    qwen_batch_calls = 0
    alt_batch_calls = 0
    deepseek_calls = 0
    deepseek_fail = 0
    racing_summaries = []

    first_ts = None
    last_ts = None
    seen_gens = set()

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            gen = rec.get("generation")
            stage = rec.get("stage", "")
            msg = rec.get("message", "")
            data = rec.get("data", {}) or {}
            ts = rec.get("timestamp")

            if gen is None or gen < start_gen or gen > end_gen:
                # Allow LLM calls with gen=None (debug logs) to be counted
                if stage == "llm" and msg.startswith("LLM call: hybrid_batch"):
                    hybrid_batch_calls += 1
                elif stage == "llm" and msg.startswith("LLM call: qwen_batch"):
                    qwen_batch_calls += 1
                elif stage == "llm" and "DeepSeek call" in msg:
                    deepseek_calls += 1
                    if "fail" in msg:
                        deepseek_fail += 1
                continue

            if first_ts is None:
                first_ts = ts
            last_ts = ts
            seen_gens.add(gen)

            if stage == "main" and msg.startswith("[     main]"):
                # extract gen_time from " | 18.0s | "
                import re
                m = re.search(r"\|\s*([0-9.]+)s\s*\|\s*[0-9.]+h", msg)
                if m:
                    gen_times.append(float(m.group(1)))
            if stage == "dashboard":
                # best_acc=+0.450 | med_acc=+0.300
                import re
                m_b = re.search(r"best_acc=\+?([\-0-9.]+)", msg)
                m_m = re.search(r"med_acc=\+?([\-0-9.]+)", msg)
                if m_b:
                    best_accs.append(float(m_b.group(1)))
                if m_m:
                    median_accs.append(float(m_m.group(1)))
            if stage == "health":
                if "MONOCULTURE" in msg:
                    monoculture_events += 1
                else:
                    # extract llm_alive=N
                    import re
                    m = re.search(r"llm_alive=(\d+)", msg)
                    if m:
                        llm_alive_samples.append(int(m.group(1)))
                    m = re.search(
                        r"structs=(\d+)/50 \| clones=(\d+)% \|.+?prims_used=(\d+)/\d+",
                        msg,
                    )
                    if m:
                        health_samples.append({
                            "gen": gen,
                            "structs": int(m.group(1)),
                            "clones": int(m.group(2)),
                            "prims_used": int(m.group(3)),
                        })
            if stage == "aos":
                probs = data.get("probabilities", {})
                if probs:
                    aos_snapshots.append((gen, probs))
            if stage == "mutation":
                mt = data.get("mutation_type", "")
                if mt:
                    mutation_op_counts[mt] += 1
            if stage == "selection":
                muts = data.get("mutations", [])
                op = muts[-1] if muts else "?"
                # this is a "death" log for non-selected organisms
                mutation_op_survival[op][1] += 1  # died
            if stage == "llm" and msg.startswith("LLM call: hybrid_batch"):
                hybrid_batch_calls += 1
            elif stage == "llm" and msg.startswith("LLM call: qwen_batch"):
                qwen_batch_calls += 1
            elif stage == "llm" and "alt" in msg and "batch" in msg:
                alt_batch_calls += 1
            elif stage == "llm" and "DeepSeek call" in msg:
                deepseek_calls += 1
                if "fail" in msg:
                    deepseek_fail += 1
            if stage == "racing":
                m = data
                racing_summaries.append(m)

    # ── Compute summary ─────────────────────────────────────────────
    if not gen_times:
        print(f"No gens found in window [{start_gen}, {end_gen}] for {log_path}")
        return

    n_gens = len(seen_gens)
    print(f"=== {run_dir.name} | gens {min(seen_gens)}..{max(seen_gens)} (N={n_gens}) ===")
    print(f"Time window: {first_ts} -> {last_ts}")

    print(f"\n--- Throughput ---")
    print(f"  Gens sampled for time: {len(gen_times)}")
    print(f"  Mean gen_time: {mean(gen_times):.2f}s  (median {sorted(gen_times)[len(gen_times)//2]:.2f}s, "
          f"min {min(gen_times):.2f}s, max {max(gen_times):.2f}s)")
    if gen_times:
        gens_per_hr = 3600 / mean(gen_times)
        print(f"  Gens/hour: {gens_per_hr:.1f}  ({gens_per_hr*24:.0f}/day)")

    print(f"\n--- Fitness trajectory ---")
    if best_accs:
        print(f"  best_acc:  start={best_accs[0]:+.3f}  end={best_accs[-1]:+.3f}  "
              f"max={max(best_accs):+.3f}  mean={mean(best_accs):+.3f}")
    if median_accs:
        print(f"  med_acc:   start={median_accs[0]:+.3f}  end={median_accs[-1]:+.3f}  "
              f"max={max(median_accs):+.3f}  mean={mean(median_accs):+.3f}")

    print(f"\n--- Population health ---")
    if llm_alive_samples:
        print(f"  llm_alive: samples={len(llm_alive_samples)}  "
              f"mean={mean(llm_alive_samples):.2f}  max={max(llm_alive_samples)}  "
              f"nonzero%={sum(1 for x in llm_alive_samples if x > 0)/len(llm_alive_samples):.1%}")
    if health_samples:
        avg_structs = mean(h["structs"] for h in health_samples)
        avg_clones = mean(h["clones"] for h in health_samples)
        avg_prims = mean(h["prims_used"] for h in health_samples)
        print(f"  structs/50 avg: {avg_structs:.1f}")
        print(f"  clones %% avg:   {avg_clones:.1f}%")
        print(f"  prims_used avg: {avg_prims:.1f} / 27")
    print(f"  MONOCULTURE events: {monoculture_events}")

    print(f"\n--- AOS evolution ---")
    if aos_snapshots:
        # Last 5 snapshots
        for g, p in aos_snapshots[-5:]:
            ps = " ".join(f"{k[:4]}={v:.2f}" for k, v in p.items())
            print(f"  gen {g}: {ps}")

    print(f"\n--- Mutation operator usage (in-window) ---")
    for op, cnt in mutation_op_counts.most_common():
        print(f"  {op:40s} : {cnt}")

    print(f"\n--- LLM call breakdown ---")
    print(f"  hybrid_batch calls: {hybrid_batch_calls}")
    print(f"  qwen_batch calls:   {qwen_batch_calls}")
    print(f"  DeepSeek calls:     {deepseek_calls}  (failed: {deepseek_fail})")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
