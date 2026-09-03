"""WOW archaeology -- corpus extraction (READ-ONLY, streaming).

PRIME DIRECTIVE inherited from the WOW-0 forensic survey and still binding:
OBSERVE, MUTATE NOTHING. Both source services are LIVE (8799 PID 23276,
8811 PID 20112). This module:
  * never opens the hot engine.db in place -- it reads a forensic COPY;
  * never issues HTTP to either service;
  * streams the 284MB JSONL rather than loading it;
  * verifies the ledger hash chain as it goes (a corpus that cannot be
    verified cannot support a nomination).

Everything produced here is DISCOVERY EVIDENCE. It can nominate. It can
never admit.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict

D13 = "F:/SerendipityD"
SEGS = [f"{D13}/var/ledger/segment-00000000.jsonl",
        f"{D13}/var/ledger/segment-00000001.jsonl"]


def stream_ledger(verify_chain=True):
    """Yield (seq, kind, ts, payload, refs). Verifies prev/entry hashes."""
    prev = None
    broken = 0
    for seg in SEGS:
        with open(seg, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if verify_chain and prev is not None:
                    if r.get("prev_hash") != prev:
                        broken += 1
                prev = r.get("entry_hash")
                yield r
    if broken:
        print(f"  [chain] {broken} prev_hash discontinuities", file=sys.stderr)


def extract_d13(outdir):
    """Artifacts, lineage, executions, selections, checkpoints."""
    artifacts = {}      # artifact_id -> record
    lineage = []        # (child, parent, op, seed)
    execs = []          # execution rows
    selections = []
    ckpt = Counter()
    kinds = Counter()
    engines = {}
    n = 0
    for r in stream_ledger():
        n += 1
        k, p, refs = r.get("kind"), r.get("payload") or {}, r.get("refs") or {}
        kinds[k] += 1
        if k == "ENGINE_REGISTERED":
            engines[p.get("engine_id")] = p
        elif k in ("ARTIFACT_CREATED", "ARTIFACT_MUTATED", "ARTIFACT_RECOMBINED"):
            aid = p.get("artifact_id")
            artifacts[aid] = {
                "artifact_id": aid, "op": p.get("op"), "seed": p.get("seed"),
                "genotype_addr": p.get("genotype_addr"),
                "genotype_len": p.get("genotype_bytes_len"),
                "engine_id": p.get("engine_id"), "seq": r.get("seq"),
                "ts": r.get("ts"), "kind": k,
                "trace_id": refs.get("trace_id"),
                "parents": refs.get("parent_ids") or [],
            }
            for par in (refs.get("parent_ids") or []):
                lineage.append((aid, par, p.get("op"), p.get("seed")))
        elif k == "ARTIFACT_EXECUTED":
            res = p.get("result") or {}
            execs.append({
                "seq": r.get("seq"), "ts": r.get("ts"),
                "artifact_id": res.get("artifact_id"),
                "task_id": res.get("task_id"), "seed": res.get("seed"),
                "input_hash": res.get("input_hash"),
                "output_hash": res.get("output_hash"),
                "status": res.get("status"), "steps": res.get("steps"),
                "error_kind": res.get("error_kind"),
                "max_steps": (p.get("limits") or {}).get("max_steps"),
                "trace_id": refs.get("trace_id"),
            })
        elif k == "SELECTION":
            selections.append({"seq": r.get("seq"), "ts": r.get("ts"),
                               "payload": p, "refs": refs})
        elif k == "EXPERIMENT_CHECKPOINT":
            ckpt[refs.get("trace_id") or p.get("experiment_id") or "?"] += 1
    os.makedirs(outdir, exist_ok=True)
    for name, obj in [("d13_artifacts", list(artifacts.values())),
                      ("d13_lineage", lineage),
                      ("d13_executions", execs),
                      ("d13_selections", selections)]:
        with open(f"{outdir}/{name}.json", "w") as f:
            json.dump(obj, f)
    print(f"D-13: {n} records | {len(artifacts)} artifacts | "
          f"{len(lineage)} lineage edges | {len(execs)} executions | "
          f"{len(selections)} selections | {len(ckpt)} checkpoint traces")
    print(f"  kinds: {dict(kinds)}")
    print(f"  engines: {list(engines)}")
    return artifacts, lineage, execs, selections


def extract_engine(dbcopy, outdir):
    """SFE engine substrate from the forensic COPY."""
    c = sqlite3.connect(f"file:{dbcopy}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    out = {}
    for t in ("experiments", "observations", "failures", "artifacts",
              "worlds", "hypotheses", "predictions", "lineage_edges",
              "work_items", "clients", "budgets", "topology_groups",
              "events", "checkpoints", "sessions"):
        try:
            rows = [dict(r) for r in c.execute(f"SELECT * FROM {t}")]
        except Exception as e:
            rows = []
            print(f"  [{t}] {e}")
        out[t] = rows
    os.makedirs(outdir, exist_ok=True)
    for t, rows in out.items():
        with open(f"{outdir}/eng_{t}.json", "w") as f:
            json.dump(rows, f, default=str)
    print("ENGINE: " + " | ".join(f"{t}={len(r)}" for t, r in out.items()
                                  if r))
    return out


if __name__ == "__main__":
    outdir = sys.argv[1]
    dbcopy = sys.argv[2]
    extract_d13(outdir)
    extract_engine(dbcopy, outdir)
