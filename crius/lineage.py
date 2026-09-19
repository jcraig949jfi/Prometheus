"""Lineage readout (operator GO 2026-09-19): ancestral gradients toward acquired state.

For a search run: walk the ancestry of the final-population top candidate and
tabulate, per ancestor, fitness, successes, interactions, store trace (WS_/BLK_
executions), blocks created, invocations and workspace bytes kept, so a
gradient toward keeping/using state is visible if it exists. Also a per-
iteration census over ALL candidates: how many kept state, how many invoked
a block, and whether those had higher fitness than their contemporaries.

CLI: python -m crius.lineage --run RUN_ID   (writes crius/runs/RUN_ID/LINEAGE.md)
"""

from __future__ import annotations

import argparse
import json
import os

from . import receipts, vm

STORE_KEYS = ("WS_READ", "WS_WRITE", "WS_APPEND", "WS_SREAD", "WS_SLEN", "WS_REC_NEW", "WS_REC_GET", "WS_REC_SET",
              "WS_LINK", "WS_LINKS", "WS_LINK_GET", "WS_ALLOC", "WS_FREE", "WS_FIND", "BLK_NEW", "BLK_APPEND",
              "BLK_PATCH", "BLK_COPY", "BLK_COMPOSE", "BLK_DELETE", "BLK_INVOKE", "BLK_LEN", "BLK_COUNT",
              "BLK_STATE_GET", "BLK_STATE_SET", "BLK_REC_BEGIN", "BLK_REC_END")


def _agg(rec):
    ps = list(rec["per_seed"].values())
    n = len(ps)
    tr = {}
    for p in ps:
        for k, v in p.get("store_trace", {}).items():
            tr[k] = tr.get(k, 0) + v
    reads = sum(v for k, v in tr.items() if k in ("WS_READ", "WS_SREAD", "WS_REC_GET", "WS_LINK_GET", "WS_FIND", "BLK_STATE_GET", "WS_LINKS", "WS_SLEN", "BLK_LEN", "BLK_COUNT"))
    writes = sum(v for k, v in tr.items() if k in ("WS_WRITE", "WS_APPEND", "WS_REC_NEW", "WS_REC_SET", "WS_LINK", "BLK_NEW", "BLK_APPEND", "BLK_PATCH", "BLK_COPY", "BLK_COMPOSE", "BLK_STATE_SET", "BLK_REC_END"))
    return {
        "fitness": rec["fitness"], "successes": sum(p["successes"] for p in ps) / n,
        "interactions": sum(p["interactions_total"] for p in ps) / n,
        "store_reads": reads, "store_writes": writes, "invokes": tr.get("BLK_INVOKE", 0),
        "blocks_created": sum(p["blocks_created_total"] for p in ps), "invoked": sum(p["artifacts_invoked_total"] for p in ps),
        "ws_bytes": sum(p["workspace_bytes_final"] for p in ps), "invalid": sum(p.get("invalid_actions_total", 0) for p in ps),
        "length": rec["length"],
    }


def analyse(run_dir: str) -> str:
    cands = {}
    by_it = {}
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            cands[r["candidate_id"]] = r
            by_it.setdefault(r["iteration"], []).append(r)
    best = receipts.read_json(os.path.join(run_dir, "best.json"))
    top_id = sorted(best["final_population"], key=lambda p: (-p["fitness"], p["length"], p["candidate_id"]))[0]["candidate_id"]
    L = []
    P = L.append
    P("LINEAGE READOUT run=%s arm=%s" % (best["run_id"], best["arm"]))
    # ---- ancestry of the final-population top
    chain = []
    cur = cands[top_id]
    while cur is not None:
        chain.append(cur)
        cur = cands.get(cur["parent_id"]) if cur["parent_id"] else None
    chain.reverse()
    P("ANCESTRY of final-population top %s (%d steps, oldest first; every 1/12th plus the last 6)" % (top_id, len(chain) - 1))
    P("  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification")
    step = max(1, len(chain) // 12)
    picks = list(range(0, len(chain), step)) + list(range(max(0, len(chain) - 6), len(chain)))
    seen = set()
    for i in picks:
        if i in seen:
            continue
        seen.add(i)
        r = chain[i]
        a = _agg(r)
        P("  %3d  %7.3f  %4.1f  %5.0f  %5d  %6d  %6d  %9d  %6d  %6d  %3d  %s" % (
            r["iteration"], a["fitness"], a["successes"], a["interactions"], a["store_reads"], a["store_writes"], a["invokes"],
            a["blocks_created"], a["invoked"], a["ws_bytes"], a["length"], r["modification"][:40]))
    # gradient statistics along the lineage
    ks = [_agg(r) for r in chain]
    first_half = ks[: len(ks) // 2] or ks
    second_half = ks[len(ks) // 2:] or ks

    def mean(xs, k):
        return sum(x[k] for x in xs) / len(xs)
    P("  gradient (mean first half -> second half of the lineage): reads %.0f -> %.0f, writes %.0f -> %.0f, "
      "invokes %.1f -> %.1f, blocks %.1f -> %.1f, wsBytes %.0f -> %.0f, successes %.1f -> %.1f" % (
          mean(first_half, "store_reads"), mean(second_half, "store_reads"), mean(first_half, "store_writes"), mean(second_half, "store_writes"),
          mean(first_half, "invokes"), mean(second_half, "invokes"), mean(first_half, "blocks_created"), mean(second_half, "blocks_created"),
          mean(first_half, "ws_bytes"), mean(second_half, "ws_bytes"), mean(first_half, "successes"), mean(second_half, "successes")))
    # ---- per-iteration census over all candidates
    P("CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best")
    for it in sorted(by_it):
        if it % 25 != 0 and it != max(by_it):
            continue
        rows = by_it[it]
        aggs = [_agg(r) for r in rows]
        kept = [a for a in aggs if a["ws_bytes"] > 0 or a["invoked"] > 0]
        notk = [a for a in aggs if not (a["ws_bytes"] > 0 or a["invoked"] > 0)]
        inv = [a for a in aggs if a["invoked"] > 0]
        P("  %3d  %3d  %5d  %5d  %9s  %9s  %7.3f" % (
            it, len(rows), len(kept), len(inv), ("%.3f" % (sum(a["fitness"] for a in kept) / len(kept))) if kept else "--",
            ("%.3f" % (sum(a["fitness"] for a in notk) / len(notk))) if notk else "--", max(a["fitness"] for a in aggs)))
    # ---- did any candidate that invoked blocks ever enter the top 8 of its iteration?
    n_top_inv = 0
    n_inv = 0
    for it, rows in by_it.items():
        ranked = sorted(rows, key=lambda r: -r["fitness"])[:8]
        for r in rows:
            a = _agg(r)
            if a["invoked"] > 0:
                n_inv += 1
                if r in ranked:
                    n_top_inv += 1
    P("  candidates that invoked a block: %d; of those in their iteration's top 8: %d" % (n_inv, n_top_inv))
    # ---- mechanism of the top: listing + trace
    r = cands[top_id]
    a = _agg(r)
    P("TOP MECHANISM %s: fitness %.3f succ %.1f inter %.0f reads %d writes %d invokes %d blocks %d wsBytes %d invalid %d" % (
        top_id, a["fitness"], a["successes"], a["interactions"], a["store_reads"], a["store_writes"], a["invokes"], a["blocks_created"], a["ws_bytes"], a["invalid"]))
    tr = {}
    for p in r["per_seed"].values():
        for k, v in p.get("store_trace", {}).items():
            tr[k] = tr.get(k, 0) + v
    P("  trace: %s" % json.dumps(dict(sorted(tr.items(), key=lambda kv: -kv[1]))))
    for line in vm.disassemble(vm.program_from_json(r["program"])).splitlines():
        P("    " + line)
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    run_dir = args.run if os.path.isdir(args.run) else os.path.join("crius", "runs", args.run)
    text = analyse(run_dir)
    with open(os.path.join(run_dir, "LINEAGE.md"), "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
