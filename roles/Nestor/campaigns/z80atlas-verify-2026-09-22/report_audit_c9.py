"""Cycle-9 report audit: recompute every load-bearing number from the RAW bundle files,
independently of adjudicate_c9.py and hypotheses.py, and fail the report on any
disagreement.

Independent means: this file opens the bundle JSON files itself, groups them with the
frozen manifest itself, and re-derives H1's M and I, H2's per-specimen B/C counts and
verdicts, the panel verdict, and H3's certificate counts and separations with its own
code. Only the thresholds are shared, from the hash-covered constants object. It then
checks that
  * the MACHINE block equals the recomputation;
  * every number and verdict word in the prose also appears in the MACHINE block (no
    prose-only claims);
  * the report names the frozen protocol hash.

    python report_audit_c9.py [observatory]   -> AUDIT_C9.json; exit 0 iff PASS
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from constants import C   # noqa: E402

BEGIN, END = "<!-- MACHINE-BEGIN", "MACHINE-END -->"
KW = "__run_kwargs__"


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def bundle_id(b):
    """Recompute the content address exactly as the P-7 spec does, from the manifest."""
    roles = {"H1": {"gate_on_cost_vm": "TREATMENT", "gate_off_cost_vm": "CONTROL"},
             "H2": {"B_reimplant_actual": "TREATMENT", "C_reimplant_random": "CONTROL"},
             "H3": {"A_easy_plus_migration": "TREATMENT",
                    "B_homogeneous_same_migration": "CONTROL"}}.get(b["hypothesis_id"], {})
    arms = sorted(({"name": a["arm"], "role": roles.get(a["arm"], "INTERVENTION"),
                    "cell": dict(a["cell"], **{KW: a.get("kwargs") or {}}),
                    "seed": int(a["seed"]), "tier": a["tier"]} for a in b["arms"]),
                  key=lambda a: a["name"])
    import bundles as BD
    body = {"hypothesis_id": b["hypothesis_id"], "pair_seed": int(b["pair_seed"]), "arms": arms,
            "factor_deltas": b.get("factor_deltas") or {},
            "expected_cardinality": b["expected_cardinality"],
            "protocol_version": BD.PROTOCOL_VERSION}
    return hashlib.sha256(_canon(body).encode("ascii")).hexdigest()


def raw(obs, manifest):
    out = defaultdict(list)
    for b in manifest["bundles"]:
        p = pathlib.Path(obs) / "bundles" / (bundle_id(b) + ".json")
        res = json.loads(p.read_text())["results"] if p.exists() else {}
        out[b["hypothesis_id"]].append((b, res))
    return out


def recompute(obs, manifest):
    R = raw(obs, manifest)
    m = {}
    if R.get("H1"):
        arms = ("gate_off_cost_vm", "gate_on_cost_vm", "gate_off_cost_free", "gate_on_cost_free")
        comp = [r for _, r in R["H1"] if all(a in r for a in arms)]
        if comp:
            mu = {a: sum((r[a].get("held_max_final") or 0.0) for r in comp) / len(comp) for a in arms}
            M = ((mu["gate_on_cost_vm"] + mu["gate_on_cost_free"]) - (mu["gate_off_cost_vm"] + mu["gate_off_cost_free"])) / 2
            I = (mu["gate_on_cost_free"] - mu["gate_off_cost_free"]) - (mu["gate_on_cost_vm"] - mu["gate_off_cost_vm"])
            t = C["H1_THRESHOLD"]
            v = ("GATE_EFFECT_AND_COST_INTERACTION" if abs(M) >= t and abs(I) >= t else
                 "GATE_EFFECT" if abs(M) >= t else "COST_INTERACTION_ONLY" if abs(I) >= t else
                 "NO_DETECTED_EFFECT")
            m["H1"] = {"verdict": v, "n_complete": len(comp), "M": round(M, 4), "I": round(I, 4),
                       "threshold": C["H1_THRESHOLD"],
                       "means_held_final": {a: round(x, 4) for a, x in mu.items()}}
        else:
            m["H1"] = {"verdict": "INCOMPLETE", "n_complete": 0, "M": None, "I": None,
                       "threshold": C["H1_THRESHOLD"], "means_held_final": None}
    if R.get("H2"):
        spec = defaultdict(lambda: {"stratum": None, "rows": []})
        for b, r in R["H2"]:
            spec[b["specimen"]]["stratum"] = tuple(b["stratum"])
            spec[b["specimen"]]["rows"].append(r)

        def reach(s, d, key):
            return (s.get(key) or 0) >= d

        def per(key):
            out = {}
            for k, v in spec.items():
                rows = v["rows"]
                arms_ok = all(len(r) == 3 for r in rows)
                bh = sum(reach(r["B_reimplant_actual"], C["CAUSAL_DEPTH"], key) for r in rows) if arms_ok else None
                ch = sum(reach(r["C_reimplant_random"], C["CAUSAL_DEPTH"], key) for r in rows) if arms_ok else None
                if not arms_ok or len(rows) != C["H2_SEEDS"]:
                    verdict = "INCOMPLETE"
                elif bh >= C["H2_B_MIN"] and ch <= C["H2_C_MAX"]:
                    verdict = "SUPPORTS"
                else:
                    verdict = "DOES_NOT_SUPPORT"
                out[k] = {"verdict": verdict, "B_reaching": bh, "C_reaching": ch}
            sup = sorted(k for k, v in out.items() if v["verdict"] == "SUPPORTS")
            strata = {spec[k]["stratum"] for k in sup}
            pv = ("PANEL_POSITIVE" if len(strata) >= C["H2_PANEL_MIN_SPECIMENS"] else
                  "ISOLATED_CANDIDATE" if len(sup) == 1 else
                  "SAME_STRATUM_CANDIDATES" if len(sup) > 1 else
                  "REPLICATION_EVENTS_WITHOUT_PROPAGATION")
            return out, sup, strata, pv
        out, sup, strata, pv = per("max_causal_replication_depth")
        _o, _s, _st, pv_lit = per("max_causal_replication_depth_literal")
        m["H2"] = {"verdict": pv, "supporting": sup, "distinct_supporting_strata": len(strata),
                   "per_specimen": dict(sorted(out.items())), "sensitivity_literal_verdict": pv_lit}
    if R.get("H3"):
        arms = ("A_easy_plus_migration", "B_homogeneous_same_migration", "C_easy_no_migration")
        comp = [r for _, r in R["H3"] if all(a in r for a in arms)]
        if comp:
            cnt = {a: sum(bool(r[a].get("has_reservoir_certificate")) for r in comp) for a in arms}
            n = len(comp)
            sb = round(cnt[arms[0]] / n - cnt[arms[1]] / n, 4)
            sc = round(cnt[arms[0]] / n - cnt[arms[2]] / n, 4)
            v = ("NOT_DEMONSTRATED" if cnt[arms[0]] < C["H3_MIN_CERTIFICATES"] else
                 "RESERVOIR_SUPPORTED" if sb >= C["H3_SEPARATION"] and sc >= C["H3_SEPARATION"] else
                 "NO_SEPARATION")
            m["H3"] = {"verdict": v, "n_complete": n, "certificates": cnt,
                       "separation_vs_B": sb, "separation_vs_C": sc}
        else:
            m["H3"] = {"verdict": "INCOMPLETE", "n_complete": 0, "certificates": None,
                       "separation_vs_B": None, "separation_vs_C": None}
    return m


def audit(obs, manifest, freeze=None):
    obs = pathlib.Path(obs)
    text = (obs / "REPORT_C9.md").read_text(encoding="utf-8")
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    try:
        block = json.loads(text.split(BEGIN, 1)[1].split(END, 1)[0])
    except Exception as e:                                           # noqa: BLE001
        chk("machine block parses", False, str(e))
        return checks
    chk("machine block parses", True)
    rc = recompute(obs, manifest)
    for h, v in rc.items():
        got = block.get(h)
        for k, val in v.items():
            chk("%s.%s recomputed from raw bundles" % (h, k),
                got is not None and _canon(got.get(k)) == _canon(val),
                "report %s vs recomputed %s" % (json.dumps((got or {}).get(k))[:120], json.dumps(val)[:120]))
    prose = text.split(END, 1)[1]
    bl = json.dumps(block)
    words = set(re.findall(r"\*\*([A-Z_]+)\*\*", prose))
    chk("every verdict word in the prose is in the machine block",
        all(w in bl for w in words), "prose verdicts %s" % sorted(words))
    # A decimal may end a sentence ("... = 0.25."), so trailing punctuation is allowed;
    # the negative control "prose-only number added" failed on exactly that case.
    nums = set(re.findall(r"(?<![\w.])-?\d+\.\d+(?=[^\w]|$)", prose))
    missing = [x for x in nums if x not in bl]
    chk("every decimal number in the prose is in the machine block", not missing,
        "prose-only numbers: %s" % missing[:8])
    rows = re.findall(r"^\| (\S+) \| ([A-Z_]+) \| (\S+) \| (\S+) \|$", prose, flags=re.M)
    ps = (block.get("H2") or {}).get("per_specimen") or {}
    bad_rows = [r for r in rows if r[0] in ps and
                (r[1], r[2], r[3]) != (ps[r[0]]["verdict"], str(ps[r[0]]["B_reaching"]), str(ps[r[0]]["C_reaching"]))]
    chk("every H2 table row equals the machine block", not bad_rows and len(rows) == len(ps),
        "rows %d, specimens %d, mismatched %s" % (len(rows), len(ps), bad_rows[:3]))
    if freeze:
        chk("report names the frozen protocol hash", freeze["protocol_hash"] in text)
    return checks


def main(argv):
    obs = HERE / (argv[1] if len(argv) > 1 else "observatory")
    manifest = json.loads((HERE / "MANIFEST_FROZEN.json").read_text())
    freeze = json.loads((HERE / "FREEZE.json").read_text()) if (HERE / "FREEZE.json").exists() else None
    checks = audit(obs, manifest, freeze)
    ok = all(c["pass"] for c in checks)
    (obs / "AUDIT_C9.json").write_text(json.dumps({"ok": ok, "checks": checks}, indent=1))
    for c in checks:
        if not c["pass"]:
            print("FAIL", c["check"], c["detail"])
    print("AUDIT_C9:", "PASS" if ok else "FAIL", "(%d checks)" % len(checks))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
