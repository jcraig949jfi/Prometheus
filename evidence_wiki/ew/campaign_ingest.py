"""Campaign ingestion reader (PEW point release, 2026-09-17).

Reads the evidence Archaeon's campaign machine COMMITS -- receipts, attempt
records, preregistrations, REACHABILITY / CORRIDOR / LEDGER rows, per-run
rows and their per-generation series -- at one git commit, and lands each
producer row as ONE content-addressed observation in ew.campaign_observations
under the translation contract (docs/point_release/PEW_CAMPAIGN_INGESTION_
CONTRACT.md). It invents nothing: identities an owner exists for but the
row does not carry are the literal UNKNOWN; identities that do not apply
are NULL; a reconstructed identity says so (origin_kind). Labels the
producer wrote (level, disposition_candidate) are stored AS WRITTEN under
the producer's code identity; PEW derives nothing here.

    python -m ew.campaign_ingest --campaign 3 [--commit <sha>] [--receipt <path>]
    python -m ew.campaign_ingest --campaign 3 --dry-run

Idempotent: observation_id is the content address of (kind, row), so
re-ingesting an unchanged campaign inserts zero rows; a committed line whose
content changed between commits produces a NEW observation and an
ingestion_conflicts row, never an overwrite. Checkpoints per committed path
carry the commit, the blob sha, the line count and the reader version.
Never run from the pinned worktree; never against a store that is not the
named environment (ew.db refuses).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # evidence_wiki/
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from ew import db as ewdb                              # noqa: E402
from ew import workspace                               # noqa: E402

READER_VERSION = "ew.campaign_ingest/1.3"   # 1.1: design factors in run strata; 1.2: foundry_profile_scheme (Proteus #339); 1.3: campaign 4 directory, seed UNKNOWN until Archaeon names it
CONTRACT_VERSION = "PEW_CAMPAIGN_INGESTION_CONTRACT v0.1 (2026-09-17)"
UNKNOWN = "UNKNOWN"
# Proteus #339: "instr1-16:6528b9dc" is ARCHAEON's rendering of a Proteus
# foundry_manifest.v0 regime (minus seed/n) hashed by
# archaeon.wse.reachability.foundry_id; kept VERBATIM as the identity, tagged
# with the scheme so the P1 catalog can join it to the full profile.
FOUNDRY_SCHEME = "archaeon.wse.reachability.foundry_id.v1"

# T1: campaign identity comes from the committed PATH, cross-checked against
# the campaign seed the producer stamped; RECEIPT.campaign is NOT trusted
# (every C3 receipt of record says "cmp2").
# Shared tables (one file, rows from every campaign, each row stamped):
# the reachability table was migrated in place under campaign2/ (C3 readiness
# group A) and the corridor table lives under campaign3/ (73 C2 rows imported).
SHARED_TABLES = (("archaeon/campaign2/REACHABILITY.jsonl", "reachability"),
                 ("archaeon/campaign3/CORRIDOR.jsonl", "corridor"))
CAMPAIGNS = {
    1: {"campaign_id": "cmp1", "seed": 20260917, "dir": "archaeon/campaign1"},
    2: {"campaign_id": "cmp2", "seed": 20260918, "dir": "archaeon/campaign2"},
    3: {"campaign_id": "cmp3", "seed": 20260920, "dir": "archaeon/campaign3"},
    # Campaign 4: the directory is known, the seed is not yet (MNE-53). T1 then
    # identifies a row by the producer's stamp, else the path; when Archaeon
    # names the seed it is added here as reader 1.4 by explicit version
    # transition (the frozen surface pins this map).
    4: {"campaign_id": "cmp4", "seed": None, "dir": "archaeon/campaign4"},
}
SEED_TO_CAMPAIGN = {v["seed"]: v["campaign_id"] for v in CAMPAIGNS.values() if v["seed"] is not None}
DEFINITION_FILES = {
    "reachability": "archaeon/wse/reachability.py",
    "corridor": "archaeon/wse/corridor.py",
    "run": "archaeon/wse/evolve.py",
    "generation": "archaeon/wse/telemetry.py",
}


# ----------------------------------------------------------------- git I/O
def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:300]}")
    return r.stdout


def git_bytes(commit, path):
    r = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=str(REPO), capture_output=True, timeout=600)
    if r.returncode != 0:
        return None
    return r.stdout


def git_blob_sha(commit, path):
    try:
        return git("rev-parse", f"{commit}:{path}").strip()
    except RuntimeError:
        return None


def git_ls(commit, prefix):
    out = git("ls-tree", "-r", "--name-only", commit, prefix)
    return [l for l in out.splitlines() if l.strip()]


# ----------------------------------------------------------- canonical ids
def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def digest(o):
    return hashlib.sha256(canon(o).encode("utf-8")).hexdigest()


def observation_id(kind, row):
    return "CO-" + hashlib.sha256((kind + "\n" + canon(row)).encode("utf-8")).hexdigest()[:32]


def attempt_id_of(harness, n):
    return f"{harness}/a{int(n):02d}"


def campaign_from(seed, path_campaign, notes, stamp=None):
    """T1. The seed decides when it is a known campaign seed; else the
    producer's own stamp (source.campaign: the shared reachability table also
    holds wse-survey-v01 and ssf-c1..c3 rows, which are real producers, not
    cmp1-3); else the path. A disagreement is recorded on the row, never
    resolved by trust in the receipt field."""
    if seed in SEED_TO_CAMPAIGN:
        c = SEED_TO_CAMPAIGN[seed]
        if stamp and stamp != c:
            notes.append(f"campaign_seed {seed} names {c}; producer stamp says {stamp}; seed used")
        elif c != path_campaign and not stamp:
            notes.append(f"campaign_seed {seed} names {c}; path names {path_campaign}; seed used")
        return c
    if stamp:
        return stamp
    return path_campaign


# Producer-defined design factors a run row may carry (Archaeon's names, not
# PEW's): stratification must survive ingestion without parsing experiment
# names (order s7). Copied into strata verbatim when present.
DESIGN_FACTOR_KEYS = ("family", "target", "table", "climber", "encoding", "quality", "dose", "dose_frac", "cap",
                      "n_imported", "site", "cell", "regime", "rung", "delay", "schedule_name", "readout", "world",
                      "budget_evals", "G", "N", "E")

BOOL_COLS = {"stopped_on_solve", "summit_censored", "reached", "censored"}
INT_COLS = {"attempt_number", "resumed_from_attempt", "seed", "generation", "n_pop", "g_budget", "e_episodes",
            "first_foothold_gen", "first_solved_gen", "first_shelf_gen", "summit_candidate_gen", "first_summit_gen",
            "horizon", "source_line"}
FLOAT_COLS = {"best_train_max", "heldout", "source_competence", "direct_reuse_best"}


def _typed(col, v):
    """Producers write 0/1 for booleans and floats for generations here and
    there; the typed column keeps the value, the verbatim row (measured)
    keeps the producer's spelling."""
    if v is None:
        return None
    try:
        if col in BOOL_COLS:
            return bool(v) if not isinstance(v, str) else v.lower() in ("true", "1", "yes")
        if col in INT_COLS:
            return int(v) if not isinstance(v, bool) else int(v)
        if col in FLOAT_COLS:
            return float(v) if not isinstance(v, (list, dict, str)) else None
    except (TypeError, ValueError):
        return None
    return v


# ------------------------------------------------------------- row makers
class Ingest:
    def __init__(self, campaign_n, commit, dry_run=False):
        self.c = CAMPAIGNS[campaign_n]
        self.n = campaign_n
        self.commit = commit
        self.dry = dry_run
        self.run_id = "ING-" + time.strftime("%Y%m%dT%H%M%S") + "-" + commit[:8]
        self.defs = {k: (git_blob_sha(commit, p) or UNKNOWN) for k, p in DEFINITION_FILES.items()}
        self.rows = []            # pending observation dicts
        self.streams = {}         # path -> {blob, lines, seen, new}
        self.notes = []
        self.conn = None if dry_run else ewdb.connect()

    # -- envelope helpers
    def base(self, kind, row, path, line, campaign_id, **env):
        rid = digest(row)
        d = {
            "observation_id": observation_id(kind, row), "kind": kind,
            "campaign_id": campaign_id, "harness_id": env.get("harness_id"),
            "execution_id": env.get("execution_id"), "design_id": env.get("design_id"),
            "design_kind": env.get("design_kind"), "attempt_id": env.get("attempt_id"),
            "attempt_number": env.get("attempt_number"), "resumed_from_attempt": env.get("resumed_from_attempt"),
            "step_id": env.get("step_id"), "foundry_profile": env.get("foundry_profile"),
            "schedule_id": env.get("schedule_id"), "rng_identity": env.get("rng_identity"),
            "world_id": env.get("world_id"), "engine_instance_id": env.get("engine_instance_id"),
            "engine_source_hash": env.get("engine_source_hash"), "arm": env.get("arm"),
            "seed": env.get("seed"), "generation": env.get("generation"),
            "cell": env.get("cell"), "knobs_digest": env.get("knobs_digest"), "regime": env.get("regime"),
            "n_pop": env.get("n_pop"), "g_budget": env.get("g_budget"), "e_episodes": env.get("e_episodes"),
            "strata": env.get("strata"),
            "best_train_max": env.get("best_train_max"), "heldout": env.get("heldout"),
            "first_foothold_gen": env.get("first_foothold_gen"), "first_solved_gen": env.get("first_solved_gen"),
            "first_shelf_gen": env.get("first_shelf_gen"), "summit_candidate_gen": env.get("summit_candidate_gen"),
            "first_summit_gen": env.get("first_summit_gen"), "stopped_on_solve": env.get("stopped_on_solve"),
            "summit_censored": env.get("summit_censored"), "level_as_written": env.get("level_as_written"),
            "reached": env.get("reached"), "source_cell": env.get("source_cell"), "target_cell": env.get("target_cell"),
            "source_competence": env.get("source_competence"), "direct_reuse_best": env.get("direct_reuse_best"),
            "edge_kind": env.get("edge_kind"), "termination_reason": env.get("termination_reason"),
            "horizon": env.get("horizon"), "censored": env.get("censored"), "censoring_reason": env.get("censoring_reason"),
            "measured": row, "definition_version": env.get("definition_version"),
            "producer_row_digest": rid, "origin_kind": env.get("origin_kind", "producer"),
            "source_commit": self.commit, "source_path": path, "source_line": line,
            "source_blob_sha": self.streams[path]["blob"], "reader_version": READER_VERSION,
            "ingest_run_id": self.run_id, "recorded_at": row.get("recorded_at") if isinstance(row, dict) else None,
        }
        self.rows.append(d)
        return d

    def stream(self, path, blob, nlines):
        self.streams[path] = {"blob": blob, "lines": nlines, "seen": 0, "new": 0}

    # -- jsonl tables
    def ingest_jsonl(self, path, kind):
        raw = git_bytes(self.commit, path)
        if raw is None:
            self.notes.append(f"{path}: absent at {self.commit[:9]}")
            return 0
        lines = [l for l in raw.decode("utf-8").splitlines() if l.strip()]
        self.stream(path, git_blob_sha(self.commit, path), len(lines))
        for i, l in enumerate(lines, 1):
            row = json.loads(l)
            notes = []
            src = row.get("source") or {}
            seed_c = row.get("campaign_seed") or (src.get("campaign_seed"))
            path_c = self.c["campaign_id"]
            if kind == "reachability":
                cid = campaign_from(seed_c, path_c, notes, stamp=src.get("campaign"))
            elif kind == "corridor":
                # corridor rows carry no seed; source.campaign is Archaeon's own stamp (cmp2/cmp3 correct there)
                cid = src.get("campaign") or path_c
            else:
                cid = path_c
            harness = src.get("experiment") or row.get("experiment")
            att = src.get("attempt")
            attempt_id = attempt_id_of(harness, att) if (harness and att is not None) else (UNKNOWN if harness else None)
            env = dict(harness_id=harness or UNKNOWN, attempt_id=attempt_id, arm=src.get("arm"))
            if kind == "reachability":
                knobs = row.get("knobs") or {}
                env.update(
                    foundry_profile=row.get("foundry") or UNKNOWN, world_id=row.get("world_id") or UNKNOWN,
                    seed=row.get("seed"),
                    rng_identity=f"{row.get('campaign_seed')}:{row.get('seed')}:{row.get('rng_label')}" if row.get("campaign_seed") is not None else UNKNOWN,
                    cell=row.get("cell"), knobs_digest=("sha256:" + digest(knobs)) if knobs else None,
                    regime=row.get("regime"), n_pop=row.get("N"), g_budget=row.get("G"), e_episodes=row.get("E"),
                    best_train_max=row.get("best_train_max"), heldout=row.get("heldout"),
                    first_foothold_gen=row.get("first_foothold_gen"), first_solved_gen=row.get("first_solved_gen"),
                    first_shelf_gen=row.get("first_shelf_gen"), summit_candidate_gen=row.get("summit_candidate_gen"),
                    first_summit_gen=row.get("first_summit_gen"), stopped_on_solve=row.get("stopped_on_solve"),
                    summit_censored=row.get("summit_censored"), level_as_written=row.get("level"),
                    reached=row.get("reached"), horizon=row.get("G"),
                    censored=bool(row.get("summit_censored")) if row.get("summit_censored") is not None else None,
                    censoring_reason=("horizon G reached before summit" if row.get("summit_censored") else None),
                    strata={"cell": row.get("cell"), "value_bits": row.get("value_bits"), "foundry_profile": row.get("foundry"),
                            "foundry_profile_scheme": FOUNDRY_SCHEME if row.get("foundry") else None,
                            "regime": row.get("regime"), "row_kind": row.get("kind"), "arm": src.get("arm"),
                            "budget_class": f"N{row.get('N')}G{row.get('G')}E{row.get('E')}",
                            "rng_label": row.get("rng_label"), "solve_threshold": row.get("solve_threshold"),
                            "eval_resolution": row.get("eval_resolution")},
                    definition_version=f"archaeon.wse.reachability@{self.defs['reachability']}")
            elif kind == "corridor":
                dr = row.get("direct_reuse") or {}
                init = row.get("init") or {}
                env.update(
                    foundry_profile=row.get("source_foundry") or UNKNOWN, edge_kind=row.get("kind"),
                    source_cell=row.get("source_cell"), target_cell=row.get("target_cell"),
                    source_competence=row.get("source_competence"), direct_reuse_best=dr.get("best"),
                    regime=row.get("regime"), seed=init.get("seed"), n_pop=init.get("N"),
                    level_as_written=init.get("level"), heldout=init.get("heldout"),
                    first_foothold_gen=init.get("first_foothold_gen"), first_shelf_gen=init.get("first_shelf_gen"),
                    first_summit_gen=init.get("first_summit_gen"), summit_candidate_gen=init.get("summit_candidate_gen"),
                    strata={"source_cell": row.get("source_cell"), "target_cell": row.get("target_cell"),
                            "edge_kind": row.get("kind"), "source_foundry": row.get("source_foundry"),
                            "foundry_profile_scheme": FOUNDRY_SCHEME if row.get("source_foundry") else None,
                            "target_foundry": row.get("target_foundry"), "regime": row.get("regime"),
                            "source_budget": row.get("source_budget"), "target_budget": row.get("target_budget"),
                            "source_maturity": row.get("source_maturity")},
                    definition_version=f"archaeon.wse.corridor@{self.defs['corridor']}")
            elif kind == "ledger":
                env.update(strata={"category": row.get("category"), "severity": row.get("severity"), "auto": row.get("auto")},
                           attempt_id=None)
            if notes:
                row = dict(row); row["_ingest_notes"] = notes
            self.base(kind, row, path, i, cid, **env)
        return len(lines)

    # -- per-experiment documents
    def ingest_experiments(self):
        prefix = self.c["dir"] + "/"
        files = git_ls(self.commit, prefix)
        exp_dirs = sorted({f.split("/")[2] for f in files if f.count("/") >= 3 and f.split("/")[2] not in ("attempts",)})
        n = 0
        for exp in exp_dirs:
            base = f"{prefix}{exp}/"
            names = {x[len(base):] for x in files if x.startswith(base)}
            self.of_record = None
            self.of_record_origin = "producer"
            if "ATTEMPTS.json" in names:
                try:
                    aj = json.loads(git_bytes(self.commit, base + "ATTEMPTS.json").decode("utf-8"))
                    self.of_record = int(aj.get("of_record")) if aj.get("of_record") is not None else None
                except Exception:
                    self.of_record = None
            elif self.n == 1:
                # T2: campaign 1 numbered nothing; the file pair is the only evidence
                self.of_record = 2 if "RECEIPT_attempt1.json" in names else 1
                self.of_record_origin = "reconstructed"
            for f in [x for x in files if x.startswith(base)]:
                name = f[len(base):]
                if name == "RECEIPT.json":
                    n += self.ingest_receipt(f, exp, of_record=True)
                elif name == "RECEIPT_attempt1.json":
                    n += self.ingest_receipt(f, exp, of_record=False, reconstructed_attempt=1)
                elif name.startswith("attempts/") and name.endswith("/RECEIPT.json"):
                    n += self.ingest_receipt(f, exp, of_record=False)
                elif name == "PREREG.json" or (name.startswith("attempts/") and name.endswith("/PREREG.json")):
                    n += self.ingest_prereg(f, exp)
                elif name == "ATTEMPTS.json":
                    n += self.ingest_attempts(f, exp)
                elif name == "rows.json" or (name.startswith("attempts/") and name.endswith("/rows.json")) or name == "rows_attempt1.json":
                    n += self.ingest_rows(f, exp, name)
        return n

    def ingest_receipt(self, path, exp, of_record, reconstructed_attempt=None):
        raw = git_bytes(self.commit, path)
        if raw is None:
            return 0
        r = json.loads(raw.decode("utf-8"))
        self.stream(path, git_blob_sha(self.commit, path), 1)
        notes = []
        cid = campaign_from(r.get("campaign_seed"), self.c["campaign_id"], notes)
        if r.get("campaign") and r.get("campaign") != cid:
            notes.append(f"receipt.campaign={r.get('campaign')!r} disagrees; T1 applied")
        harness = r.get("experiment") or exp
        origin = "producer"
        if r.get("attempt_id"):
            attempt_id, attempt_no = r["attempt_id"], r.get("attempt")
        elif reconstructed_attempt is not None:
            attempt_id, attempt_no, origin = attempt_id_of(harness, reconstructed_attempt), reconstructed_attempt, "reconstructed"
        elif of_record and self.of_record is not None:
            attempt_id, attempt_no = attempt_id_of(harness, self.of_record), self.of_record
            origin = self.of_record_origin
        else:
            attempt_id, attempt_no = UNKNOWN, r.get("attempt")
        eng = r.get("engine") or {}
        ev = r.get("engine_version") or {}
        worlds = r.get("worlds") or {}
        world_id = list(worlds.values())[0] if isinstance(worlds, dict) and len(worlds) == 1 else (None if not worlds else UNKNOWN)
        summary = {k: r.get(k) for k in ("attempt", "attempt_id", "campaign", "campaign_seed", "experiment", "prereg_digest",
                                         "grammar_hash", "runtime_hash", "started_at", "finished_at", "purpose",
                                         "hypothesis", "engine_path", "resumed_from", "typed_states",
                                         "disposition_candidate", "ledger_ids", "decisions",
                                         "reachability_rows_appended", "corridor_rows_appended", "summary", "timings",
                                         "teardown", "workspace") if k in r}
        summary["errors_count"] = len(r.get("errors") or [])
        summary["records_count"] = len(r.get("records") or r.get("engine_records") or {})
        summary["steps_count"] = len(r.get("steps") or {})
        summary["replayed_count"] = len(r.get("replayed") or [])
        summary["artifacts_count"] = len(r.get("artifacts") or {})
        summary["worlds"] = worlds
        summary["engine"] = eng
        summary["engine_version"] = ev
        summary["of_record"] = of_record
        summary["_ingest_notes"] = notes
        # design identity: only a sealed prereg digest counts (T3)
        design_id = r.get("prereg_digest") or (UNKNOWN if self.n == 1 else UNKNOWN)
        env = dict(harness_id=harness, attempt_id=attempt_id, attempt_number=attempt_no,
                   resumed_from_attempt=r.get("resumed_from"), design_id=design_id,
                   design_kind="prereg_digest" if r.get("prereg_digest") else None,
                   engine_instance_id=eng.get("engine_instance_id") or ev.get("engine_instance_id") or UNKNOWN,
                   engine_source_hash=eng.get("engine_source_hash") or ev.get("engine_source_hash") or UNKNOWN,
                   foundry_profile=UNKNOWN, world_id=world_id, origin_kind=origin,
                   rng_identity=f"{r.get('campaign_seed')}" if r.get("campaign_seed") else UNKNOWN,
                   strata={"of_record": of_record, "engine_path": r.get("engine_path")})
        self.base("receipt", summary, path, None, cid, **env)
        n = 1
        # engine records: (label -> exp_id, obs_id)
        # campaign 1 wrote engine_records; campaigns 2-3 write records
        for label, ids in (r.get("records") or r.get("engine_records") or {}).items():
            ids = ids if isinstance(ids, dict) else {"id": ids}
            row = {"label": label, "exp_id": ids.get("exp_id"), "obs_id": ids.get("obs_id"), "receipt": path,
                   **({"raw": ids} if "exp_id" not in ids else {})}
            self.base("engine_record", row, path, None, cid, harness_id=harness, attempt_id=attempt_id,
                      world_id=world_id, engine_instance_id=env["engine_instance_id"], origin_kind=origin,
                      arm=label.split("/")[0] if "/" in label else None)
            n += 1
        for name, art in (r.get("artifacts") or {}).items():
            art = art if isinstance(art, dict) else {"artifact_id": art}     # campaign 1: bare id strings
            row = {"name": name, **art, "receipt": path}
            self.base("artifact_ref", row, path, None, cid, harness_id=harness, attempt_id=attempt_id,
                      engine_instance_id=env["engine_instance_id"], origin_kind=origin)
            n += 1
        imports = r.get("imports")
        if imports:
            self.base("import", {"imports": imports, "receipt": path}, path, None, cid, harness_id=harness,
                      attempt_id=attempt_id, origin_kind=origin)
            n += 1
        return n

    def ingest_prereg(self, path, exp):
        raw = git_bytes(self.commit, path)
        if raw is None:
            return 0
        p = json.loads(raw.decode("utf-8"))
        self.stream(path, git_blob_sha(self.commit, path), 1)
        harness = p.get("experiment") or exp
        budget = p.get("budget") or {}
        sched = {k: budget.get(k) for k in ("rungs", "rung_gens", "rung0_max", "p", "G_ladder") if k in budget}
        schedule_id = ("sha256:" + digest(sched)) if sched else None
        self.base("design", p, path, None, self.c["campaign_id"], harness_id=harness,
                  attempt_id=attempt_id_of(harness, p["attempt"]) if p.get("attempt") is not None else UNKNOWN,
                  design_id=p.get("prereg_digest") or UNKNOWN, design_kind="prereg_digest" if p.get("prereg_digest") else None,
                  schedule_id=schedule_id, n_pop=budget.get("N"), g_budget=budget.get("G") or budget.get("G_ladder"),
                  e_episodes=budget.get("E"),
                  strata={"arms": p.get("arms"), "sealed_fields": p.get("sealed_fields"), "claim_ceiling": p.get("claim_ceiling")})
        return 1

    def ingest_attempts(self, path, exp):
        raw = git_bytes(self.commit, path)
        if raw is None:
            return 0
        a = json.loads(raw.decode("utf-8"))
        self.stream(path, git_blob_sha(self.commit, path), len(a.get("attempts") or {}))
        harness = a.get("experiment") or exp
        n = 0
        for k, att in sorted((a.get("attempts") or {}).items(), key=lambda kv: int(kv[0])):
            row = dict(att); row["attempt"] = int(k); row["of_record"] = (int(k) == a.get("of_record"))
            self.base("attempt", row, path, int(k), self.c["campaign_id"], harness_id=harness,
                      attempt_id=attempt_id_of(harness, k), attempt_number=int(k),
                      resumed_from_attempt=att.get("resumed_from"),
                      strata={"engine_path": att.get("engine_path"), "purpose": att.get("purpose"), "of_record": row["of_record"]})
            n += 1
        return n

    SERIES_KEYS = ("schedule", "trace", "matrix", "elite_manifest", "top_k", "history")

    def ingest_rows(self, path, exp, name):
        raw = git_bytes(self.commit, path)
        if raw is None:
            return 0
        try:
            rows = json.loads(raw.decode("utf-8"))
        except Exception as e:
            self.notes.append(f"{path}: not JSON ({e})")
            return 0
        if isinstance(rows, dict):
            rows = rows.get("rows") if isinstance(rows.get("rows"), list) else None
        if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
            self.notes.append(f"{path}: not a list of run rows; skipped")
            return 0
        self.stream(path, git_blob_sha(self.commit, path), len(rows))
        harness = exp
        if name.startswith("attempts/"):
            att_no = int(name.split("/")[1][1:]); origin = "producer"
        elif name == "rows_attempt1.json":
            att_no, origin = 1, "reconstructed"
        else:
            att_no, origin = self.of_record, self.of_record_origin
        attempt_id = attempt_id_of(harness, att_no) if att_no else UNKNOWN
        n = 0
        for i, row in enumerate(rows):
            series = {}
            run = {}
            for k, v in row.items():
                if k in self.SERIES_KEYS or (isinstance(v, list) and len(v) > 50 and all(isinstance(x, (dict, list)) for x in v[:3])):
                    series[k] = {"n": len(v) if hasattr(v, "__len__") else None, "digest": "sha256:" + digest(v)}
                else:
                    run[k] = v
            run["_series"] = series
            run["_index"] = i
            eng = row.get("engine") or {}
            g0 = row.get("gen0_provenance") or {}
            world_id = eng.get("world_id") or row.get("world_id") or None
            env = dict(harness_id=harness, attempt_id=attempt_id, arm=row.get("arm"), seed=row.get("seed"),
                       world_id=world_id, origin_kind=origin,
                       rng_identity=(f"{g0.get('campaign_seed')}:{g0.get('cell_seed')}" if g0 else UNKNOWN),
                       first_solved_gen=row.get("first_solved_gen"), reached=row.get("reached"),
                       heldout=row.get("competence_heldout") if isinstance(row.get("competence_heldout"), (int, float)) else row.get("general_heldout"),
                       strata={"arm": row.get("arm"), "seed": row.get("seed"), "gen0_fill": g0.get("fill"),
                               "n_substituted": g0.get("n_substituted"), "verified_common": g0.get("verified_common"),
                               "imported": row.get("imported"), "persist": row.get("persist"), "p": row.get("p"),
                               # producer-named design factors, carried verbatim when present (order s7):
                               **{k: row.get(k) for k in DESIGN_FACTOR_KEYS if k in row and not isinstance(row.get(k), (dict, list))}},
                       definition_version=f"archaeon.wse.evolve@{self.defs['run']}")
            self.base("run", run, path, i, self.c["campaign_id"], **env)
            n += 1
            # per-generation series: any list of dicts carrying 'gen'
            for k, v in row.items():
                if isinstance(v, list) and v and isinstance(v[0], dict) and "gen" in v[0]:
                    for item in v:
                        g = item.get("gen")
                        grow = dict(item); grow["_series"] = k; grow["_run_index"] = i
                        self.base("generation", grow, path, i, self.c["campaign_id"], harness_id=harness,
                                  attempt_id=attempt_id, arm=row.get("arm"), seed=row.get("seed"), world_id=world_id,
                                  generation=g, origin_kind=origin,
                                  strata={"arm": row.get("arm"), "seed": row.get("seed"), "series": k,
                                          "rung": item.get("rung"), "p": item.get("p")},
                                  definition_version=f"archaeon.wse.telemetry@{self.defs['generation']}")
                        n += 1
        return n

    # ------------------------------------------------------------- writing
    def dedupe(self):
        """Identical copies of a producer row (the of-record rows.json is a
        copy of attempts/aNN/rows.json) are one observation; keep the first."""
        seen, out = set(), []
        for d in self.rows:
            if d["observation_id"] in seen:
                continue
            seen.add(d["observation_id"]); out.append(d)
        dropped = len(self.rows) - len(out)
        self.rows = out
        return dropped

    def write(self):
        if self.dry:
            return {"dry_run": True, "pending": len(self.rows)}
        conn, cur = self.conn, self.conn.cursor()
        cols = ["observation_id", "kind", "campaign_id", "harness_id", "execution_id", "design_id", "design_kind",
                "attempt_id", "attempt_number", "resumed_from_attempt", "step_id", "foundry_profile", "schedule_id",
                "rng_identity", "world_id", "engine_instance_id", "engine_source_hash", "arm", "seed", "generation",
                "cell", "knobs_digest", "regime", "n_pop", "g_budget", "e_episodes", "strata", "best_train_max",
                "heldout", "first_foothold_gen", "first_solved_gen", "first_shelf_gen", "summit_candidate_gen",
                "first_summit_gen", "stopped_on_solve", "summit_censored", "level_as_written", "reached",
                "source_cell", "target_cell", "source_competence", "direct_reuse_best", "edge_kind",
                "termination_reason", "horizon", "censored", "censoring_reason", "measured", "definition_version",
                "producer_row_digest", "origin_kind", "source_commit", "source_path", "source_line", "source_blob_sha",
                "reader_version", "ingest_run_id", "recorded_at"]
        # conflicts: same (path, line) previously ingested with a different digest
        paths = sorted(self.streams)
        cur.execute("SELECT source_path, source_line, producer_row_digest, observation_id, source_commit, kind "
                    "FROM ew.campaign_observations WHERE source_path = ANY(%s)", (paths,))
        prior = {}
        for sp, sl, dg, oid, sc, kd in cur.fetchall():
            prior.setdefault((sp, sl, kd), []).append((dg, oid, sc))
        new = seen = conflicts = refreshed = 0
        by_stream_new = {p: 0 for p in paths}
        for d in self.rows:
            seen += 1
            key = (d["source_path"], d["source_line"], d["kind"])
            if key in prior and d["kind"] in ("reachability", "corridor", "ledger", "receipt", "design"):
                if all(dg != d["producer_row_digest"] for dg, _, _ in prior[key]) and not any(dg == d["producer_row_digest"] for dg, _, _ in prior[key]):
                    dg0, oid0, sc0 = prior[key][0]
                    cur.execute("INSERT INTO ew.ingestion_conflicts(producer, stream, seq, stored_digest, offered_digest, "
                                "stored_observation_id, source_commit, note) VALUES ('archaeon', %s, %s, %s, %s, %s, %s, %s)",
                                (d["source_path"], d["source_line"], dg0, d["producer_row_digest"], oid0, self.commit,
                                 f"committed line content changed between {sc0[:9]} and {self.commit[:9]}; both observations kept"))
                    conflicts += 1
            cur.execute("SELECT nextval('ew.canonical_revision_seq')")
            rev = cur.fetchone()[0]
            vals = [_typed(c, json.dumps(d[c], default=str) if c in ("strata", "measured") and d[c] is not None else d[c]) for c in cols]
            # Envelope columns (everything PEW derived from the row) refresh when
            # the READER version moved; measured/producer_row_digest never change.
            env_cols = [c for c in cols if c not in ("observation_id", "kind", "measured", "producer_row_digest",
                                                     "source_commit", "source_path", "source_line", "source_blob_sha",
                                                     "ingest_run_id", "recorded_at")]
            set_clause = ", ".join(f"{c}=EXCLUDED.{c}" for c in env_cols)      # reader_version is in env_cols
            cur.execute(f"INSERT INTO ew.campaign_observations({','.join(cols)}, revision) VALUES "
                        f"({','.join(['%s'] * len(cols))}, %s) ON CONFLICT (observation_id) DO UPDATE SET {set_clause} "
                        f"WHERE ew.campaign_observations.reader_version <> EXCLUDED.reader_version "
                        f"RETURNING (xmax = 0) AS inserted", vals + [rev])
            got = cur.fetchone()
            if got is not None and got[0]:
                new += 1
                by_stream_new[d["source_path"]] += 1
            elif got is not None:
                refreshed += 1
        for p in paths:
            st = self.streams[p]
            cur.execute("INSERT INTO ew.ingestion_checkpoints(producer, stream, last_seq, last_digest, source_commit, "
                        "reader_version, rows_seen, rows_new, updated_at) VALUES ('archaeon', %s, %s, %s, %s, %s, %s, %s, now()) "
                        "ON CONFLICT (producer, stream) DO UPDATE SET last_seq=EXCLUDED.last_seq, last_digest=EXCLUDED.last_digest, "
                        "source_commit=EXCLUDED.source_commit, reader_version=EXCLUDED.reader_version, "
                        "rows_seen=ew.ingestion_checkpoints.rows_seen+EXCLUDED.rows_seen, "
                        "rows_new=ew.ingestion_checkpoints.rows_new+EXCLUDED.rows_new, updated_at=now()",
                        (p, st["lines"], st["blob"], self.commit, READER_VERSION, st["lines"], by_stream_new[p]))
        payload_sha = hashlib.sha256("\n".join(sorted(d["observation_id"] for d in self.rows)).encode()).hexdigest()
        cur.execute("INSERT INTO ew.write_log(endpoint, machine, agent, payload_sha256, accepted, result_object_id) "
                    "VALUES ('campaign.ingest', %s, %s, %s, true, %s)",
                    (os.environ.get("PROMETHEUS_MACHINE") or "M2", "campaign-ingest", payload_sha, self.run_id))
        conn.commit()
        return {"seen": seen, "new": new, "envelope_refreshed": refreshed, "conflicts": conflicts, "streams": {p: {**self.streams[p], "new": by_stream_new[p]} for p in paths},
                "write_log_payload_sha256": payload_sha}


WORKSPACE = workspace.assert_not_canonical("ingest campaign evidence")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=int, required=True, choices=sorted(CAMPAIGNS))
    ap.add_argument("--commit", default=None, help="git commit to read from (default: origin/main)")
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    commit = git("rev-parse", a.commit or "origin/main").strip()
    t0 = time.time()
    ing = Ingest(a.campaign, commit, dry_run=a.dry_run)
    c = ing.c
    counts = {}
    for path, kind in SHARED_TABLES:
        counts[path] = ing.ingest_jsonl(path, kind)
    counts[f"{c['dir']}/LEDGER.jsonl"] = ing.ingest_jsonl(f"{c['dir']}/LEDGER.jsonl", "ledger")
    counts["experiments"] = ing.ingest_experiments()
    counts["identical_copies_dropped"] = ing.dedupe()
    by_kind = {}
    for d in ing.rows:
        by_kind[d["kind"]] = by_kind.get(d["kind"], 0) + 1
    unknowns = {}
    for d in ing.rows:
        for k in ("harness_id", "attempt_id", "design_id", "engine_instance_id", "foundry_profile", "world_id", "rng_identity"):
            if d.get(k) == UNKNOWN:
                unknowns[k] = unknowns.get(k, 0) + 1
    reconstructed = sum(1 for d in ing.rows if d["origin_kind"] == "reconstructed")
    result = ing.write()
    receipt = {"campaign": c["campaign_id"], "commit": commit, "reader_version": READER_VERSION,
               "contract_version": CONTRACT_VERSION, "ingest_run_id": ing.run_id,
               "definition_identities": ing.defs, "source_counts": counts, "rows_by_kind": by_kind,
               "unknown_identity_counts": unknowns, "reconstructed_rows": reconstructed,
               "result": result, "notes": ing.notes, "workspace": WORKSPACE,
               "seconds": round(time.time() - t0, 1), "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if a.receipt:
        Path(a.receipt).write_text(json.dumps(receipt, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "workspace"}, indent=1, default=str)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
