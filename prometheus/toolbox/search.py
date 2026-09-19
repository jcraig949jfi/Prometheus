"""Search ABOVE the execution kernel (directive s18; overnight C26).

A Selector proposes PlayerSpecs from archive ROWS; the kernel runs them as an ordinary Experiment whose
`players` axis is swept (one player per sweep point); receipts are ingested into rows. The archive is a
JSONL file: `elite` rows (one per evaluated player, with fingerprint, descriptor, objective, receipt id and
path) and `GEN_DONE` marker rows. A generation is COMMITTED only by its marker; evolve() on a workdir that
already holds rows resumes after the last marker, re-running any generation that has no marker (its receipts
file, if any, is left as evidence and a fresh attempt file is used). Seeds derive from (seed, gen) so an
uninterrupted run and a resumed run reach the same rows.

    evolve(template, ref("selector.truncation.v1", keep=3, n=6), generations=4, workdir=..., seed=11)

The kernel does not know it is inside a search; nothing here changes the IR, the executor or the receipts.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List

from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox.ir import Experiment
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.ref.worlds import stream

ARCHIVE = "archive.jsonl"


# ------------------------------------------------------------------------------------------ rows
def load_rows(path) -> List[dict]:
    p = pathlib.Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _append(path, row: dict) -> None:
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"); f.flush()


def committed_rows(rows: List[dict]) -> List[dict]:
    """Elite rows that belong to a COMMITTED generation, in order: rows are buffered until the GEN_DONE marker of
    their generation; a GEN_ABANDONED marker (or a GEN_DONE for a different generation) drops the buffer."""
    out: List[dict] = []; buf: List[dict] = []
    for r in rows:
        k = r["kind"]
        if k == "elite":
            buf.append(r)
        elif k == "GEN_DONE":
            out += [b for b in buf if b["gen"] == r["gen"]]; buf = []
        elif k == "GEN_ABANDONED":
            buf = []
    return out


def elites_by_cell(rows: List[dict]) -> Dict[tuple, List[dict]]:
    cells: Dict[tuple, List[dict]] = {}
    for r in rows:
        if r["kind"] != "elite":
            continue
        key = tuple(r["descriptor"]); cur = cells.get(key)
        if cur is None or (r["objective"] is not None and (cur[0]["objective"] is None or r["objective"] > cur[0]["objective"])):
            cells[key] = [r]
    return cells


# ------------------------------------------------------------------------------------------ selectors
class TruncationSelector:
    kind = "selector.truncation.v1"

    def __init__(self, keep: int = 3, n: int = 6, mutation: str = "transform.point_mutation.v1"):
        self.keep = keep; self.n = n; self.mutation = mutation

    def manifest(self) -> dict:
        return {"kind": self.kind, "keep": self.keep, "n": self.n, "mutation": self.mutation}

    def propose(self, archive_rows: List[dict], rng_seed: int, n: int) -> List[PlayerSpec]:
        from prometheus.toolbox.registry import default_registry
        reg = default_registry(); t = reg.make(self.mutation); s = stream("truncation", rng_seed)
        elites = sorted((r for r in archive_rows if r["kind"] == "elite" and r["objective"] is not None), key=lambda r: (-r["objective"], r["fingerprint"]))[:self.keep]
        if not elites:
            return [random_statemachine(rng_seed * 131 + i, meta={"gen0": True}) for i in range(n)]
        out: List[PlayerSpec] = []
        for i in range(n):
            parent = elites[s.below(len(elites))]["player"]
            out.append(t.apply(parent, rng_seed * 977 + i))
        return out

    def ingest(self, receipts: List[dict]) -> List[dict]:
        return _rows_from_receipts(receipts)


class MapElitesSelector(TruncationSelector):
    kind = "selector.map_elites.v1"

    def __init__(self, n: int = 8, mutation: str = "transform.point_mutation.v1"):
        super().__init__(keep=0, n=n, mutation=mutation)

    def manifest(self) -> dict:
        return {"kind": self.kind, "n": self.n, "mutation": self.mutation}

    def propose(self, archive_rows: List[dict], rng_seed: int, n: int) -> List[PlayerSpec]:
        from prometheus.toolbox.registry import default_registry
        reg = default_registry(); t = reg.make(self.mutation); s = stream("map_elites", rng_seed)
        cells = list(elites_by_cell(archive_rows).values())
        if not cells:
            return [random_statemachine(rng_seed * 131 + i, meta={"gen0": True}) for i in range(n)]
        return [t.apply(cells[s.below(len(cells))][0]["player"], rng_seed * 977 + i) for i in range(n)]


def _rows_from_receipts(receipts: List[dict]) -> List[dict]:
    """One elite row per PLAYER (a sweep point), aggregating its seeds: objective = mean over seeds (None if any
    seed had none), descriptor = the first seed's, receipt ids and seeds listed. (C26b: one row per receipt made
    a player with two seeds look like two elites.)"""
    by: Dict[str, dict] = {}
    for r in receipts:
        if r["arm"] != "primary":
            continue
        key = json.dumps(r["sweep_point"], sort_keys=True)
        desc = (r["science"].get("observations", {}).get("observer.descriptor.v1") or {}).get("descriptor", [])
        row = by.setdefault(key, {"kind": "elite", "player": r["_player_manifest"], "fingerprint": r["science"]["player_fingerprints"]["0"]["hash"],
                                  "descriptors": [], "objectives": [], "receipt_ids": [], "seeds": []})
        row["descriptors"].append(list(desc)); row["objectives"].append((r["science"].get("objective") or {}).get("value"))
        row["receipt_ids"].append(r["receipt_id"]); row["seeds"].append(r["seed"])
    rows = []
    for row in by.values():
        vals = row.pop("objectives")
        row["objective"] = None if any(v is None for v in vals) or not vals else sum(vals) / len(vals)
        ds = [d for d in row["descriptors"] if d]
        # C27: the cell key is the element-wise floor(mean + 0.5) over seeds, never one seed's descriptor
        row["descriptor"] = [int(sum(d[i] for d in ds) / len(ds) + 0.5) for i in range(len(ds[0]))] if ds else []
        rows.append(row)
    return rows


def _abandoned_count(rows: List[dict]) -> int:
    n = 0; buf = 0
    for r in rows:
        if r["kind"] == "elite":
            buf += 1
        elif r["kind"] == "GEN_DONE":
            buf = 0
        elif r["kind"] == "GEN_ABANDONED":
            n += buf; buf = 0
    return n


# ------------------------------------------------------------------------------------------ driver
def _run_generation(template: Experiment, players: List[PlayerSpec], gen: int, seed: int, workdir: pathlib.Path, registry) -> List[dict]:
    from prometheus.toolbox.backends.local import execute
    e = Experiment.from_dict(template.to_dict())
    e.players = [players[0].manifest()]
    e.sweep = {"players": [[p.manifest()] for p in players]}
    e.seed_policy = dict(template.seed_policy, base=seed * 100003 + gen * 1009)
    e.provenance = dict(template.provenance, search_gen=gen)
    attempt = 0
    while (workdir / ("gen_%03d_a%d.jsonl" % (gen, attempt))).exists():
        attempt += 1                                             # a crashed attempt's file stays as evidence
    path = workdir / ("gen_%03d_a%d.jsonl" % (gen, attempt))
    rep = execute(e.compile("local", registry).job, path, registry)
    receipts = read_all(path)
    for r in receipts:
        if r["arm"] == "primary":
            r["_player_manifest"] = r["sweep_point"]["players"][0]
    return receipts


def evolve(template: Experiment, selector_ref: dict, generations: int, workdir, seed: int, registry=None) -> dict:
    from prometheus.toolbox.registry import default_registry
    registry = registry or default_registry()
    sel = registry.make(selector_ref["kind"], **selector_ref.get("params", {}))
    workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    archive = workdir / ARCHIVE
    rows = load_rows(archive)
    done = [r["gen"] for r in rows if r["kind"] == "GEN_DONE"]
    start = (max(done) + 1) if done else 0
    committed = committed_rows(rows)
    if len(committed) != sum(1 for r in rows if r["kind"] == "elite") - _abandoned_count(rows):
        # trailing rows with no marker: an interrupted generation. Mark them abandoned so no reader trusts them.
        _append(archive, {"kind": "GEN_ABANDONED", "gen": start, "reason": "rows without a GEN_DONE marker at resume"})
    for gen in range(start, generations):
        players = sel.propose(committed, seed * 7919 + gen, sel.n)
        receipts = _run_generation(template, players, gen, seed, workdir, registry)
        new_rows = [dict(r, gen=gen) for r in sel.ingest(receipts)]
        for r in new_rows:
            _append(archive, r)
        _append(archive, {"kind": "GEN_DONE", "gen": gen, "n": len(new_rows), "selector": sel.manifest()})
        committed += new_rows
    return {"generations_done": generations, "resumed_from_gen": start, "archive": str(archive), "elites": len(committed)}
