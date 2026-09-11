"""The frozen June specimen (operator ruling 2026-09-11 s2).

Loads ONLY roles/Arachne/archive/run_2026-06-04/ after verifying its
MANIFEST (LF-normalised sha256, comms/manifest.py). No live landscape, no
new edge, no crawl. Everything an analysis needs is derived here so every
downstream number cites one provenance.

Facts the loader establishes (and tests):
- The archive holds TWO segments. Segment 1: ticks 1-45, 10:20:11Z to
  10:21:00Z (crawler ids 1..N). Then a --fresh restart at 10:22:20Z reset
  the tick counter and the id counter: segment 2 runs ticks 1-700 to
  11:21:33Z. Crawler ids COLLIDE across segments (groups-1-8 exists in
  both); a crawler is identified by (segment, id). The fabric file is
  append-only across both.
- Every edge maps to a segment tick by interpolating born_at between the
  lineage log's (at, tick) anchors (~5 s per tick).
- The crawler's own fitness (agents/arachne/crawler.py at 3b9d9ed15) is
  reconstructed per tick from the edges it persisted: progress =
  2*new_nodes + new_edges per step, window 16, times (1 - 0.6 * mean
  null_p), null 0.5 on a step with no edge. The reconstruction is
  validated against the parent_fitness the swarm logged at every branch
  (positive control: the same function, computed two ways).
"""
from __future__ import annotations

import json
import sys
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[3]
ARCHIVE = REPO / "roles" / "Arachne" / "archive" / "run_2026-06-04"
SEGMENT_BOUNDARY = "2026-06-04T10:21:30+00:00"     # between the last seg-1 event (10:21:00) and the first seg-2 edge
WINDOW = 16
DEATH_STALL = 12
CODE_SHA = "3b9d9ed15"      # the crawler.py/swarm.py that ran the archived segments (see ARCHAEOLOGY)


def _iso(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def verify_manifest() -> Dict[str, str]:
    """Raise if any archive file disagrees with MANIFEST.md."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from comms.manifest import artifact_hash as file_sha256  # type: ignore
    man = (ARCHIVE / "MANIFEST.md").read_text(encoding="utf-8")
    out = {}
    for line in man.splitlines():
        if not line.startswith("- "):
            continue
        name, _, sha = line[2:].partition("  sha256:")
        actual = file_sha256(ARCHIVE / name.strip())
        if actual != sha.strip():
            raise RuntimeError("specimen tampered: {} {} != manifest {}".format(name, actual, sha))
        out[name.strip()] = sha.strip()
    return out


class Specimen:
    def __init__(self, verify: bool = True):
        self.hashes = verify_manifest() if verify else {}
        self.lineage: List[dict] = [json.loads(l) for l in (ARCHIVE / "lineage.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.edges: List[dict] = [json.loads(l) for l in (ARCHIVE / "edges.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.swarm_state = json.loads((ARCHIVE / "swarm_state.json").read_text(encoding="utf-8"))
        self.population = json.loads((ARCHIVE / "population.json").read_text(encoding="utf-8"))
        b = _iso(SEGMENT_BOUNDARY)
        for r in self.lineage:
            r["segment"] = 1 if _iso(r["at"]) < b else 2
        for i, e in enumerate(self.edges):
            e["order"] = i
            e["segment"] = 1 if _iso(e["born_at"]) < b else 2
        self._anchors = self._build_anchors()
        for e in self.edges:
            e["tick"] = self.tick_of(e["segment"], e["born_at"])
        # global novelty in append order (what fabric.add saw)
        seen = set()
        for e in self.edges:
            e["new_nodes"] = 0
            for n in (e["src"], e["dst"]):
                if n not in seen:
                    seen.add(n); e["new_nodes"] += 1
        self.crawlers = self._crawler_table()

    # -- tick mapping --------------------------------------------------------
    def _build_anchors(self) -> Dict[int, Tuple[List[float], List[int]]]:
        per: Dict[int, List[Tuple[float, int]]] = defaultdict(list)
        for r in self.lineage:
            per[r["segment"]].append((_iso(r["at"]), r["tick"]))
        out = {}
        for seg, pts in per.items():
            pts.sort()
            out[seg] = ([t for t, _ in pts], [k for _, k in pts])
        return out

    def tick_of(self, segment: int, at: str) -> int:
        ts, ks = self._anchors[segment]
        t = _iso(at)
        i = bisect_right(ts, t)
        if i == 0:
            # before the first anchor: extrapolate at the segment's mean pace
            pace = (ts[-1] - ts[0]) / max(1, ks[-1] - ks[0])
            return max(1, int(round(ks[0] - (ts[0] - t) / pace)))
        if i >= len(ts):
            pace = (ts[-1] - ts[0]) / max(1, ks[-1] - ks[0])
            return int(round(ks[-1] + (t - ts[-1]) / pace))
        t0, t1, k0, k1 = ts[i - 1], ts[i], ks[i - 1], ks[i]
        if k1 == k0 or t1 == t0:
            return k0
        return int(round(k0 + (t - t0) * (k1 - k0) / (t1 - t0)))

    # -- crawler table -------------------------------------------------------
    def _crawler_table(self) -> Dict[Tuple[int, str], dict]:
        C: Dict[Tuple[int, str], dict] = {}
        founders = ["mathlib-0-1", "lmfdb-0-2", "algolib-0-3", "oeis-0-4", "knots-0-5", "groups-0-6", "feral-0-7"]
        for seg in (1, 2):
            for f in founders:
                C[(seg, f)] = {"segment": seg, "id": f, "born_tick": 0, "origin": "founder", "parent": None,
                               "landscape": f.split("-")[0], "generation": 0, "death_tick": None, "death_reason": None}
        for r in self.lineage:
            seg = r["segment"]
            if r["event"] == "branch":
                C[(seg, r["child"])] = {"segment": seg, "id": r["child"], "born_tick": r["tick"], "origin": "branch",
                                        "parent": r["parent"], "landscape": r["child"].split("-")[0],
                                        "generation": int(r["child"].split("-")[1]), "death_tick": None, "death_reason": None,
                                        "parent_fitness_logged": r["parent_fitness"], "child_ruleset": r["child_ruleset"]}
            elif r["event"] == "floor_revive":
                C[(seg, r["id"])] = {"segment": seg, "id": r["id"], "born_tick": r["tick"], "origin": "floor_revive",
                                     "parent": None, "landscape": r["landscape"], "generation": 0,
                                     "death_tick": None, "death_reason": None}
            elif r["event"] in ("revive",):
                C[(seg, r["id"])] = {"segment": seg, "id": r["id"], "born_tick": r["tick"], "origin": "revive",
                                     "parent": None, "landscape": r["landscape"], "generation": 0,
                                     "death_tick": None, "death_reason": None}
        for r in self.lineage:
            if r["event"] == "death":
                key = (r["segment"], r["id"])
                if key not in C:
                    C[key] = {"segment": r["segment"], "id": r["id"], "born_tick": None, "origin": "unknown", "parent": None,
                              "landscape": r["id"].split("-")[0], "generation": r.get("generation"), "death_tick": None, "death_reason": None}
                C[key]["death_tick"] = r["tick"]; C[key]["death_reason"] = r["reason"]; C[key]["total_edges_logged"] = r["total_edges"]
        end_tick = {1: max(k for k in self._anchors[1][1]), 2: self.swarm_state["tick"]}
        for key, c in C.items():
            c["end_tick"] = c["death_tick"] if c["death_tick"] is not None else end_tick[c["segment"]]
            c["alive_at_end"] = c["death_tick"] is None
        by = defaultdict(list)
        for e in self.edges:
            if e["crawler"] in ("rosetta", "operational"):
                continue
            by[(e["segment"], e["crawler"])].append(e)
        for key, c in C.items():
            es = by.get(key, [])
            c["edges"] = len(es)
            c["nodes_introduced"] = sum(e["new_nodes"] for e in es)
            c["null_discounted_nodes"] = round(sum(e["new_nodes"] * (1.0 - e["null_p"]) for e in es), 3)
            c["first_edge_tick"] = min((e["tick"] for e in es), default=None)
            c["last_edge_tick"] = max((e["tick"] for e in es), default=None)
            c["lifetime_ticks"] = (c["end_tick"] - c["born_tick"]) if c["born_tick"] is not None else None
        return C

    # -- the mechanism's own fitness, per tick ---------------------------------
    def fitness_series(self, segment: int, cid: str) -> Dict[int, float]:
        """fitness after each tick the crawler stepped (first step = born_tick+1
        for a branch child, tick 1 for a founder), exactly as crawler.py computes
        it: window of the last 16 steps of progress and mean null."""
        c = self.crawlers[(segment, cid)]
        steps: Dict[int, Tuple[int, List[float]]] = defaultdict(lambda: (0, []))
        for e in self.edges:
            if e["segment"] == segment and e["crawler"] == cid:
                p, nl = steps[e["tick"]]
                steps[e["tick"]] = (p + 2 * e["new_nodes"] + 1, nl + [e["null_p"]])
        first = (c["born_tick"] or 0) + 1
        last = c["end_tick"]
        prog: List[float] = []; nulls: List[float] = []; out: Dict[int, float] = {}
        for t in range(first, last + 1):
            p, nl = steps.get(t, (0, []))
            prog.append(p); nulls.append(sum(nl) / len(nl) if nl else 0.5)
            w_p = prog[-WINDOW:]; w_n = nulls[-WINDOW:]
            out[t] = (sum(w_p) / len(w_p)) * (1.0 - 0.6 * (sum(w_n) / len(w_n)))
        return out

    def fitness_at(self, segment: int, cid: str, tick: int) -> Optional[float]:
        s = self.fitness_series(segment, cid)
        if not s:
            return None
        ks = [k for k in s if k <= tick]
        return s[max(ks)] if ks else None

    def validate_reconstruction(self) -> dict:
        """Positive control: logged parent_fitness at each branch vs the
        reconstruction at the same tick. Returns the agreement table."""
        rows = []
        for r in self.lineage:
            if r["event"] != "branch":
                continue
            rec = self.fitness_at(r["segment"], r["parent"], r["tick"])
            rows.append({"segment": r["segment"], "tick": r["tick"], "parent": r["parent"],
                         "logged": r["parent_fitness"], "reconstructed": None if rec is None else round(rec, 3),
                         "abs_err": None if rec is None else round(abs(rec - r["parent_fitness"]), 3)})
        errs = [x["abs_err"] for x in rows if x["abs_err"] is not None]
        return {"n": len(rows), "n_reconstructed": len(errs),
                "within_0.05": sum(1 for e in errs if e <= 0.05), "within_0.10": sum(1 for e in errs if e <= 0.10),
                "max_abs_err": max(errs) if errs else None, "rows": rows}


if __name__ == "__main__":
    S = Specimen()
    print("hashes verified:", len(S.hashes))
    print("edges", len(S.edges), "seg1", sum(e["segment"] == 1 for e in S.edges), "seg2", sum(e["segment"] == 2 for e in S.edges))
    print("crawlers", len(S.crawlers))
    v = S.validate_reconstruction()
    print({k: v[k] for k in v if k != "rows"})
    for row in v["rows"][:12]:
        print(row)
