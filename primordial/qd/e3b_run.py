"""E3b: FalkorDB load-time genes, repeated restarts, round-robin, with a null gene.

  python -m primordial.qd.e3b_run [--rounds 5] [--reps 7] [--genes ...] [--tag full]

Posted on the bus before the run (E3b-falkordb-load-genes-repeated):
  genes    default_a, cache1, cache100, omp1, omp3, default_b (default_b == default_a: NULL)
  design   R rounds; inside each round every gene gets one fresh container (round-robin)
  measure  per restart: E3's 6 reference-variant queries, median of `reps` each -> total_ms
  WIN      gene median total over rounds < MIN of default_a's totals
  NULL     default_b must not win (else INDETERMINATE)
  CHEAT    first restart: gate kills Q1 v3 (drop DISTINCT) and Q2 v3 (LIMIT 5), passes honest v0-v2
Reuses E3's engine launcher, corpus builder and query runner unchanged.
"""
from __future__ import annotations

import argparse
import json
import time
from statistics import median

import psutil
import redis

from primordial.qd import e3_run as E3

EXP = "E3b-falkordb-load-genes-repeated"
ROWS = E3.ROWS.with_name(f"{EXP}.jsonl")
GENES = {  # name -> (CACHE_SIZE, OMP_THREAD_COUNT); None = stock default
    "default_a": (None, None), "cache1": (1, None), "cache100": (100, None),
    "omp1": (None, 1), "omp3": (None, 3), "default_b": (None, None),
}


def emit(row):
    row["ts"] = time.time()
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=5); p.add_argument("--reps", type=int, default=7)
    p.add_argument("--genes", default=",".join(GENES)); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full")
    a = p.parse_args()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    genes = a.genes.split(",")
    ref: dict[str, str] = {}
    totals = {g: [] for g in genes}
    first = True
    for rnd in range(a.rounds):
        for gene in genes:
            cache, omp = GENES[gene]
            boot_s = E3.start_engine(a.port, cache, omp)
            r = redis.Redis(host="127.0.0.1", port=a.port)
            fp = E3.ensure_corpus(r)
            psutil.cpu_percent(None)
            total, hashes = 0.0, {}
            for qid, vid, cheat, cypher in E3.QUERIES:
                if not first and vid != 0:
                    continue
                h, n, med, internal, spread = E3.run_query(r, cypher, a.reps)
                if vid == 0:
                    hashes[qid] = h
                    ref.setdefault(qid, h)
                    total += med if med is not None else float("nan")
                emit({"exp_id": EXP, "tag": a.tag, "kind": "query", "round": rnd, "gene": gene, "query": qid,
                      "variant": vid, "cheat": cheat, "rows_sha256": h, "n_rows": n, "gate": h == ref[qid],
                      "wall_ms_median": med, "internal_ms_median": internal, "wall_ms_p90_p10": spread,
                      "boot_s": round(boot_s, 2), "corpus_fp": fp})
            cpu = psutil.cpu_percent(None)
            gate_ok = all(hashes[q] == ref[q] for q in hashes)
            totals[gene].append(total)
            emit({"exp_id": EXP, "tag": a.tag, "kind": "restart", "round": rnd, "gene": gene,
                  "cache_size": cache, "omp_thread_count": omp, "total_ms_v0": round(total, 3),
                  "gate_v0_all": gate_ok, "host_cpu_pct": cpu, "boot_s": round(boot_s, 2)})
            print(f"round {rnd} {gene} total {total:.1f} ms gate {gate_ok} cpu {cpu}", flush=True)
            first = False
    base = min(totals["default_a"]) if totals.get("default_a") else None
    summary = {g: {"totals": [round(t, 2) for t in totals[g]], "median": round(median(totals[g]), 2),
                   "wins": (base is not None and g != "default_a" and median(totals[g]) < base)} for g in genes}
    emit({"exp_id": EXP, "tag": a.tag, "kind": "summary", "default_a_min": base, "genes": summary})
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
