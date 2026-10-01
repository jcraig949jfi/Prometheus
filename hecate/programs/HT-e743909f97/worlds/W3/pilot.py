"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only."""
import json, sys, time
import core

def main():
    t0 = time.process_time()
    with open("pilot_rows.jsonl", "w", encoding="utf-8") as f:
        for seed in core.SEEDS:
            for arm, fn in (("POSITIVE_CONTROL", core.run_positive), ("CHEAT", core.run_cheat),
                            ("NULL_TWIN", core.run_null_twin)):
                row = fn(seed); row["attempt"] = int(sys.argv[1]) if len(sys.argv) > 1 else 1
                f.write(json.dumps(row) + "\n"); f.flush()
    cpu = time.process_time() - t0
    with open("pilot_cpu.json", "w") as g:
        json.dump({"cpu_seconds": cpu}, g)
    print("cpu s", round(cpu, 1))

if __name__ == "__main__":
    main()
