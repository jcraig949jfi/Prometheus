"""Witness launch driver (C-009-T016). PLUMBING ONLY: it computes and prints no accuracy, retention or reward.

Two subcommands (python -B -m rso.witness.run_witness ...):

  launch CONFIG --ledger STORE --out DIR [--contract C] [--code-commit SHA] [--launch-run-id ID] [--exclude-record F]
      Runs a registered list of (subject genome file, arm, predicate, seeds) as ONE ledgered TOP_LEVEL launch per
      bundle against Ledger.from_contract(STORE, C), through rso/witness/ares_client.py. Each entry is one node
      execution row (RECEIPT, parent_run_id = the launch, receipt_sha256 recorded when its receipt exists, BX2/BX3).
      Bundle DIR: receipts/R###.json (the canonical receipt bytes), subjects/<sha16>.json, seeds.json,
      inventory.json ({"schema", "rows"}, ledger.inventory()), run.json ({"run_id"}), MANIFEST.json LAST (its
      presence means the launch completed; it carries launch_run_id), artifacts/<sha256> (every byte string each
      receipt names in outputs / oracle, verified against the receipt's sha256 and length before it is written,
      stored once per distinct sha256, and listed per node in MANIFEST nodes[].artifacts as {role, sha256, length,
      file}; the evaluator recomputes from these bytes, PREREGISTRATION s7). Producer seam: node_artifacts().
  subject --world W --mode M --P n --G n --eps n --seed n --out DIR [--cfg-json '{...}']
      Runs ares.search.run for a registered subject configuration and writes genome.json (the champion genome as
      canonical bytes), subject_record.json (its sha256, the run receipt, EVERY episode seed the GA drew: the
      per-generation training draws and the held-out sets). Nothing the run measured is written or printed: the
      returned log, held-out and fitness values are discarded. The registered subjects (PREREG_DRAFT s2) are C-010's
      first act after the preregistration freezes; this module's tests never run them.

CONFIG (JSON): {"schema": "rso.witness.launch_config.v0", "label", "world" (default W15), "seed_floor" (optional int),
"exclude_seed_records" (optional paths relative to CONFIG), "entries": [{"subject": path relative to CONFIG,
"arm", "predicate", "seeds": [int, ...]}]}.

Refused before any ledger row is written: an unknown arm, an empty / non-integer / duplicate seed list, a duplicate
node, a seed below seed_floor, a seed in ares EVAL_SEEDS or balanced_seeds_for(world) or in an excluded subject
record, a non-canonical subject genome file, and (T017 / RULER.md s5.2) an S-NOPL entry whose seeds differ from its
S entry's in value or order -- p_chan pairs by position and cannot check seed identity itself. A bundle directory that
already holds anything is never overwritten.

Field decisions (rso-builder-role s2.7):
  - CPU is charged to the node rows (time.process_time around each node); the TOP_LEVEL row carries 0 CPU and 0
    bytes so the ledger's sums do not double count. Revisit if the keeper wants launch overhead metered.
  - A failed node marks its row and the launch FAILED, keeps the partial receipts and inventory, writes no MANIFEST.
    A KeyboardInterrupt leaves the rows INTERRUPTED (unmetered, never zero) by design.
  - The default launch id is "w-<sha12 of the config bytes>-<UTC>-<8 random hex>"; the ledger refuses a repeated id.
Python >= 3.8; numpy.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import uuid

from ares import search as AR
from ares import substrate as S
from rso.binding import binding as B
from rso.slice001 import ledger as L
from rso.slice001 import receipt as R
from rso.witness import ares_client as AC

CONFIG_SCHEMA = "rso.witness.launch_config.v0"
MANIFEST_SCHEMA = "rso.witness.manifest.v0"
INVENTORY_SCHEMA = "rso.witness.inventory.v0"
SEEDS_SCHEMA = "rso.witness.seeds.v0"
SUBJECT_SCHEMA = "rso.witness.subject_record.v0"
SUPPLIED_BY = "rso.witness.run_witness.launch"
PAIRED_ARMS = (("S", "S-NOPL"),)
PAIRED_BASE_PREDICATE = "P-RET"
MAX_SEED = 2 ** 63 - 1


class WitnessError(Exception):
    """Refused or failed. Fails closed; nothing is guessed."""


# --------------------------------------------------------------------------------------------------------
# Bytes

def genome_bytes(genome):
    """The canonical genome file bytes; sha256 of these equals ares_client.genome_digest of the organism."""
    return json.dumps(genome, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise WitnessError("cannot read %s: %s" % (path, e))


def _read_json(path):
    try:
        return json.loads(_read_bytes(path).decode("utf-8"))
    except ValueError as e:
        raise WitnessError("%s is not JSON: %s" % (path, e))


def _write(path, data):
    d = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def _canon(obj):
    return R.canonical_bytes(obj)


def _fresh_dir(out_dir):
    if os.path.exists(out_dir) and (not os.path.isdir(out_dir) or os.listdir(out_dir)):
        raise WitnessError("output %s exists and is not an empty directory; never overwritten" % out_dir)


# --------------------------------------------------------------------------------------------------------
# Subject run: the champion genome and every episode seed the GA drew

class _SeedRecorder(object):
    """Wraps ares.search.rollout for the duration of one run, recording the seed lists it is called with and
    passing everything through untouched. record=True calls are the per-generation training draws; the others are
    held-out evaluations. Fitness is never read."""

    def __init__(self):
        self.training, self.heldout = [], []

    def __enter__(self):
        self._orig = AR.rollout
        orig, rec = self._orig, self

        def rollout(pop, world, seeds, record=False):
            seeds = [int(x) for x in seeds]
            (rec.training if record else rec.heldout).append(seeds)
            return orig(pop, world, seeds, record=record)
        AR.rollout = rollout
        return self

    def __exit__(self, exc_type, exc, tb):
        AR.rollout = self._orig
        return False


def run_subject(world, mode, cfg_kwargs, P, G, eps, seed, out_dir):
    """ares.search.run for one registered subject configuration; writes genome.json and subject_record.json."""
    _fresh_dir(out_dir)
    cfg = S.Config(**(cfg_kwargs or {}))
    with _SeedRecorder() as rec:
        res = AR.run(world, mode, cfg, P=P, G=G, eps=eps, seed=seed)
    data = genome_bytes(res["final"]["genome"])
    heldout = []
    for s in rec.heldout:
        if s not in heldout:
            heldout.append(s)
    every = sorted(set(x for s in rec.training for x in s) | set(x for s in heldout for x in s))
    record = {"schema": SUBJECT_SCHEMA, "world": world, "mode": mode, "cfg": cfg.to_dict(),
              "P": int(P), "G": int(G), "eps": int(eps), "seed": int(seed),
              "genome_file": "genome.json", "genome_sha256": sha256_hex(data), "genome_length": len(data),
              "run_receipt": res["receipt"],
              "training_seeds_by_generation": rec.training, "heldout_seed_sets": heldout,
              "episode_seeds": every}
    _write(os.path.join(out_dir, "genome.json"), data)
    _write(os.path.join(out_dir, "subject_record.json"),
           json.dumps(record, sort_keys=True, indent=1).encode("utf-8") + b"\n")
    return record


# --------------------------------------------------------------------------------------------------------
# Config validation (everything here runs before the ledger is touched)

def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _excluded_seeds(world_name, records):
    ex = {}
    for s in AR.EVAL_SEEDS:
        ex[int(s)] = "ares EVAL_SEEDS"
    for s in AR.balanced_seeds_for(AC.world(world_name, "present")):
        ex[int(s)] = "ares balanced_seeds_for(%s)" % world_name
    for path in records:
        rec = _read_json(path)
        if not isinstance(rec, dict) or not isinstance(rec.get("episode_seeds"), list):
            raise WitnessError("%s has no episode_seeds list" % path)
        for s in rec["episode_seeds"]:
            ex.setdefault(int(s), "excluded subject record %s" % os.path.basename(path))
    return ex


def load_config(config_path, exclude_records=()):
    """Validate CONFIG and read its subject files. Returns a plan dict; raises WitnessError on any refusal."""
    cfg = _read_json(config_path)
    base = os.path.dirname(os.path.abspath(config_path))
    if not isinstance(cfg, dict) or cfg.get("schema") != CONFIG_SCHEMA:
        raise WitnessError("config schema must be %s" % CONFIG_SCHEMA)
    label, world_name = cfg.get("label"), cfg.get("world", AC.WORLD)
    if not isinstance(label, str) or not label:
        raise WitnessError("config needs a non-empty label")
    floor = cfg.get("seed_floor")
    if floor is not None and not _is_int(floor):
        raise WitnessError("seed_floor must be an integer when given")
    entries = cfg.get("entries")
    if not isinstance(entries, list) or not entries:
        raise WitnessError("config needs a non-empty entries list")
    records = [os.path.join(base, p) for p in cfg.get("exclude_seed_records", [])] + list(exclude_records)
    try:
        excluded = _excluded_seeds(world_name, records)
    except KeyError:
        raise WitnessError("unknown world %r" % world_name)
    subjects, plan, seen, by_subject_arm = {}, [], set(), {}
    for i, e in enumerate(entries):
        where = "entries[%d]" % i
        if not isinstance(e, dict) or not all(k in e for k in ("subject", "arm", "predicate", "seeds")):
            raise WitnessError("%s needs subject, arm, predicate, seeds" % where)
        if e["arm"] not in AC.ARMS:
            raise WitnessError("%s: unknown arm %r; registered: %s" % (where, e["arm"], ", ".join(AC.ARMS)))
        if not isinstance(e["predicate"], str) or not e["predicate"]:
            raise WitnessError("%s: predicate must be a non-empty string" % where)
        seeds = e["seeds"]
        if not isinstance(seeds, list) or not seeds:
            raise WitnessError("%s: seeds must be a non-empty list" % where)
        if not all(_is_int(s) and 0 <= s <= MAX_SEED for s in seeds):
            raise WitnessError("%s: every seed must be a non-negative integer" % where)
        if len(set(seeds)) != len(seeds):
            raise WitnessError("%s: duplicate seed in the list" % where)
        for s in seeds:
            if floor is not None and s < floor:
                raise WitnessError("%s: seed %d is below the seed floor %d" % (where, s, floor))
            if s in excluded:
                raise WitnessError("%s: seed %d is excluded (%s)" % (where, s, excluded[s]))
        spath = os.path.join(base, e["subject"])
        if spath not in subjects:
            data = _read_bytes(spath)
            try:
                pop = S.Population.from_genomes([json.loads(data.decode("utf-8"))])
            except (ValueError, KeyError, TypeError) as ex:
                raise WitnessError("%s: %s is not a genome file: %s" % (where, e["subject"], ex))
            if AC.genome_digest(pop) != sha256_hex(data):
                raise WitnessError("%s: %s is not canonical genome bytes (genome_bytes form); re-write it with "
                                   "the subject subcommand" % (where, e["subject"]))
            subjects[spath] = {"data": data, "pop": pop, "sha256": sha256_hex(data)}
        sub = subjects[spath]
        nid = AC.node_id(sub["sha256"], e["arm"], e["predicate"], world_name)
        if nid in seen:
            raise WitnessError("%s: duplicate node %s" % (where, nid))
        seen.add(nid)
        by_subject_arm[(sub["sha256"], e["arm"], e["predicate"])] = seeds
        plan.append({"subject": sub, "arm": e["arm"], "predicate": e["predicate"], "seeds": list(seeds),
                     "node_id": nid})
    # RULER.md s5.2: S-NOPL is paired with S's P-RET node -- keyed by predicate, not by arm alone, because S also runs
    # P-OBS, P-ERASE and P-PRES on other seed lists (C-010-T013 integration fix); without a P-RET entry, with the S
    # entry of the same predicate.
    for (sha, a, pred), seeds in list(by_subject_arm.items()):
        for base_arm, paired in PAIRED_ARMS:
            if a != paired:
                continue
            base = by_subject_arm.get((sha, base_arm, PAIRED_BASE_PREDICATE), by_subject_arm.get((sha, base_arm, pred)))
            if base is not None and base != seeds:
                raise WitnessError("%s must run on %s's episode seeds in the same order (RULER.md s5.2): the "
                                   "paired test cannot check seed identity itself" % (paired, base_arm))
    return {"label": label, "world": world_name, "plan": plan, "subjects": list(subjects.values()),
            "config_bytes": _read_bytes(config_path)}


# --------------------------------------------------------------------------------------------------------
# Artifacts (PREREGISTRATION s7): every byte string the evaluator reads is stored as artifacts/<sha256>

def node_artifacts(receipt_fn, handle, arm_name, predicate, subject, seeds):
    """The seam to the producer. Returns (receipt dict, {sha256: bytes}).

    Preferred form (C-010-T010): receipt_fn returns that tuple itself. Until it does, receipt_fn returns the
    receipt dict alone and the bytes are re-derived here by re-running the same deterministic node through
    ares_client (arm, run_episodes) in the shape receipt_dict emits (trace:actions, oracle:regimes,
    oracle:reset_steps); verify_artifacts then checks them against the receipt either way, so a re-derivation
    that disagrees with the receipt is refused, never trusted."""
    got = receipt_fn(handle, arm_name, predicate, subject, seeds)
    if isinstance(got, tuple):
        rec, arts = got
        return rec, dict(arts)
    pop, mode, rt_cls = AC.arm(arm_name, subject)
    out = AC.run_episodes(pop, AC.world(handle.world_name, mode), seeds, runtime_cls=rt_cls)
    arts = {}
    for data in (out["actions"].tobytes(), out["regimes"].tobytes(), json.dumps(out["reset_steps"]).encode("ascii")):
        arts[sha256_hex(data)] = data
    return got, arts


def verify_artifacts(rec, arts):
    """Check the bytes against the receipt's own listing: all named bytes present, sha256 and length agree, and
    nothing unnamed. Returns the manifest entries in receipt order (outputs, then oracle)."""
    entries = []
    for key in ("outputs", "oracle"):
        for a in rec.get(key) or []:
            entries.append(a)
    named = set()
    listed = []
    for a in entries:
        sha, role, length = a.get("sha256"), a.get("role"), a.get("length")
        if sha not in arts:
            raise WitnessError("artifact %s (%s) is missing: no bytes supplied for its sha256" % (role, sha))
        data = arts[sha]
        if sha256_hex(data) != sha:
            raise WitnessError("artifact %s: bytes do not hash to the receipt's sha256 %s" % (role, sha))
        if len(data) != length:
            raise WitnessError("artifact %s (%s): length %d != receipt length %r" % (role, sha, len(data), length))
        named.add(sha)
        listed.append({"role": role, "sha256": sha, "length": length, "file": "artifacts/" + sha})
    extra = sorted(set(arts) - named)
    if extra:
        raise WitnessError("bytes supplied that the receipt does not name (not named): %s" % ", ".join(extra))
    return listed


def _store_artifacts(out_dir, listed, arts):
    for a in listed:
        path = os.path.join(out_dir, a["file"])
        if os.path.exists(path):
            if _read_bytes(path) != arts[a["sha256"]]:
                raise WitnessError("%s already holds different bytes; never overwritten" % a["file"])
            continue
        _write(path, arts[a["sha256"]])


# --------------------------------------------------------------------------------------------------------
# Launch

def _default_launch_id(config_bytes):
    return "w-%s-%s-%s" % (sha256_hex(config_bytes)[:12], time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
                           uuid.uuid4().hex[:8])


def _default_commit():
    c = AR.code_commit()
    if c == "UNKNOWN":
        raise WitnessError("cannot determine the code commit; pass --code-commit")
    return c


def launch(config_path, ledger, out_dir, code_commit=None, launch_run_id=None, exclude_records=(),
           supplied_by=SUPPLIED_BY):
    """One ledgered TOP_LEVEL launch -> one bundle. Returns the summary dict (ids and counts only)."""
    loaded = load_config(config_path, exclude_records)
    _fresh_dir(out_dir)
    code_commit = code_commit or _default_commit()
    launch_run_id = launch_run_id or _default_launch_id(loaded["config_bytes"])
    handle = AC.Launch(launch_run_id, code_commit, loaded["world"])      # identity holder; rows live in the ledger
    top = ledger.begin(launch_run_id, "WITNESS:" + loaded["label"], L.TOP_LEVEL, supplied_by=supplied_by)
    nodes, per_subject = [], {}
    try:
        for n, item in enumerate(loaded["plan"]):
            run_id = "%s/%s" % (launch_run_id, item["node_id"])
            att = ledger.begin(run_id, item["node_id"], L.RECEIPT, supplied_by=supplied_by,
                               parent_run_id=launch_run_id)
            c0 = time.process_time()
            try:
                rec, arts = node_artifacts(AC.receipt_dict, handle, item["arm"], item["predicate"],
                                           item["subject"]["pop"], item["seeds"])
                listed = verify_artifacts(rec, arts)
                data = AC.receipt_bytes(rec)
                _store_artifacts(out_dir, listed, arts)
            except Exception:
                att.finish("FAILED", cpu_s=time.process_time() - c0)
                raise
            fname = "receipts/R%03d.json" % n
            _write(os.path.join(out_dir, fname), data)
            att.finish("COMPLETED", cpu_s=time.process_time() - c0, artifact_bytes=len(data),
                       receipt_sha256=B.receipt_sha256(data))
            nodes.append({"node_id": item["node_id"], "run_id": run_id, "arm": item["arm"],
                          "predicate": item["predicate"], "subject_sha256": item["subject"]["sha256"],
                          "receipt_file": fname,
                          "artifact": {"role": "receipt", "sha256": B.receipt_sha256(data), "length": len(data)},
                          "artifacts": listed})
            s = per_subject.setdefault(item["subject"]["sha256"], {"arms": {}, "union": set()})
            s["arms"][item["arm"]] = list(item["seeds"])
            s["union"].update(item["seeds"])
    except Exception as e:
        top.finish("FAILED")
        _write(os.path.join(out_dir, "inventory.json"), _canon({"schema": INVENTORY_SCHEMA, "rows": ledger.inventory()}))
        if isinstance(e, L.CapExhausted):
            raise
        raise WitnessError("launch %s FAILED at node %d (%s): %s: %s; no MANIFEST written" % (
            launch_run_id, len(nodes), loaded["plan"][len(nodes)]["node_id"], type(e).__name__, e))
    top.finish("COMPLETED")
    subjects = []
    for sub in loaded["subjects"]:
        fname = "subjects/%s.json" % sub["sha256"][:16]
        _write(os.path.join(out_dir, fname), sub["data"])
        subjects.append({"sha256": sub["sha256"], "file": fname, "length": len(sub["data"])})
    _write(os.path.join(out_dir, "seeds.json"), _canon({
        "schema": SEEDS_SCHEMA, "launch_run_id": launch_run_id,
        "subjects": {k: {"arms": v["arms"], "union": sorted(v["union"])} for k, v in per_subject.items()}}))
    _write(os.path.join(out_dir, "inventory.json"), _canon({"schema": INVENTORY_SCHEMA, "rows": ledger.inventory()}))
    _write(os.path.join(out_dir, "run.json"), _canon({"run_id": launch_run_id}))
    _write(os.path.join(out_dir, "MANIFEST.json"), _canon({
        "schema": MANIFEST_SCHEMA, "launch_run_id": launch_run_id, "label": loaded["label"],
        "world": loaded["world"], "code_commit": code_commit, "nodes": nodes, "subjects": subjects}))
    return {"launch_run_id": launch_run_id, "nodes": len(nodes), "bundle": out_dir, "status": "COMPLETED"}


# --------------------------------------------------------------------------------------------------------
# CLI

def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.witness.run_witness")
    sub = ap.add_subparsers(dest="cmd")
    sub.required = True
    a = sub.add_parser("launch")
    a.add_argument("config")
    a.add_argument("--ledger", required=True)
    a.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    a.add_argument("--out", required=True)
    a.add_argument("--code-commit")
    a.add_argument("--launch-run-id")
    a.add_argument("--exclude-record", action="append", default=[])
    b = sub.add_parser("subject")
    b.add_argument("--world", required=True)
    b.add_argument("--mode", default="present")
    b.add_argument("--P", type=int, required=True)
    b.add_argument("--G", type=int, required=True)
    b.add_argument("--eps", type=int, required=True)
    b.add_argument("--seed", type=int, required=True)
    b.add_argument("--cfg-json", default="{}")
    b.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "launch":
            led = L.Ledger.from_contract(args.ledger, args.contract)
            out = launch(args.config, led, args.out, code_commit=args.code_commit,
                         launch_run_id=args.launch_run_id, exclude_records=args.exclude_record)
        else:
            try:
                cfg_kwargs = json.loads(args.cfg_json)
            except ValueError as e:
                raise WitnessError("--cfg-json is not JSON: %s" % e)
            rec = run_subject(args.world, args.mode, cfg_kwargs, args.P, args.G, args.eps, args.seed, args.out)
            out = {"out": args.out, "genome_sha256": rec["genome_sha256"],
                   "episode_seed_count": len(rec["episode_seeds"])}
    except L.CapExhausted as e:
        sys.stderr.write("cap exhausted: %s\n" % e)
        return 3
    except (WitnessError, L.LedgerError) as e:
        sys.stderr.write("witness error: %s\n" % e)
        return 2
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
