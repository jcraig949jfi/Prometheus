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
from typing import Any, Dict, List, Optional

from prometheus.toolbox.contracts import PlayerSpec, component_manifest_hash
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


class SelectorNeedsScalar(ValueError):
    """C94: a rank-based selector met a vector objective without (or with an unknown) `rank`. Raised BEFORE any
    generation is written, with the component keys named, so the designer can say rank=<key>."""


def scalar_objective(row: dict, rank: Optional[str] = None):
    """The number a selector ranks by: the row's objective if scalar, its `rank` component if a vector; None if
    absent. A vector without a usable rank raises SelectorNeedsScalar (the keys are in the message)."""
    v = row.get("objective")
    if v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, dict):
        if rank is None or rank not in v:
            raise SelectorNeedsScalar("objective is a vector with components %s; the selector needs rank=<one of them> (got rank=%r)" % (sorted(v), rank))
        return v[rank]
    raise SelectorNeedsScalar("objective value of unsupported shape %s; a selector needs a number or a named component" % type(v).__name__)


def elites_by_cell(rows: List[dict], rank: Optional[str] = None) -> Dict[tuple, List[dict]]:
    cells: Dict[tuple, List[dict]] = {}
    for r in rows:
        if r["kind"] != "elite":
            continue
        key = tuple(r["descriptor"]); cur = cells.get(key); v = scalar_objective(r, rank)
        if cur is None or (v is not None and (scalar_objective(cur[0], rank) is None or v > scalar_objective(cur[0], rank))):
            cells[key] = [r]
    return cells


# ------------------------------------------------------------------------------------------ selectors
def _gen0(registry, representation: str, rng_seed: int, n: int) -> List[PlayerSpec]:
    """C73: generation 0 comes from the REGISTERED generator of the chosen representation (the registry row's
    factory takes a seed), so a selector evolves any representation without subclassing."""
    gen = registry.get(representation).factory
    return [gen(rng_seed * 131 + i, meta={"gen0": True}) for i in range(n)]


class TruncationSelector:
    kind = "selector.truncation.v1"

    def __init__(self, keep: int = 3, n: int = 6, mutation: str = "transform.point_mutation.v1", representation: str = "statemachine.v1", rank: Optional[str] = None):
        self.keep = keep; self.n = n; self.mutation = mutation; self.representation = representation; self.rank = rank

    def manifest(self) -> dict:
        return {"kind": self.kind, "keep": self.keep, "n": self.n, "mutation": self.mutation, "representation": self.representation, "rank": self.rank}

    def propose(self, archive_rows: List[dict], rng_seed: int, n: int) -> List[PlayerSpec]:
        from prometheus.toolbox.registry import default_registry
        reg = default_registry(); t = reg.make(self.mutation); s = stream("truncation", rng_seed)
        ranked = [(scalar_objective(r, self.rank), r) for r in archive_rows if r["kind"] == "elite"]
        elites = [r for _, r in sorted(((v, r) for v, r in ranked if v is not None), key=lambda x: (-x[0], x[1].get("player_hash", ""), x[1]["fingerprint"]))][:self.keep]
        if not elites:
            return _gen0(reg, self.representation, rng_seed, n)
        out: List[PlayerSpec] = []
        for i in range(n):
            parent = elites[s.below(len(elites))]["player"]
            tt = t if "player." + parent["representation"] in t.accepts else reg.make("transform.shuffle.v1")   # a representation the mutation cannot touch gets a structure-preserving fallback
            out.append(tt.apply(parent, rng_seed * 977 + i))
        return out

    def ingest(self, receipts: List[dict]) -> List[dict]:
        return _rows_from_receipts(receipts)


class MapElitesSelector(TruncationSelector):
    kind = "selector.map_elites.v1"

    def __init__(self, n: int = 8, mutation: str = "transform.point_mutation.v1", representation: str = "statemachine.v1", rank: Optional[str] = None):
        super().__init__(keep=0, n=n, mutation=mutation, representation=representation, rank=rank)

    def manifest(self) -> dict:
        return {"kind": self.kind, "n": self.n, "mutation": self.mutation, "representation": self.representation, "rank": self.rank}

    def propose(self, archive_rows: List[dict], rng_seed: int, n: int) -> List[PlayerSpec]:
        from prometheus.toolbox.registry import default_registry
        reg = default_registry(); s = stream("map_elites", rng_seed)
        cells = list(elites_by_cell(archive_rows, self.rank).values())
        if not cells:
            return _gen0(reg, self.representation, rng_seed, n)
        out = []
        for i in range(n):
            parent = cells[s.below(len(cells))][0]["player"]
            t = reg.make(self.mutation) if "player." + parent["representation"] in reg.make(self.mutation).accepts else reg.make("transform.shuffle.v1")
            out.append(t.apply(parent, rng_seed * 977 + i))
        return out


def _mean_objective(vals: list):
    """Mean over seeds of scalar values, or per-component mean of vector values; None if any seed had none (or a
    component was None in any seed), or the shapes disagree."""
    if not vals or any(v is None for v in vals):
        return None
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        return sum(vals) / len(vals)
    if all(isinstance(v, dict) for v in vals) and len({tuple(sorted(v)) for v in vals}) == 1:
        return {k: (None if any(v[k] is None for v in vals) else sum(v[k] for v in vals) / len(vals)) for k in vals[0]}
    return None


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
        fp = r["science"]["player_fingerprints"]["0"]
        row = by.setdefault(key, {"kind": "elite", "player": r["_player_manifest"], "fingerprint": fp["hash"],
                                  "player_hash": fp.get("spec_hash") or component_manifest_hash(r["_player_manifest"]),      # C96: identity, not behavioural class
                                  "descriptors": [], "objectives": [], "receipt_ids": [], "seeds": []})
        row["descriptors"].append(list(desc)); row["objectives"].append((r["science"].get("objective") or {}).get("value"))
        row["receipt_ids"].append(r["receipt_id"]); row["seeds"].append(r["seed"])
    rows = []
    for row in by.values():
        vals = row.pop("objectives")
        row["objective"] = _mean_objective(vals)                     # C94: number, {component: mean} or None
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
    if rep.runs_not_started:
        raise GenerationIncomplete("generation %d stopped by the wall budget: %d runs not started" % (gen, rep.runs_not_started), "WALL_BUDGET_EXHAUSTED")
    receipts = read_all(path)
    for r in receipts:
        if r["arm"] == "primary":
            r["_player_manifest"] = r["sweep_point"]["players"][0]
    return receipts


class GenerationIncomplete(RuntimeError):
    def __init__(self, msg, reason):
        super().__init__(msg); self.reason = reason


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
    for r in committed:                                            # C94: a selector that cannot rank the archive refuses before any write
        scalar_objective(r, getattr(sel, "rank", None))
    for gen in range(start, generations):
        players = sel.propose(committed, seed * 7919 + gen, sel.n)
        try:
            receipts = _run_generation(template, players, gen, seed, workdir, registry)
        except GenerationIncomplete as exc:                      # C69: an incomplete generation is never committed
            return {"generations_done": gen, "resumed_from_gen": start, "archive": str(archive), "elites": len(committed), "stopped": exc.reason, "detail": str(exc)}
        new_rows = [dict(r, gen=gen) for r in sel.ingest(receipts)]
        for r in new_rows:                                          # C94: refuse with the keys named BEFORE the generation is written
            scalar_objective(r, getattr(sel, "rank", None))
        for r in new_rows:
            _append(archive, r)
        _append(archive, {"kind": "GEN_DONE", "gen": gen, "n": len(new_rows), "selector": sel.manifest()})
        committed += new_rows
    return {"generations_done": generations, "resumed_from_gen": start, "archive": str(archive), "elites": len(committed), "stopped": None}
