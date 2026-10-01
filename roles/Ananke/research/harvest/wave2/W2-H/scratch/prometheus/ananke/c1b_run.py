"""PTE-C1b driver (PREREG_PTE_C1b.md v1 + A1-A3). Fail-closed.

    python -m prometheus.ananke.c1b_run --plan                 # list cells; runs nothing
    python -m prometheus.ananke.c1b_run --home <H> --release <comms id>

It refuses to run unless: prometheus/ananke and the prereg are clean in
git; the code SHA and the prereg sha256 equal roles/Ananke/pte/c1b/
FREEZE_C1b.json; and --release names a comms message that passes check_release():
from Aporia, kind ruling, to Ananke, subject starting with the exact token
"C1B HOLD RELEASE:", created after the freeze commit, and naming that commit
in its body (#696/#699; the operator HOLD of 2026-09-25 can be lifted only
by Aporia over comms). Stages:
  S1 specimen batteries (M2, M3) on C1b held-out worlds
  S2 fresh-seed searches, 4 per specimen, and their batteries
  S3 CORRECTED_WINDOW_RECHECK on every C1 D-wave adjudicated cell
Hard cap 3 h (PREREG s6); unrun cells are CENSORED; PARK after 5
consecutive failed cells.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import gzip
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import traceback

import numpy as np

from . import c1b, envs, search
from .physics import Physics
from .rng import H_int

REPO = pathlib.Path(__file__).resolve().parents[2]
PREREG = REPO / "roles/Ananke/pte/PREREG_PTE_C1b.md"
FREEZE = REPO / "roles/Ananke/pte/c1b/FREEZE_C1b.json"
ELIG = REPO / "roles/Ananke/pte/c1b/ELIGIBILITY_dev.json"
CAP_S = 3 * 3600
N_FRESH = 4
PARK_AFTER = 5

Z_NEEDS = ("DELAY_LINE_SPECIMEN", "IN_FLIGHT_UNDECODED", "IN_FLIGHT_PLUS_JOINT")
B_NEEDS = ("DELAY_LINE_SPECIMEN", "IN_FLIGHT_UNDECODED")
WORDING = ("SETRULE is required; routing could not carry anything (dest_mode all). "
           "NOT: the rule, rather than routing, was shown to carry it. (A2.1)")


# ------------------------------------------------------------ guards
def lf_sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def git(*a) -> str:
    return subprocess.check_output(["git", *a], cwd=REPO, text=True).strip()


def guard(release: str | None) -> dict:
    problems = []
    dirty = git("status", "--porcelain", "prometheus/ananke", str(PREREG.relative_to(REPO)),
                "roles/Ananke/pte/c1b")
    if dirty:
        problems.append("dirty tree: " + dirty.replace("\n", "; "))
    if not FREEZE.exists():
        problems.append("no FREEZE_C1b.json (code freeze not done)")
        fz = {}
    else:
        fz = json.loads(FREEZE.read_text())
        code = git("rev-parse", "HEAD")
        if git("log", "-1", "--format=%H", "--", "prometheus/ananke") != fz.get("code_tree_commit"):
            problems.append("prometheus/ananke changed since the freeze")
        if lf_sha256(PREREG) != fz.get("prereg_sha256"):
            problems.append("prereg sha256 differs from the freeze")
        fz["head"] = code
    if not release:
        problems.append("no --release: the operator HOLD stands until Aporia releases it on comms")
    else:
        try:
            commit, when = freeze_commit()
            problems += check_release(fetch_message(release), commit, when)
        except Exception as e:                          # noqa: BLE001
            problems.append(f"cannot verify comms #{release}: {e}")
    if problems:
        raise SystemExit("C1b driver REFUSES to start:\n  " + "\n  ".join(problems))
    return fz


RELEASE_TOKEN = "C1B HOLD RELEASE:"      # #696/#699: exact subject prefix, case-sensitive


def freeze_commit() -> tuple[str, datetime.datetime]:
    """The commit that last wrote FREEZE_C1b.json, and its commit time."""
    rel = str(FREEZE.relative_to(REPO))
    sha = git("log", "-1", "--format=%H", "--", rel)
    if not sha:
        raise RuntimeError("FREEZE_C1b.json is not committed")
    return sha, datetime.datetime.fromisoformat(git("show", "-s", "--format=%cI", sha))


def fetch_message(msg_id) -> dict:
    """The full comms message (with body) from Ananke's inbox."""
    out = subprocess.check_output([sys.executable, "-m", "comms", "inbox", "--all", "--json",
                                   "Ananke"], cwd=REPO, text=True)
    d = json.loads(out)
    msgs = d if isinstance(d, list) else d.get("messages", d)
    for m in msgs:
        if str(m.get("id")) == str(msg_id):
            return m
    raise KeyError(f"comms #{msg_id} not in Ananke's inbox")


def check_release(m: dict, commit: str, frozen_at: datetime.datetime) -> list[str]:
    """ALL of (#696): sender Aporia; subject STARTS WITH the exact token;
    kind == ruling; Ananke among the recipients; created after the freeze
    commit; the body names the freeze commit (>= 9 hex chars of its SHA).
    Returns the list of failures (empty = a valid release)."""
    bad = []
    if m.get("sender") != "Aporia":
        bad.append("sender is not Aporia")
    if not (m.get("subject") or "").startswith(RELEASE_TOKEN):
        bad.append(f"subject does not start with {RELEASE_TOKEN!r}")
    if m.get("kind") != "ruling":
        bad.append("kind is not ruling")
    if "Ananke" not in (m.get("recipients") or []):
        bad.append("Ananke is not a recipient")
    try:
        created = datetime.datetime.fromisoformat(str(m.get("created_at")))
        if created <= frozen_at:
            bad.append("created before the freeze commit")
    except ValueError:
        bad.append("unparseable created_at")
    words = re.findall(r"[0-9a-f]{9,40}", m.get("body") or "")
    if not any(commit.startswith(w) for w in words):
        bad.append(f"body does not name the freeze commit {commit[:9]}")
    return [f"comms #{m.get('id')}: {b}" for b in bad]


# ------------------------------------------------------------ specimens
def load(cell_id: str):
    r = c1b.specimen_row(cell_id, str(REPO / c1b.ROWS))
    return (Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"]),
            np.asarray(r["result"]["champion"], dtype=np.int64), r)


def d_wave_cells() -> list[dict]:
    out = []
    with gzip.open(REPO / c1b.ROWS, "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["wave"] == "D" and r["kind"] == "adjudicate":
                out.append(r)
    return out


def plan() -> dict:
    return {
        "S1": [f"{m}:{cid}" for m, ids in c1b.SPECIMENS.items() for cid in ids],
        "S2": [f"{m}:{cid}:fresh{k}" for m, ids in c1b.SPECIMENS.items() for cid in ids
               for k in range(N_FRESH)],
        "S3": [r["cell_id"] for r in d_wave_cells()],
    }


# ------------------------------------------------------------ readings
def read_m2(res: dict, env) -> dict:
    n, n1 = res["normal"]["run"], res["normal_from1"]["run"]
    b = {"A": c1b.kills(res["flush_inflight"]),
         "Z": c1b.intact(res["flush_inflight_iti"], n1),
         "B": c1b.intact(res["reset_all_nonpacket"], n),
         "C": c1b.census_predicts(n, "c_inflight_sum", c1b.ticks(env)["mid"])["pass"],
         "I": c1b.drops(res["reset_inbox"], n)}
    for x in ("S", "Kp", "w", "En"):
        b["K_" + x] = c1b.drops(res["reset_" + x], n)
    return b


def label_m2(b: dict, not_eligible: list) -> str:
    lab = c1b.m2_label(b)
    base = lab.split(":")[0]
    needs_z = base in Z_NEEDS or (base == "MIXED" and "in_flight" in lab)
    needs_b = base in B_NEEDS
    if ("Z" in not_eligible and needs_z) or ("B" in not_eligible and needs_b):
        lab += "_UNRESOLVED"
    return lab


def read_m3(res: dict, env, ph: Physics) -> dict:
    n = res["normal"]["run"]
    c1_lo = c1b.ci(res["drop_window_c1"]["run"].pairs)[1] if res["drop_window_c1"]["status"] == "RAN" \
        else c1b.ci(n.pairs)[1]
    ro_kill = c1b.kills(res["drop_readout_tick_only"])
    cor_kill = c1b.kills(res["drop_window_corrected"])
    routing_inert = ph.dest_mode == "all"
    r_rule = c1b.drops(res["freeze_rule"], n)
    r_route = True if routing_inert else c1b.intact(res["freeze_routing"], n)
    return {"T": bool(ro_kill and cor_kill and c1_lo >= c1b.C1_INTACT_LO),
            "X": c1b.kills(res["drop_window_c1"]),
            "R": bool(r_rule and r_route),
            "M": c1b.rule_predicts(n, c1b.ticks(env)["ro"])["pass"],
            "_positive_components": {"readout_tick_only_kills": ro_kill,
                                     "corrected_window_kills": cor_kill,
                                     "c1_window_lo99": c1_lo},
            "_routing": "INERT_BY_PHYSICS" if routing_inert else "LIVE"}


def label_m3(b: dict, not_eligible: list, routing_resolved: bool) -> str:
    core = {k: b[k] for k in c1b.M3_KEYS}
    lab = c1b.m3_label(core, routing_resolved=routing_resolved)
    if "T_c1_window" in not_eligible and "TRANSPORT" in lab:
        lab += "_UNRESOLVED"
    if "not_R" in not_eligible and not b["R"] and lab in ("TRANSPORT_ONLY", "NOT_SUPPORTED"):
        lab += "_UNRESOLVED"
    return lab


def summarise(res: dict) -> dict:
    return {k: {"status": v["status"], "acc": c1b.ci(v["run"].pairs)} for k, v in res.items()}


# ------------------------------------------------------------ stages
class Store:
    def __init__(self, home: pathlib.Path, receipt: dict):
        self.dir = home / "pte-c1b"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.rows = self.dir / "rows.jsonl"
        self.receipt = receipt

    def append(self, row: dict):
        row = dict(row, receipt=self.receipt, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        with self.rows.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=_js) + "\n")


def _js(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def battery_row(mech: str, cid: str, ph, env, genome, seeds, elig: dict, device) -> dict:
    ne = elig.get(cid, {}).get("NOT_ELIGIBLE", [])
    if mech == "M2":
        res = c1b.run_battery(c1b.m2_battery(ph, env), genome, env, seeds, device)
        b = read_m2(res, env)
        lab = label_m2(b, ne)
        n = res["normal"]["run"]
        extra = {"census": c1b.census_predicts(n, "c_inflight_sum", c1b.ticks(env)["mid"]),
                 "census_ro": c1b.census_predicts(n, "c_inflight_sum_ro", c1b.ticks(env)["mid"])}
    else:
        res = c1b.run_battery(c1b.m3_battery(ph, env), genome, env, seeds, device)
        b = read_m3(res, env, ph)
        routing_resolved = b["_routing"] == "INERT_BY_PHYSICS" or "F_route" not in ne
        lab = label_m3(b, ne, routing_resolved)
        extra = {"rule_predicts": c1b.rule_predicts(res["normal"]["run"], c1b.ticks(env)["ro"])}
        if b["_routing"] == "INERT_BY_PHYSICS" and "RULE_SWITCH" in lab:
            extra["wording"] = WORDING
    extra["carryover"] = c1b.carryover(res["normal"]["run"], env)
    return {"mechanism": mech, "cell": cid, "booleans": b, "label": lab, "not_eligible": ne,
            "arms": summarise(res), **extra}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--home", type=pathlib.Path)
    ap.add_argument("--release")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args(argv)
    if a.plan:
        print(json.dumps(plan(), indent=1))
        return 0
    fz = guard(a.release)
    assert a.home, "--home required"
    elig = json.loads(ELIG.read_text())["specimens"]
    receipt = {"code": fz["head"], "freeze": fz, "release_msg": a.release, "device": a.device}
    st = Store(a.home, receipt)
    seeds = c1b.assays.world_seeds(c1b.HELD_NS, c1b.H_WORLDS)
    t0 = time.time()
    fails = 0

    def budget_ok():
        return time.time() - t0 < CAP_S

    def cell(kind, fn):
        nonlocal fails
        if not budget_ok():
            st.append({"stage": kind, "status": "CENSORED"})
            return None
        try:
            row = fn()
            fails = 0
            st.append(dict(row, stage=kind, status="DONE"))
            return row
        except Exception:                                # noqa: BLE001
            fails += 1
            st.append({"stage": kind, "status": "FAILED", "error": traceback.format_exc()[-2000:]})
            if fails >= PARK_AFTER:
                (st.dir / "PARKED.json").write_text(json.dumps({"accountable": "Ananke",
                                                                 "after": PARK_AFTER}))
                raise SystemExit("PARKED after 5 consecutive failed cells")
            return None

    labels = {}
    for mech, ids in c1b.SPECIMENS.items():                                  # S1
        for cid in ids:
            ph, env, g, _ = load(cid)
            r = cell("S1", lambda: battery_row(mech, cid, ph, env, g, seeds, elig, a.device))
            labels[cid] = r and r["label"]
    for mi, (mech, ids) in enumerate(c1b.SPECIMENS.items()):                 # S2
        for ci_, cid in enumerate(ids):
            ph, env, _, row = load(cid)
            sp = search.SearchSpec(**{k: v for k, v in row["search"].items()
                                      if k in {f.name for f in dataclasses.fields(search.SearchSpec)}})
            for k in range(N_FRESH):
                sseed = H_int(c1b.SEARCH_NS, mi, ci_, k)

                def fresh(k=k, sseed=sseed):
                    ev = search.evolve(ph, env, sseed, sp, device=a.device)
                    champ = np.asarray(ev["champion"], dtype=np.int64)
                    out = {"mechanism": mech, "replicates": cid, "k": k, "search_seed": sseed,
                           "held": ev["held"],
                           "signal": ev["held"]["lo99"] > 0.55}
                    if out["signal"]:
                        br = battery_row(mech, f"{cid}:fresh{k}", ph, env, champ, seeds, elig, a.device)
                        out.update(label=br["label"], booleans=br["booleans"], arms=br["arms"])
                    return out
                cell("S2", fresh)
    for r in d_wave_cells():                                                 # S3
        def recheck(r=r):
            ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
            g = np.asarray(r["extra"]["genome"], dtype=np.int64)
            bat = c1b.m3_battery(ph, env)
            res = c1b.run_battery({k: bat[k] for k in ("normal", "drop_window_c1",
                                                       "drop_window_corrected",
                                                       "drop_readout_tick_only")}, g, env, seeds,
                                  a.device)
            return {"cell": r["extra"]["source_cell"], "family": env.family,
                    "label": "CORRECTED_WINDOW_RECHECK", "arms": summarise(res),
                    "frozen_routing_C1": "VACUOUS" if ph.dest_mode == "all" else "live",
                    "c1_packet_ablation": r["result"]["controls"].get("packet_ablation")}
        cell("S3", recheck)
    (st.dir / "DONE.json").write_text(json.dumps({"labels": labels, "wall_s": time.time() - t0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
