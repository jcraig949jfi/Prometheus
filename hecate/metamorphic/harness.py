"""Metamorphic test harness for Hecate world evaluators.

A good evaluator must react correctly when its input rows are corrupted in
known ways. This harness copies each world to a scratch directory, applies a
mutation operator to the evaluator's rows file, runs the evaluator there (never
in place), reads the verdict it writes, and judges the reaction against an
expectation fixed per mutation (see README.md).

Usage:
    python hecate/metamorphic/harness.py --scratch DIR [--only SUBSTR]
        [--workers 6] [--timeout 60] [--json OUT.json] [--md OUT.md]

Nothing under hecate/programs is written. No git, no network.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROGRAMS = os.path.join(REPO, "hecate", "programs")

SEED_KEYS = ("seed", "seed_index")
# Design (stratum) keys: identify which cell of the design a row belongs to.
DESIGN_KEYS = ("attack", "variant", "attempt", "phase", "tag", "run", "k", "level", "d",
               "delta", "tau", "exhaustion", "mismatched", "s", "config", "exhaustive",
               "role", "mode", "decoder")
# Coarse keys used for within-seed grouping (M7) and for fallback matching.
GROUP_KEYS = ("attack", "variant", "attempt", "phase", "tag", "run")
# Label keys: identity/provenance of a row, never copied between arms.
LABEL_KEYS = SEED_KEYS + DESIGN_KEYS + ("source", "triplicateId", "world")
META_ARMS = {"_META", "META", "RUNINFO", "CPU", "CALIBRATION"}

POS = {"SIGNAL", "SURVIVES", "ORIG_FOSSIL_ALT_PASS", "PILOT_PASS"}
NEG = {"NULL"}
CONF = {"CONFOUNDED"}
INSTR = {"INSTRUMENT_FAIL", "NOT_BUILT", "SPEC_UNATTAINABLE"}

# Pilot-only worlds (no evaluate.py): argv, rows file read, output file.
PILOTS = {
    "HT-37e311ce05/worlds/W4": (["2"], "pilot_rows.jsonl", "PILOT.json"),
    "HT-55162c0ac0/worlds/W2": (["2"], "pilot_rows.jsonl", "PILOT.json"),
    "HT-8a87057933/worlds/W4": (["2"], "pilot_rows.jsonl", "PILOT.json"),
    "HT-974471f045/worlds/W1": (["2"], "pilot_rows_attempt2.jsonl", "PILOT.json"),
    "HT-ae38c641b1/worlds/W4": (["2"], "pilot_rows.jsonl", "PILOT.json"),
    "HT-faa9277e02/worlds/W1": (["1"], "pilot_rows.jsonl", "PILOT.json"),
}
# Arm aliases where the world names its roles differently.
ALIASES = {
    "HT-ae38c641b1/worlds/W5/probe": {"TREATMENT": "V", "NULL_TWIN": "NULL_TWIN_V"},
    "HT-faa9277e02/worlds/W6/probe": {"CONTROL": "FIXED"},
    "HT-8a87057933/worlds/W5/probe": {"CONTROL": "CONTROL_REF"},
    "HT-8a87057933/worlds/W5/pass4": {"CONTROL": "CONTROL_REF"},
}

MUTATIONS = {
    "M1": "swap TREATMENT <-> NULL_TWIN data (simultaneous copy both ways)",
    "M2": "NULL_TWIN := copy of TREATMENT (pilot: NULL_TWIN := copy of POSITIVE_CONTROL)",
    "M3a": "TREATMENT := copy of CONTROL",
    "M3b": "TREATMENT := copy of NULL_TWIN",
    "M4": "drop every *POSITIVE_CONTROL* row",
    "M4c": "drop every *CHEAT* row (extension: same vacuous-gate question for the cheat control)",
    "M5": "CHEAT := copy of TREATMENT (pilot: CHEAT := copy of NULL_TWIN)",
    "M6": "every seed's rows := seed s0's rows (seed label kept)",
    "M7": "measurement payload permuted across arms within each (seed, stratum) group",
}


# --------------------------------------------------------------------------- targets
@dataclass
class Target:
    tid: str            # e.g. HT-321a8fd8e0/worlds/W1/pass4
    kind: str           # main | probe | pass4 | pilot
    copy_root: str      # directory copied to scratch (world dir)
    eval_rel: str       # evaluator dir relative to copy_root ('' or 'probe' / 'pass4')
    script: str
    argv: list
    rows_file: str
    out_file: str
    roles: dict = field(default_factory=dict)


def discover(programs=PROGRAMS):
    out = []
    for prog in sorted(os.listdir(programs)):
        wroot = os.path.join(programs, prog, "worlds")
        if not prog.startswith("HT-") or not os.path.isdir(wroot):
            continue
        for w in sorted(os.listdir(wroot)):
            wd = os.path.join(wroot, w)
            if not os.path.isdir(wd):
                continue
            rel = f"{prog}/worlds/{w}"
            if os.path.exists(os.path.join(wd, "evaluate.py")) and os.path.exists(os.path.join(wd, "rows.jsonl")):
                out.append(Target(rel, "main", wd, "", "evaluate.py", [], "rows.jsonl", "OUTCOME.json"))
            elif rel in PILOTS:
                argv, rf, of = PILOTS[rel]
                out.append(Target(rel, "pilot", wd, "", "pilot_eval.py", argv, rf, of))
            for sub, of in (("probe", "OUTCOME.json"), ("pass4", "PASS4_OUTCOME.json")):
                sd = os.path.join(wd, sub)
                if os.path.exists(os.path.join(sd, "evaluate.py")) and os.path.exists(os.path.join(sd, "rows.jsonl")):
                    out.append(Target(f"{rel}/{sub}", sub, wd, sub, "evaluate.py", [], "rows.jsonl", of))
    return out


def resolve_roles(t, rows):
    arms = {r.get("arm") for r in rows}
    al = ALIASES.get(t.tid, {})
    roles = {}
    for role in ("TREATMENT", "NULL_TWIN", "CONTROL", "POSITIVE_CONTROL", "CHEAT"):
        name = al.get(role, role)
        roles[role] = name if name in arms else None
    return roles


# --------------------------------------------------------------------------- row utilities
def load_rows(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def dump_rows(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def seed_key(r):
    for k in SEED_KEYS:
        if k in r:
            return k
    return None


def _v(r, k):
    v = r.get(k)
    return json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v


def _key(r, keys):
    sk = seed_key(r)
    return (r.get(sk) if sk else None,) + tuple(_v(r, k) for k in keys)


def is_meta(r):
    return r.get("arm") is None or r.get("arm") in META_ARMS


def copy_arm(rows, src, dst, pool=None, lenient=False, info=None):
    """Make arm dst a copy of arm src, keeping dst's row count, seeds and design cells.

    Each dst row is replaced by the best-matching src row (same seed + design
    cell; falling back to coarser keys, then by index). Label keys (seed,
    design cell, provenance such as 'source'/'role') are restored from the dst
    row; dst-only payload keys are DROPPED, so dst really is a copy of src (an
    evaluator that needs a dst-only field crashes, reported as CRASH-SCHEMA).
    `pool` (default: rows) is where src rows are looked up, so that two copies
    can be chained into a simultaneous swap. lenient=True keeps dst-only
    payload keys (stale dst data) -- used only as a fallback after a
    CRASH-SCHEMA, and the kept keys are recorded in `info`.
    """
    S = [r for r in (pool if pool is not None else rows) if r.get("arm") == src]
    if not S or not any(r.get("arm") == dst for r in rows):
        return None
    ladders = [DESIGN_KEYS, ("attack", "variant", "attempt", "k", "level", "d", "delta", "tau"),
               GROUP_KEYS, ("attack",), ()]
    idx = [{} for _ in ladders]
    for r in S:
        for i, ks in enumerate(ladders):
            idx[i].setdefault(_key(r, ks), []).append(r)
    out, n = [], 0
    for r in rows:
        if r.get("arm") != dst:
            out.append(r)
            continue
        src_row = None
        for i, ks in enumerate(ladders):
            hit = idx[i].get(_key(r, ks))
            if hit:
                src_row = hit[n % len(hit)] if i == len(ladders) - 1 else hit[0]
                break
        if src_row is None:
            src_row = S[n % len(S)]
        n += 1
        new = dict(r) if lenient else {}
        new.update(copy.deepcopy(src_row))
        if info is not None:
            only = set(r) - set(src_row) - set(LABEL_KEYS) - {"arm"}
            info.setdefault("dst_only_keys", set()).update(only)
        for k in LABEL_KEYS:
            if k in r:
                new[k] = r[k]
        new["arm"] = dst
        out.append(new)
    return out


def swap_arms(rows, a, b, lenient=False, info=None):
    """Simultaneous swap of the data of arms a and b (labels/design cells stay put)."""
    step = copy_arm(rows, b, a, lenient=lenient, info=info)
    return copy_arm(step, a, b, pool=rows, lenient=lenient, info=info) if step is not None else None


def drop_arm(rows, tag):
    out = [r for r in rows if tag not in str(r.get("arm"))]
    return out if len(out) < len(rows) else None


def dup_seed(rows):
    seeds = sorted({r.get(seed_key(r)) for r in rows if seed_key(r) and not is_meta(r)
                    and isinstance(r.get(seed_key(r)), (int, float))})
    if len(seeds) < 2:
        return None
    s0 = seeds[0]
    ref = {}
    for r in rows:
        sk = seed_key(r)
        if sk and r.get(sk) == s0 and not is_meta(r):
            ref.setdefault((r.get("arm"),) + _key(r, DESIGN_KEYS)[1:], r)
            ref.setdefault(("coarse", r.get("arm")) + _key(r, GROUP_KEYS)[1:], r)
    out, changed = [], 0
    for r in rows:
        sk = seed_key(r)
        if is_meta(r) or not sk or r.get(sk) == s0:
            out.append(r)
            continue
        r0 = ref.get((r.get("arm"),) + _key(r, DESIGN_KEYS)[1:]) or \
            ref.get(("coarse", r.get("arm")) + _key(r, GROUP_KEYS)[1:])
        if r0 is None:
            out.append(r)
            continue
        new = dict(r)
        new.update(copy.deepcopy(r0))
        new[sk] = r[sk]
        out.append(new)
        changed += 1
    return out if changed else None


def shuffle_within_seed(rows, rng, info=None):
    """Within each (seed, coarse stratum) group, move measurement values across
    arms. For every payload key, the rows of the group that carry it are
    permuted (one permutation per distinct carrier set, so a row's measurement
    vector moves together), preferring permutations in which every row gets
    another arm's value. Keys carried by one arm only cannot move; they are
    recorded in info['unmoved_keys']."""
    groups = {}
    for i, r in enumerate(rows):
        if is_meta(r):
            continue
        groups.setdefault(_key(r, GROUP_KEYS), []).append(i)
    out = [dict(r) for r in rows]
    moved_keys, unmoved, moved_arms = set(), set(), set()
    for g, ids in groups.items():
        carriers = {}
        for i in ids:
            for k in rows[i]:
                if k not in LABEL_KEYS and k != "arm":
                    carriers.setdefault(k, []).append(i)
        perms = {}
        for k, cs in carriers.items():
            arms = [rows[i]["arm"] for i in cs]
            if len(set(arms)) < 2:
                unmoved.add(k)
                continue
            key = tuple(cs)
            if key not in perms:
                best, best_bad = None, None
                for _ in range(100):
                    perm = list(range(len(cs)))
                    rng.shuffle(perm)
                    bad = sum(arms[p] == arms[j] for j, p in enumerate(perm))
                    if best is None or bad < best_bad:
                        best, best_bad = perm, bad
                    if bad == 0:
                        break
                perms[key] = best
            for j, p in enumerate(perms[key]):
                if p != j:
                    out[cs[j]][k] = copy.deepcopy(rows[cs[p]][k])
                    moved_keys.add(k)
                    moved_arms.add(rows[cs[j]]["arm"])
    if info is not None:
        info["moved_keys"] = moved_keys
        info["unmoved_keys"] = unmoved - moved_keys
        info["moved_arms"] = moved_arms
    return out if moved_keys else None


def mutate(name, rows, roles, kind, rng, lenient=False, info=None):
    """Return mutated rows, or None when the mutation does not apply."""
    T, NT, C, PC, CH = (roles[k] for k in ("TREATMENT", "NULL_TWIN", "CONTROL", "POSITIVE_CONTROL", "CHEAT"))
    kw = dict(lenient=lenient, info=info)
    if name == "M1":
        return swap_arms(rows, T, NT, **kw) if T and NT else None
    if name == "M2":
        if T and NT:
            return copy_arm(rows, T, NT, **kw)
        return copy_arm(rows, PC, NT, **kw) if kind == "pilot" and PC and NT else None
    if name == "M3a":
        return copy_arm(rows, C, T, **kw) if T and C else None
    if name == "M3b":
        return copy_arm(rows, NT, T, **kw) if T and NT else None
    if name == "M4":
        return drop_arm(rows, "POSITIVE_CONTROL")
    if name == "M4c":
        return drop_arm(rows, "CHEAT")
    if name == "M5":
        if T and CH:
            return copy_arm(rows, T, CH, **kw)
        return copy_arm(rows, NT, CH, **kw) if kind == "pilot" and NT and CH else None
    if name == "M6":
        return dup_seed(rows)
    if name == "M7":
        return shuffle_within_seed(rows, rng, info)
    raise KeyError(name)


COPY_MUTS = ("M1", "M2", "M3a", "M3b", "M5")


# --------------------------------------------------------------------------- running
def _ignore(_d, names):
    return [n for n in names if n == "__pycache__"]


def run_one(t, mut, rows, scratch, timeout):
    """Run evaluator t on a scratch copy with the given rows (None = unmutated)."""
    slug = t.tid.replace("/", "__")
    dst = os.path.join(scratch, slug, mut)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(t.copy_root, dst, ignore=_ignore)
    edir = os.path.join(dst, t.eval_rel) if t.eval_rel else dst
    if rows is not None:
        dump_rows(os.path.join(edir, t.rows_file), rows)
    outp = os.path.join(edir, t.out_file)
    if os.path.exists(outp):
        os.remove(outp)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
               MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, t.script] + t.argv, cwd=edir, env=env,
                           capture_output=True, text=True, timeout=timeout, encoding="utf-8",
                           errors="replace")
        rc, err = p.returncode, p.stderr
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "wall_s": round(time.time() - t0, 1)}
    wall = round(time.time() - t0, 1)
    if rc != 0 or not os.path.exists(outp):
        lines = [l for l in (err or "").strip().splitlines() if l.strip()]
        return {"status": "CRASH", "rc": rc, "wall_s": wall,
                "error": (lines[-1] if lines else "no output file")[:200]}
    with open(outp, encoding="utf-8") as fh:
        res = json.load(fh)
    rec = extract(res, t.kind)
    rec.update(status="OK", wall_s=wall)
    return rec


def extract(d, kind):
    if kind == "pilot":
        pc, ch, nt = d.get("positive_meets_success"), d.get("cheat_detected"), d.get("null_twin_meets_success")
        verdict = "PILOT_PASS" if d.get("pilot_pass") else "PILOT_FAIL"
        cls = "POS" if verdict == "PILOT_PASS" else "INSTR"
        return dict(verdict=verdict, cls=cls, pc=pc, ch=ch, nt=nt, anomalies=[])
    if kind == "pass4":
        c = d.get("controls", {})
        pc, ch = c.get("positive_detected"), c.get("cheat_detected")
        verdict = d.get("predicate")
        if verdict in POS:
            cls = "POS"
        elif verdict == "PARK":
            cls = "NEG" if (pc and ch) else "INSTR"
        else:
            cls = "OTHER"
        r = d.get("R", {})
        return dict(verdict=verdict, cls=cls, pc=pc, ch=ch, nt=None,
                    r_reproduced=r.get("reproduced"), anomalies=d.get("anomalies", []),
                    text=json.dumps([d.get("notes"), d.get("anomalies")], default=str)[:4000])
    v = d.get("outcome")
    text = json.dumps([d.get("outcome_reason"), d.get("notes"), d.get("anomalies")], default=str)[:4000]
    cls = ("POS" if v in POS else "NEG" if v in NEG else "CONF" if v in CONF
           else "INSTR" if v in INSTR else "OTHER")
    return dict(verdict=v, cls=cls, pc=d.get("positive_control_detected"), ch=d.get("cheat_detected"),
                nt=d.get("null_twin_meets_success"), anomalies=d.get("anomalies", []), text=text)


# --------------------------------------------------------------------------- judging
CLEAN = {"POS", "NEG", "CONF"}


def judge(m, kind, B, X, aux):
    """Return (label, note). Labels: OK, UNINF, INSENSITIVE, SILENT, WRONG, REACTED_OTHER,
    BLIND, DETECTED, SHIFTED, CRASH, CRASH_SCHEMA, TIMEOUT, UNDET, ASYM, NA
    (UNTESTABLE is assigned by run_all to lenient re-runs whose verdict may rest on stale fields)."""
    if X is None:
        return "NA", "mutation not applicable (arm absent)"
    if X["status"] == "CRASH":
        err = X.get("error", "")
        if _schema_crash(X, aux.get("row_keys", ())):
            return "CRASH_SCHEMA", err + " (row field absent from the mutated arm)"
        return "CRASH", err
    if X["status"] == "TIMEOUT":
        return "TIMEOUT", ""
    bc, xc = B["cls"], X["cls"]
    flags = lambda R: (R["verdict"], R.get("pc"), R.get("ch"), R.get("nt"))
    same = flags(B) == flags(X)

    if kind == "pilot":
        if m == "M2":   # NT := PC  -> PC must no longer beat its twin
            if B.get("pc") is False:
                return "UNINF", "PC already not detected at baseline"
            return ("INSENSITIVE", "PC still 'meets success' against a twin that IS the PC") if X.get("pc") \
                else ("OK", "PC no longer detected")
        if m == "M4":
            if X.get("pc"):
                return "INSENSITIVE", "PC detected with zero PC rows"
            return ("UNINF", "PC already not detected at baseline") if B.get("pc") is False else ("OK", "")
        if m == "M4c":
            if X.get("ch"):
                return "INSENSITIVE", "cheat detected with zero CHEAT rows"
            return ("UNINF", "cheat already undetected at baseline") if B.get("ch") is False else ("OK", "")
        if m == "M5":   # CHEAT := NT -> cheat must not be detected
            if B.get("ch") is False:
                return "UNINF", "cheat already undetected at baseline"
            return ("INSENSITIVE", "cheat 'detected' on null-twin data") if X.get("ch") else ("OK", "")
        if m == "M6":
            return _judge_m6(B, X)
        if m == "M7":
            return ("INSENSITIVE", "all control flags unchanged") if same else ("OK", f"{flags(B)} -> {flags(X)}")
        return "NA", ""

    if m == "M1":
        if bc == "INSTR":
            return ("OK", "") if xc == "INSTR" else ("WRONG", f"instrument verdict moved by a T/NT swap -> {X['verdict']}")
        if bc == "POS":
            if xc == "POS":
                return "INSENSITIVE", "still positive after treatment and null twin swapped"
            if xc == "CONF" or kind == "pass4":   # pass4 predicates have no CONFOUNDED class
                return "OK", f"-> {X['verdict']}"
            return "REACTED_OTHER", f"-> {X['verdict']} (expected CONFOUNDED)"
        if bc == "NEG":
            if xc == "NEG":
                return "OK", "invariant held"
            if xc == "INSTR":
                return "REACTED_OTHER", f"NULL -> {X['verdict']}: the control gate reads NULL_TWIN as its reference"
            if xc == "CONF":
                return "ASYM", "twin rule fires on treatment data that fails the success rule (twin rule != success rule)"
            return "WRONG", f"NULL -> {X['verdict']} although neither arm's data meets success at baseline"
        if bc == "CONF":
            return ("OK", f"-> {X['verdict']}") if xc in ("POS", "CONF") else ("WRONG", f"-> {X['verdict']}")
    if m == "M2":
        if bc == "INSTR":
            return ("OK", "") if xc == "INSTR" else ("WRONG", f"-> {X['verdict']}")
        if bc == "POS":
            if xc == "POS":
                return "INSENSITIVE", "SIGNAL with a null twin identical to treatment"
            if xc == "CONF" or kind == "pass4":
                return "OK", f"-> {X['verdict']}"
            return "REACTED_OTHER", f"-> {X['verdict']} (expected CONFOUNDED)"
        if bc == "NEG":
            if xc == "POS":
                return "WRONG", "NULL -> SIGNAL after twin made equal to treatment"
            if X.get("nt"):
                return "ASYM", "twin (= failing treatment) 'meets success': twin rule != success rule"
            return "OK", "invariant held"
        if bc == "CONF":
            return ("WRONG", "-> positive") if xc == "POS" else ("OK", f"-> {X['verdict']}")
    if m in ("M3a", "M3b"):
        src = "CONTROL" if m == "M3a" else "NULL_TWIN"
        if bc == "INSTR":
            return ("OK", "") if xc == "INSTR" else ("WRONG", f"-> {X['verdict']}")
        if xc == "POS":
            return ("INSENSITIVE", f"positive with TREATMENT == {src}") if bc == "POS" \
                else ("WRONG", f"{B['verdict']} -> positive with TREATMENT == {src}")
        if bc == "POS":
            return "OK", f"-> {X['verdict']}"
        return "OK", "invariant held" if xc == bc else f"-> {X['verdict']}"
    if m == "M4":
        if X.get("pc"):
            return "INSENSITIVE", f"PC detected with zero PC rows ({X['verdict']})"
        if xc in CLEAN:
            return "INSENSITIVE", f"clean verdict {X['verdict']} without positive controls"
        if bc == "INSTR" and B.get("pc") is False:
            return "UNINF", "baseline already instrument-failed on PC"
        return "OK", f"-> {X['verdict']}"
    if m == "M5":
        ts = True if bc == "POS" else False if bc == "NEG" else aux.get("t_success")
        if X.get("ch"):
            if ts is False:
                return "INSENSITIVE", "cheat still 'detected' on (failing) treatment data"
            if ts is None:
                return "UNDET", f"cheat detected; treatment success unknown ({X['verdict']})"
            return "OK", "cheat criterion = success criterion; treatment succeeds"
        if xc in CLEAN:
            return "SILENT", f"cheat undetected but clean verdict {X['verdict']}"
        if B.get("ch") is False:
            return "UNINF", "cheat already undetected at baseline"
        return "OK", f"cheat undetected -> {X['verdict']}"
    if m == "M4c":
        if X.get("ch"):
            return "INSENSITIVE", f"cheat detected with zero CHEAT rows ({X['verdict']})"
        if xc in CLEAN:
            return "INSENSITIVE", f"clean verdict {X['verdict']} without a cheat control"
        if B.get("ch") is False:
            return "UNINF", "cheat already undetected at baseline"
        return "OK", f"-> {X['verdict']}"
    if m == "M6":
        return _judge_m6(B, X)
    if m == "M7":
        if bc in CLEAN:
            if same and bc == "POS":
                return "INSENSITIVE", f"{B['verdict']} and all control flags unchanged"
            if same:
                return "UNINF", f"{B['verdict']} unchanged (mixing arms of a non-positive world may stay non-positive)"
            if xc == bc:
                return "REACTED_OTHER", f"flags moved {flags(B)[1:]} -> {flags(X)[1:]}, verdict kept"
            return ("OK", f"-> {X['verdict']}") if xc == "INSTR" else ("REACTED_OTHER", f"-> {X['verdict']}")
        if xc in CLEAN:
            return "WRONG", f"instrument failure -> clean {X['verdict']} after label shuffle"
        return "UNINF", "baseline already instrument-failed"
    return "NA", ""


DUP_WORDS = ("duplicat", "replicat", "zero variance", "same seed", "degenerate", "pseudo")


def _judge_m6(B, X):
    """M6 asks: does the evaluator notice that every seed carries seed s0's data?"""
    txt = json.dumps(X.get("anomalies", [])).lower()
    btxt = json.dumps(B.get("anomalies", [])).lower()
    if any(w in txt and w not in btxt for w in DUP_WORDS):
        return "DETECTED", "anomaly text flags duplication"
    if X["cls"] == "INSTR" and B["cls"] != "INSTR":
        t = X.get("text", "").lower()
        if "reproduc" in t or "attainability" in t or "frozen" in t:
            return "DETECTED", f"-> {X['verdict']} via frozen-control reproducibility check (values changed), not a duplication test"
        return "DETECTED", f"-> {X['verdict']} incidentally (control flags pc={X.get('pc')} ch={X.get('ch')}), not a duplication test"
    if (X["verdict"], X.get("pc"), X.get("ch"), X.get("nt")) != (B["verdict"], B.get("pc"), B.get("ch"), B.get("nt")):
        return "SHIFTED", f"{B['verdict']} -> {X['verdict']} (flags pc/ch/nt {B.get('pc')}/{B.get('ch')}/{B.get('nt')} -> {X.get('pc')}/{X.get('ch')}/{X.get('nt')}), no duplication flag"
    return "BLIND", "pseudo-replicated seeds accepted silently"


# --------------------------------------------------------------------------- driver
ORDER = ["M1", "M2", "M3a", "M3b", "M4", "M4c", "M5", "M6", "M7"]


def _jsonable(info):
    return {k: sorted(v) if isinstance(v, set) else v for k, v in info.items()}


def run_all(targets, scratch, timeout=60, workers=6, seed=20260930, log=print):
    """Baseline every evaluator, then every applicable mutation; a copy mutation
    that dies with CRASH-SCHEMA is re-run once in lenient mode (dst-only keys
    kept), and both results are reported."""
    plan, infos, row_keys, src_rows = {}, {}, {}, {}
    for t in targets:
        edir = os.path.join(t.copy_root, t.eval_rel) if t.eval_rel else t.copy_root
        rows = load_rows(os.path.join(edir, t.rows_file))
        src_rows[t.tid] = rows
        t.roles = resolve_roles(t, rows)
        row_keys[t.tid] = set().union(*[set(r) for r in rows])
        plan[t.tid] = {"BASE": None}
        for m in ORDER:
            info = {}
            plan[t.tid][m] = mutate(m, rows, t.roles, t.kind, random.Random(f"{seed}:{t.tid}:{m}"), info=info)
            infos[(t.tid, m)] = info
    tmap = {t.tid: t for t in targets}
    results = {t.tid: {} for t in targets}

    def job(tid, m):
        rows = plan[tid][m]
        if m != "BASE" and rows is None:
            return tid, m, None
        r = run_one(tmap[tid], m, rows, scratch, timeout)
        log(f"{tid:40s} {m:6s} {r['status']:7s} {r.get('verdict', r.get('error', ''))!s:.60} ({r['wall_s']}s)")
        return tid, m, r

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for tid, m, r in ex.map(lambda a: job(*a), [(t.tid, "BASE") for t in targets]):
            results[tid]["BASE"] = r
        live = [t for t in targets if results[t.tid]["BASE"]["status"] == "OK"]
        jobs = [(t.tid, m) for t in live for m in ORDER]
        for tid, m, r in ex.map(lambda a: job(*a), jobs):
            results[tid][m] = r
        # lenient fallback for schema crashes of copy mutations
        retry = []
        for t in live:
            for m in COPY_MUTS:
                X = results[t.tid].get(m)
                if X and X["status"] == "CRASH" and _schema_crash(X, row_keys[t.tid]):
                    info = {}
                    plan[t.tid][m + "~"] = mutate(m, src_rows[t.tid], t.roles, t.kind, None, lenient=True, info=info)
                    infos[(t.tid, m + "~")] = info
                    retry.append((t.tid, m + "~"))
        for tid, m, r in ex.map(lambda a: job(*a), retry):
            results[tid][m] = r

    table = []
    for t in targets:
        B = results[t.tid]["BASE"]
        row = {"tid": t.tid, "kind": t.kind, "roles": t.roles, "base": B, "committed": committed(t), "cells": {}}
        if B["status"] != "OK":
            row["skip"] = ("SKIPPED (>%ds)" % timeout) if B["status"] == "TIMEOUT" else f"BASELINE {B['status']}: {B.get('error', '')}"
            table.append(row)
            continue
        m1 = results[t.tid].get("M1") or {}
        if m1.get("status") != "OK":
            m1 = results[t.tid].get("M1~") or {}
        aux = {"t_success": m1.get("nt") if m1.get("status") == "OK" else None,
               "row_keys": row_keys[t.tid]}
        for m in ORDER:
            X = results[t.tid].get(m)
            lab, note = judge(m, t.kind, B, X, aux)
            cell = {"label": lab, "note": note, "result": X, "info": _jsonable(infos.get((t.tid, m), {}))}
            if (t.tid, m + "~") in infos:
                XL = results[t.tid].get(m + "~")
                labl, notel = judge(m, t.kind, B, XL, aux)
                kept = infos[(t.tid, m + "~")].get("dst_only_keys", set())
                read = sorted(k for k in kept if _reads_key(t, k))
                if labl in ("INSENSITIVE", "SILENT", "WRONG") and read:
                    labl, notel = "UNTESTABLE", (f"lenient run kept stale dst-only fields the evaluator reads "
                                                 f"{read}; raw lenient label {labl}: {notel}")
                cell["lenient"] = {"label": labl, "note": notel, "result": XL,
                                   "info": _jsonable(infos[(t.tid, m + "~")])}
            row["cells"][m] = cell
        table.append(row)
    return table


def _reads_key(t, key):
    """True if the evaluator directory's python source names `key` as a string literal."""
    edir = os.path.join(t.copy_root, t.eval_rel) if t.eval_rel else t.copy_root
    pats = (f'"{key}"', f"'{key}'")
    for fn in os.listdir(edir):
        if fn.endswith(".py"):
            with open(os.path.join(edir, fn), encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            if any(pt in src for pt in pats):
                return True
    return False


def _schema_crash(X, keys):
    err = X.get("error", "")
    return err.startswith("KeyError: '") and err[len("KeyError: '"):-1] in keys


def committed(t):
    edir = os.path.join(t.copy_root, t.eval_rel) if t.eval_rel else t.copy_root
    p = os.path.join(edir, t.out_file)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return extract(json.load(fh), t.kind)["verdict"]


SHORT = {"OK": "ok", "UNINF": "u", "INSENSITIVE": "INSENS", "SILENT": "SILENT", "WRONG": "WRONG",
         "REACTED_OTHER": "ok*", "BLIND": "blind", "DETECTED": "det", "SHIFTED": "shift",
         "CRASH": "CRASH", "CRASH_SCHEMA": "crash-s", "TIMEOUT": "T/O", "NA": "-", "UNDET": "?",
         "ASYM": "asym", "UNTESTABLE": "untest"}


def render_md(table, timeout):
    L = []
    L.append("| evaluator | kind | baseline | " + " | ".join(ORDER) + " |")
    L.append("|---|---|---|" + "---|" * len(ORDER))
    for row in table:
        if "skip" in row:
            L.append(f"| {row['tid']} | {row['kind']} | {row['skip']} |" + " |" * len(ORDER))
            continue
        b = row["base"]["verdict"]
        if row["committed"] is not None and row["committed"] != b:
            b += f" (committed {row['committed']}!)"
        cells = []
        for m in ORDER:
            c = row["cells"][m]
            txt = SHORT[c["label"]]
            if "lenient" in c:
                txt += " / " + SHORT[c["lenient"]["label"]] + "~"
            cells.append(txt)
        L.append(f"| {row['tid']} | {row['kind']} | {b} | " + " | ".join(cells) + " |")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--programs", default=PROGRAMS)
    ap.add_argument("--only", default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    if os.path.abspath(a.scratch).startswith(os.path.abspath(a.programs)):
        sys.exit("scratch must be outside hecate/programs")
    targets = discover(a.programs)
    if a.only:
        targets = [t for t in targets if a.only in t.tid]
    os.makedirs(a.scratch, exist_ok=True)
    t0 = time.time()
    table = run_all(targets, a.scratch, a.timeout, a.workers)
    print(render_md(table, a.timeout))
    print(f"[{len(targets)} evaluators, {time.time() - t0:.0f}s wall]")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(table, fh, indent=1, default=str)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(render_md(table, a.timeout) + "\n")


if __name__ == "__main__":
    main()
