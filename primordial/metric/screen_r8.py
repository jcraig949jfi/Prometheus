"""R8 item 4 (SWARM_R8 s5, LAUNCH_R8 s6-s8): screen the FROZEN round-8 world set with R16 semantics unchanged.

The R16 screen (r16_cells.cell_job) is keyed by an integer gen_seed that reaches the world only through
e4_run.Spec -> make_world(gen_seed) = expand(de_novo(GRAMMAR_VERSION, gen_seed)). Stratum B worlds ARE de_novo worlds
(gen_seed 900000 + i) and need nothing. Stratum L worlds are mutate() DESCENDANTS of w13 and have no gen_seed, so each
frozen L entry gets a WORLD KEY

    key = L_KEY0 + (index of the entry in the frozen manifest's `entries` list)      L_KEY0 = 8_000_000

(collision-free: consumed gen_seeds are 1..37 and 900000..900063) and, inside the G worker process only, make_world is
resolved through the frozen manifest: key -> genome payload -> wforge expand. The resolver refuses a world whose
world_id or Mechanics.manifest_hash() differs from the manifest. No shared file is edited: the resolver is installed
by this module's job fn in the process that runs it. Every cell row therefore reads `w<key>`; the first row of every
job is an `r8_world_key` row binding key -> world_id, band, ops, op_seeds, mech_hash.

The cell itself is r16_cells.cell_job, unchanged: deterministic parts, uniform random pooled, (train8) learner, floor,
baseline at runs_total 32 / rng_family_count 4 / runs_per_family 8, train128 learner when it can change a verdict,
verdict under gate_in|HOLD. Stage 1 rows do not exist for these worlds, so det_matches_stage1 is None (not a control
here). After the cell, the job builds the cell's own record from its checkpoint and publishes a replication trigger
for a new SURVIVED cell (replication.publish_new_survivors), because cell_job's own check reads only the R16 grid.
"""
from __future__ import annotations

import hashlib
import json
import sys

from primordial.metric import r16_cells as RC
from primordial.metric import screen as SC
from primordial.metric import worlds as WR
from primordial.metric import world_set_r8 as WS

MANIFEST = "primordial/ledger/qd/world_set_r8.json"
MANIFEST_BODY_SHA256 = "f630f9b3022cc136630e5764eb7110cbed9b54f355ed709d379bbe50d4b23767"
L_KEY0 = 8_000_000
EXP = "G-R8-screen"
ROWS = "primordial/ledger/rows/G/G-R8-screen.jsonl"
FN = "primordial.metric.screen_r8:world_cell_job"
PREDICATE_ID = "G-R8-SCREEN"
PRESSURES = ("train8_held64", "train128_held64")

_DOC = None


def manifest(path=MANIFEST) -> dict:
    global _DOC
    if _DOC is None:
        doc = json.loads((WS.ROOT / path).read_text(encoding="ascii"))
        if doc["body_sha256"] != MANIFEST_BODY_SHA256 or WS._sha(doc["body"]) != MANIFEST_BODY_SHA256:
            raise ValueError("MANIFEST_NOT_THE_FROZEN_SET")
        _DOC = doc
    return _DOC


def keys() -> dict:
    """world_id -> {key, entry_index, band, stratum, ...} for every kept entry."""
    out = {}
    for i, e in enumerate(manifest()["body"]["entries"]):
        key = int(e["gen_seed"]) if e["stratum"] == "B" else L_KEY0 + i
        out[e["world_id"]] = {"key": key, "entry_index": i, "world_id": e["world_id"], "stratum": e["stratum"],
                              "band": e["band"], "ops": e["ops"], "op_seeds": e["op_seeds"], "label": e["label"],
                              "silent_steps": e["silent_steps"], "mech_hash": e["mech_hash"],
                              "summary": e["summary"]}
    return out


def _by_key() -> dict:
    return {v["key"]: v for v in keys().values()}


def resolve(key: int):
    """-> (Mechanics, world_id) for an L world key; refuses any disagreement with the frozen manifest."""
    from wforge.world import expand
    k = _by_key().get(int(key))
    if k is None or k["stratum"] != "L":
        raise KeyError(f"{key} is not an R8 stratum-L world key")
    e = manifest()["body"]["entries"][k["entry_index"]]
    g = WS.genome_from_payload(e["genome"])
    mech = expand(g)
    if g.world_id != e["world_id"] or mech.manifest_hash() != e["mech_hash"]:
        raise ValueError(f"GENOME_DOES_NOT_REPRODUCE:{e['world_id']}")
    return mech, g.world_id


def install() -> None:
    """Route make_world(key) through the manifest for L keys in THIS process; every other seed is unchanged."""
    from primordial.soup.b1 import common as CM
    orig = getattr(CM, "_r8_original_make_world", None) or CM.make_world

    def make_world(gen_seed):
        if int(gen_seed) >= L_KEY0:
            return resolve(int(gen_seed))
        return orig(gen_seed)

    make_world._r8_resolver = True
    CM._r8_original_make_world = orig
    for mod in list(sys.modules.values()):
        f = getattr(mod, "make_world", None) if mod is not None else None
        if f is orig or getattr(f, "_r8_resolver", False):
            setattr(mod, "make_world", make_world)


def job_key(world_id: str, pressure: str) -> str:
    return f"g-r8-screen-{world_id}-{pressure}"


def world_cell_job(ctx, world_id, pressure, replication_r=None, **kw):
    install()
    k = keys()[world_id]
    from primordial.qd import e4_run as E4
    spec = E4.Spec(k["key"])
    if spec.wid != world_id:
        raise ValueError(f"WORLD_KEY_MISMATCH: key {k['key']} expands to {spec.wid}, manifest says {world_id}")
    st = ctx.load_checkpoint()
    if st is None:
        ctx.emit({"kind": "r8_world_key", "status": "control", "world": f"w{k['key']}", "gen_seed": k["key"],
                  "pressure": pressure, "manifest": MANIFEST, "manifest_body_sha256": MANIFEST_BODY_SHA256,
                  **{x: k[x] for x in ("world_id", "entry_index", "stratum", "band", "ops", "op_seeds", "label",
                                       "silent_steps", "mech_hash", "summary")},
                  "T": spec.T, "S": spec.S, "W": spec.W})
    RC.cell_job(ctx, k["key"], pressure, stage1_rows=RC.R.STAGE1 if k["key"] < 38 else _NO_STAGE1,
                replication_r=replication_r, **kw)
    st = ctx.load_checkpoint() or {}
    rec = WR.cell(st["floor"], st["base"], st.get("learn128"), est_runs=32)
    verdict = rec["verdicts"][SC.vkey(*SC.ACTIVE)]["verdict"]
    published = []
    if verdict == "SURVIVED":
        from primordial.bus import bus
        from primordial.metric import replication as RP
        r = replication_r or bus.conn()
        doc = WR.build([rec], commit="", max_survivors=None, schema=WR.SCHEMA_V2)
        published = RP.publish_new_survivors(r, doc, source="screen_r8")
    ctx.emit({"kind": "r8_cell", "status": "control", "world": f"w{k['key']}", "gen_seed": k["key"],
              "world_id": world_id, "band": k["band"], "stratum": k["stratum"], "pressure": pressure,
              "verdict": verdict, "verdicts": rec["verdicts"], "floor": rec["floor"], "floor_is_bound": rec["floor_is_bound"],
              "pending": rec.get("pending"), "gate_held64": rec["gate_held64"],
              "baseline_ci95": (rec.get("baseline") or {}).get("ci95"),
              "replication_published": [p.get("stream_id") for p in published]})


_NO_STAGE1 = "primordial/ledger/rows/G/NO_STAGE1_R8.jsonl"      # absent file -> R._rows -> [] -> matches_stage1 None


def envelope(world_id: str, pressure: str, predicate_event_id: str | None = None) -> dict:
    env = {**RC.sample_block(), "campaign_stage": "PRODUCTION", "wall_budget_s": 2400,
           "cpu_budget_s": RC.production_cpu_budget_s(), "gpu_budget_s": 0,
           "expected_output_rows": 5 + 32 * (3 if pressure == "train8_held64" else 2), "checkpointable": True,
           "required_controls": ["floor_suite", "world_key_matches_manifest"],
           "required_oracles": ["world_oracle", "fused_eq_numpy"], "cohort": "G", "predicate_id": PREDICATE_ID,
           "experiment_class": "R16_SCREEN_CELL"}
    if predicate_event_id:
        env["predicate_event_id"] = predicate_event_id
    return env


def plan(order=None, predicate_event_id: str | None = None) -> list[dict]:
    """Jobs for `order` (world_ids, default the frozen screen_order), train8 then train128 per world."""
    order = list(order if order is not None else manifest()["body"]["screen_order"])
    ks = keys()
    return [{"lane": "G", "fn": FN, "exp_id": EXP, "rows": ROWS, "job_key": job_key(w, p),
             "kwargs": {"world_id": w, "pressure": p}, "envelope": envelope(w, p, predicate_event_id),
             "world_key": ks[w]["key"], "band": ks[w]["band"]}
            for w in order for p in PRESSURES]


def manifest_file_sha256() -> str:
    return hashlib.sha256((WS.ROOT / MANIFEST).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
