"""CAMPAIGN 4 LAUNCH GATE -- the machine-readable readiness check (directive section 1).

    python -m archaeon.campaign4.launch_gate [--ref origin/main] [--json]

This is NOT a science experiment. It exists to REFUSE. Exit code 0 only when every blocking
requirement is proven GREEN against the frozen surfaces; exit 1 otherwise, naming what is not
proven and who owns it.

Design rule, learned from campaigns 1-3: an instrument that cannot read its evidence reports
UNVERIFIED, never GREEN. "A seat said so in a message" is not proof; a message is a claim, and
this gate wants an artifact. Where only a claim exists, the item is CLAIMED_NOT_PROVEN and it
still blocks.

Requirements, verbatim from the directive:
  G1 Daedalus/SFE  campaign-rate long-run on 9.0.1 complete, no 5xx, no unexplained >5 s calls;
                   WAL bounded or explicitly accepted for the intended rate; crash/restart
                   recovery measured.
  G2 Archaeon+Viv  one synthetic Campaign-4-shaped specimen has travelled the full chain,
                   including a forced engine interruption and a reproducible terminal receipt.
  G3 Vivarium      Campaign-4 consumer identity live and its M2 B1 read grant valid.
  G4 PEW           drain the Vivarium outbox if the writer credential is available; otherwise
                   launch is permitted but the final disposition may not claim complete PEW
                   closure. CONDITIONAL, non-blocking by the directive's own words.
  G5 Proteus       population manifests and structural descriptors exist for the EXACT
                   Campaign-4 starting organisms; no organism of unknown ancestry in an arm.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"
OUT = C4 / "LAUNCH_GATE_RECEIPT.json"

GREEN = "GREEN"
RED = "RED"
UNVERIFIED = "UNVERIFIED"
CLAIMED = "CLAIMED_NOT_PROVEN"
CONDITIONAL = "CONDITIONAL"


def at_ref(ref: str, path: str) -> bytes | None:
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def ls_ref(ref: str, pattern: str) -> list:
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref], capture_output=True, text=True, cwd=str(REPO))
    return [ln for ln in r.stdout.splitlines() if pattern in ln]


def g1_engine(ref: str) -> dict:
    """The long-run + crash-recovery proof, read as MEASUREMENTS from the 9.0.1 receipt.

    Two rules that keyword matching would miss and that this gate exists to apply:

      (a) the evidence must be bound to the 9.0.1 build hash. The 50.7-minute long run in
          SFE_LONG_RUN_REPORT.md was measured on the PREVIOUS build (bc8d3a0c) and is the
          report that DISCOVERED the defect 9.0.1 repairs; it cannot also be its acceptance.

      (b) the campaign-rate acceptance run must be at least as long as the time it took the
          replaced defect to appear. The previous stall class first appeared about 14 minutes
          into the run, so an acceptance regime shorter than that cannot exclude its return.
    """
    import re
    p901 = "SerendipityFoundry/SerendipityFoundryEngine/docs/point_release_2026-09/SFE_901_REPAIR_RECEIPT.md"
    b = at_ref(ref, p901)
    if b is None:
        return {"id": "G1", "owner": "Daedalus", "requirement": "campaign-rate long run on 9.0.1 + WAL bound + crash/restart recovery measured",
                "status": UNVERIFIED, "evidence": {"receipt": "absent at " + p901}, "blocks_launch": True}
    t = b.decode("utf-8", "replace")
    build_ok = "699ca0f952448b41" in t
    regimes = []
    for m in re.finditer(r"(R\d\w*)\s+([\d.]+) s\s+5xx (\d+)\s+>5s (\d+).*?WAL max\s+([\d]+) MB.*?restart ([\d.]+) s", t):
        regimes.append({"regime": m.group(1), "seconds": float(m.group(2)), "http_5xx": int(m.group(3)),
                        "calls_over_5s": int(m.group(4)), "wal_max_mb": int(m.group(5)), "restart_s": float(m.group(6))})
    # Select the campaign-rate regime by DURATION, not by position in the table. Daedalus offered
    # to place the new long run first because this parser used to take the first match; an
    # instrument whose verdict depends on row order is a defect, and the producer should not have
    # to know its quirks. Every campaign-rate regime is reported; the longest one is the acceptance.
    camps = [r for r in regimes if "campaign_rate" in r["regime"]]
    camp = max(camps, key=lambda r: r["seconds"]) if camps else None
    PRIOR_DEFECT_APPEARED_S = 840          # ~14 min, SFE_LONG_RUN_REPORT.md
    checks = {
        "evidence_bound_to_901_build": build_ok,
        "regimes_parsed": len(regimes) > 0,
        "no_5xx_any_regime": bool(regimes) and all(r["http_5xx"] == 0 for r in regimes),
        "no_calls_over_5s_any_regime": bool(regimes) and all(r["calls_over_5s"] == 0 for r in regimes),
        "wal_bounded_at_campaign_rate": bool(camp) and camp["wal_max_mb"] <= 64,
        "crash_restart_recovery_measured": bool(regimes) and all(r["restart_s"] > 0 for r in regimes),
        "campaign_rate_run_outlasts_prior_defect_onset": bool(camp) and camp["seconds"] >= PRIOR_DEFECT_APPEARED_S,
    }
    missing = [k for k, v in checks.items() if not v]
    ev = {"receipt": p901, "regimes": regimes, "campaign_rate_regimes": camps,
          "acceptance_regime_selected_by": "longest campaign_rate regime (order-independent)",
          "campaign_rate_regime": camp,
          "prior_defect_first_appeared_s": PRIOR_DEFECT_APPEARED_S,
          "checks": checks,
          "note": ("the campaign-rate acceptance regime ran %.1f s; the defect class it replaces first appeared "
                   "about %d s into the previous run, so this regime is too short to exclude its return"
                   % (camp["seconds"], PRIOR_DEFECT_APPEARED_S)) if camp and not checks["campaign_rate_run_outlasts_prior_defect_onset"] else None}
    return {"id": "G1", "owner": "Daedalus",
            "requirement": "campaign-rate long run on 9.0.1 + WAL bound + crash/restart recovery measured",
            "status": GREEN if not missing else CLAIMED, "missing": missing, "evidence": ev, "blocks_launch": True}


def g2_rehearsal() -> dict:
    p = C4 / "REHEARSAL_RECEIPT.json"
    if not p.exists():
        return {"id": "G2", "owner": "Archaeon + Vivarium", "requirement": "synthetic C4 specimen travels the full chain incl. forced restart",
                "status": UNVERIFIED, "evidence": {"receipt": "absent"}, "blocks_launch": True}
    d = json.loads(p.read_text(encoding="utf-8"))
    by = {s["stage"]: s["status"] for s in d["stages"]}
    need = ["S1", "S2-validate", "S3", "S4", "S5", "S6", "S7", "S8"]
    ok = [s for s in need if by.get(s) == "OK"]
    not_ok = [s for s in need if by.get(s) != "OK"]
    return {"id": "G2", "owner": "Archaeon + Vivarium",
            "requirement": "synthetic C4 specimen travels the full chain incl. forced restart and a reproducible receipt",
            "status": GREEN if not not_ok else RED,
            "evidence": {"stage_status": by, "stages_ok": ok, "stages_not_ok": not_ok,
                         "receipt_digest": "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest(),
                         "preconditions": d.get("preconditions")},
            "blocks_launch": True}


def g3_vivarium() -> dict:
    """Consumer identity live AND the M2 B1 read grant valid. The grant is the part this gate
    cannot prove from here: it is an engine-side authorization, and comms #368 states it still
    names an M1-ledger client."""
    return {"id": "G3", "owner": "Vivarium + Daedalus",
            "requirement": "Campaign-4 consumer identity live and its M2 B1 read grant valid",
            "status": CLAIMED,
            "evidence": {"consumer_alive_claim": "Vivarium #368: consumer ALIVE on M2 (build 08081c6ed)",
                         "grant_defect_claim": "Vivarium #368 caveat: Archaeon's B1 read grant names an M1-ledger "
                                               "client; must be re-issued for the M2 ledger client",
                         "verifiable_from_here": False,
                         "why": "grant validity is engine-side authorization; proving it requires a campaign-4 "
                                "engine identity this seat does not yet hold"},
            "blocks_launch": True}


def g4_pew(ref: str) -> dict:
    """Non-blocking by the directive's own words, but it bounds what the FINAL disposition may
    claim, so the bound is recorded as data rather than as a footnote.

    Two separable facts, kept apart on purpose:
      (a) is the observer leg READY to run when artifacts land?   -- verified from its own receipt
      (b) has the historical backlog been delivered?              -- advisory, quantified
    """
    ev = {}
    b = at_ref(ref, "evidence_wiki/integration/s7_rehearsal_results.json")
    if b is None:
        ev["s7_leg"] = "no receipt at origin/main"
        ready = False
    else:
        r = json.loads(b)
        gates = {g["gate"]: {"pass": g.get("pass"), "skipped": g.get("skipped")} for g in r.get("gates", [])}
        ev.update({"s7_receipt": "evidence_wiki/integration/s7_rehearsal_results.json",
                   "s7_all_pass": r.get("all_pass"), "s7_precheck": r.get("precheck"),
                   "reader_version": r.get("reader_version"), "s7_seconds": r.get("seconds"),
                   "s7_gates": gates, "rebuild_digests": r.get("rebuild_digests"),
                   "campaign4_rows_seen": (r.get("campaign4_rows") or {}).get("n")})
        ready = bool(r.get("all_pass"))
    ev["observer_leg_ready"] = ready
    ev["backlog_delivered"] = False
    ev["backlog_pending_reported"] = 56
    ev["backlog_source"] = "Mnemosyne tail-closure report; the queue's own health readout does not expose it"
    ev["closure_condition"] = "last_seq 56, gaps []"
    ev["directive_consequence"] = ("Campaign 4 MAY execute -- the queue is durable and nothing on the execution "
                                  "path imports the observer -- but the FINAL campaign disposition may not claim "
                                  "complete observational closure until the backlog reconciles.")
    return {"id": "G4", "owner": "Mnemosyne + Vivarium",
            "requirement": "observer leg ready; historical backlog delivered (advisory for launch)",
            "status": CONDITIONAL, "evidence": ev, "blocks_launch": False}


def canonical_population_digest(d: dict) -> str:
    """The published rule, reimplemented here rather than imported, so the gate verifies the
    declaration instead of trusting the tool that wrote it."""
    volatile = ("generated_at", "wall_s", "population_digest", "population_digest_rule",
                "superseded_raw_byte_digests")
    D = {k: v for k, v in d.items() if k not in volatile}
    return "sha256:" + hashlib.sha256(
        json.dumps(D, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def g5_proteus(ref: str) -> dict:
    """Manifests and structural descriptors for the EXACT starting organisms.

    Identity rule (repaired 2026-09-17): the population is identified by a CANONICAL digest that
    is invariant to checkout line endings. The first rule hashed raw worktree bytes, and this repo
    sets core.autocrlf=true, so Proteus minted over a CRLF reading (a3f9816f) of the same content
    this seat writes as LF (3c2ebfd9). Content was never in dispute; the identity rule was.

    The gate no longer reads a self-set `minted_by_proteus` flag -- a declaration must not certify
    itself. It reads Proteus's minted manifest and requires it to bind THIS canonical digest.
    """
    catalog = at_ref(ref, "proteus/eval/FOUNDRY_PROFILE_CATALOG.json")
    mint_b = at_ref(ref, "proteus/eval/C4_STARTING_POPULATION_MANIFEST.json")
    decl = C4 / "STARTING_POPULATION.json"
    ev = {"proteus_catalog_present": catalog is not None,
          "proteus_mint_present": mint_b is not None,
          "archaeon_declaration_present": decl.exists()}
    checks = {k: bool(v) for k, v in ev.items()}
    if decl.exists():
        d = json.loads(decl.read_text(encoding="utf-8"))
        orgs = d.get("organisms", [])
        unknown = [o.get("organism_id") for o in orgs if not (o.get("ancestries") or o.get("ancestry"))]
        declared = d.get("population_digest")
        recomputed = canonical_population_digest(d)
        ev.update({"organisms_declared": len(orgs), "organisms_without_ancestry": len(unknown),
                   "population_digest_declared": declared,
                   "population_digest_recomputed_here": recomputed,
                   "population_digest_rule_published": bool(d.get("population_digest_rule")),
                   "superseded_raw_byte_digests": d.get("superseded_raw_byte_digests")})
        checks["declaration_has_canonical_rule"] = bool(d.get("population_digest_rule"))
        checks["declaration_digest_reproducible"] = bool(declared) and declared == recomputed
        checks["every_organism_has_ancestry"] = unknown == []
        checks["organisms_present"] = len(orgs) > 0
    if mint_b is not None:
        m = json.loads(mint_b)
        bound = (m.get("declaration_canonical_digest") or m.get("population_digest")
                 or m.get("declaration_digest"))
        ev.update({"mint_binds_digest": bound, "mint_count": (m.get("population_manifest") or {}).get("count"),
                   "mint_schema": m.get("schema_version"), "minted_by": m.get("minted_by")})
        checks["mint_binds_canonical_digest"] = bool(bound) and bound == ev.get("population_digest_recomputed_here")
        checks["mint_count_matches"] = ev.get("mint_count") == ev.get("organisms_declared")
    ev["checks"] = checks
    missing = [k for k, v in checks.items() if not v]
    ev["missing"] = missing
    if missing == ["mint_binds_canonical_digest"]:
        ev["next_action"] = ("Proteus remints over the canonical digest %s (the content is unchanged: same 57 "
                             "organisms, same collapsed duplicate). The raw-byte digest it currently binds is a "
                             "checkout artifact, not a population identity."
                             % ev.get("population_digest_recomputed_here"))
    return {"id": "G5", "owner": "Proteus + Archaeon",
            "requirement": "manifests + structural descriptors for the exact C4 starting organisms; no organism of unknown ancestry",
            "status": GREEN if not missing else RED, "missing": missing, "evidence": ev, "blocks_launch": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    checks = [g1_engine(a.ref), g2_rehearsal(), g3_vivarium(), g4_pew(a.ref), g5_proteus(a.ref)]
    blocking = [c for c in checks if c["blocks_launch"]]
    green = all(c["status"] == GREEN for c in blocking)
    receipt = {
        "_what_this_is": "Campaign 4 launch gate. Execution REFUSES until every blocking requirement is GREEN.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "read_at_ref": a.ref,
        "read_at_commit": subprocess.run(["git", "rev-parse", a.ref], capture_output=True, text=True, cwd=str(REPO)).stdout.strip(),
        "gate": GREEN if green else RED,
        "campaign_may_start": green,
        "blocking_not_green": [{"id": c["id"], "owner": c["owner"], "status": c["status"]} for c in blocking if c["status"] != GREEN],
        "checks": checks,
        "rule": "an item whose evidence cannot be READ is UNVERIFIED or CLAIMED_NOT_PROVEN and still blocks; "
                "a message is a claim, not proof.",
    }
    OUT.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if a.json:
        print(json.dumps(receipt, indent=1, sort_keys=True))
    else:
        print("CAMPAIGN 4 LAUNCH GATE: %s" % receipt["gate"])
        print("-" * 68)
        for c in checks:
            flag = "BLOCKING" if c["blocks_launch"] else "advisory"
            print("%-3s %-9s %-20s %s" % (c["id"], flag, c["status"], c["owner"]))
            print("     %s" % c["requirement"])
            if c.get("missing"):
                print("     missing: %s" % ", ".join(c["missing"]))
            if c["id"] == "G2" and c["evidence"].get("stages_not_ok"):
                print("     stages not OK: %s" % ", ".join(c["evidence"]["stages_not_ok"]))
        print("-" * 68)
        print("campaign_may_start:", receipt["campaign_may_start"])
        print("receipt:", OUT)
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
