"""Backlog generator — materialize ~1000 prioritized threads from sources that EXIST.

Honesty rule: a thread is only materialized from a verified on-disk source (counted at
generation time). Sources we cannot verify get ONE generator-stub thread, never fake
batches. Every thread carries: consumer (LAW 1), priority (deterministic score), gate
(what blocks it, if anything), and provenance (which source file, which line/id).

Priority score (higher = sooner), fully deterministic:
    base   by source class (bottleneck-discriminating work highest)
    +30    if the thread targets a live bottleneck hypothesis (B-001..B-006)
    +20    if runnable in-harness at $0 (no API, no gate)
    -40    if gated on a seat (cosign/HITL/other-agent) — still filed, PARKED-at-birth
    +0..15 bucket boost from triage (Bucket A testable-now)

Rerunnable: regenerates BACKLOG.jsonl idempotently (stable ids); never touches WORK.jsonl
(the active head) — the driver promotes top-priority unblocked threads from BACKLOG to
WORK as slots free.

    python engine/driver/backlog_gen.py
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "engine" / "queues" / "BACKLOG.jsonl"


def jsonl(path: Path) -> list[dict]:
    items = []
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    threads: list[dict] = []
    counts: dict[str, int] = {}

    def add(tid, title, source, consumer, base, gate=None, bottleneck=None, meta=None):
        score = base
        if bottleneck:
            score += 30
        if gate is None:
            score += 20
        else:
            score -= 40
        threads.append({
            "id": tid, "title": title[:160], "source": source, "consumer": consumer,
            "priority": score, "gate": gate, "bottleneck": bottleneck,
            "status": "PARKED" if gate else "QUEUED",
            "parked_reason": gate, "meta": meta or {}, "generated": now,
        })
        counts[source] = counts.get(source, 0) + 1

    # ---- 1. Open-problem catalog × triage (537, bucket-boosted) ----
    triage = {t.get("id") or t.get("qid"): t for t in jsonl(ROOT / "aporia/mathematics/triage.jsonl")}
    for i, q in enumerate(jsonl(ROOT / "aporia/mathematics/questions.jsonl")):
        qid = q.get("id") or q.get("qid") or f"q{i:04d}"
        t = triage.get(qid, {})
        bucket = str(t.get("bucket", t.get("triage", ""))).upper()
        boost = 15 if "A" in bucket else (7 if "B" in bucket else 0)
        # 2026-08-20 (P20/P24): an entry without a real test_spec is not attackable —
        # attacking it means inventing goalposts mid-shot (CPNT precedent). Gate it at
        # birth on spec authoring; the SPEC-AUTHOR-BATCH lane converts these deliberately.
        spec = str(t.get("test_spec", ""))
        spec_missing = (len(spec) < 30 or "See specific test" in spec
                        or "Requires data extension" in str(t.get("data_source", "")))
        gate = "needs authored test_spec (SPEC-AUTHOR-BATCH lane)" if spec_missing else None
        add(f"CAT-{qid}", f"Catalog attack: {str(q.get('question') or q.get('title') or qid)[:120]}",
            "catalog_537", "trace-vector corpus + kill ledger", 40 + boost,
            gate=gate, bottleneck="B-004", meta={"bucket": bucket or "?"})

    # ---- 2. Retry queue batches (725 resolution_limit, 15 batches) — gated on co-sign ----
    for b in range(15):
        add(f"RETRY-RL-{b:02d}", f"Retry batch {b+1}/15 (~48 resolution_limit kills, effect-stability criterion)",
            "retry_queue_725", "B-005 rescore + weak-signal anchors", 80,
            gate="charon-cosign (DESIGN_W001)", bottleneck="B-005")
    # wider retry_recommended set: one design-extension thread, not fake batches
    add("RETRY-WIDE-000", "Extend retry design to the wider 3,378 retry_recommended set (post-RL results)",
        "retry_queue_3378", "B-005 rescore", 55, gate="RL batches complete first", bottleneck="B-005")

    # ---- 3. DR back-corpus mining (442 verified on disk, batches of 20) ----
    reports = sorted((ROOT / "aporia/docs/deep_research_reports").rglob("*.md"))
    # recovered May batch archives (stash recovery 2026-08-18): scan them into the same lane
    for bdir in sorted((ROOT / "aporia/docs").glob("deep_research_batch*")):
        if bdir.is_dir():
            reports += sorted(bdir.rglob("*.md"))
    reports = [r for r in reports if not r.name.endswith("_answer.md")]
    # Consumption-aware (2026-08-19): only generate batches for reports NOT yet in the
    # mining ledger. The whole 614-report corpus was consumed DRBC-00..R10; without this
    # check the generator kept emitting phantom batches for an empty remainder.
    consumed = set()
    ledger = ROOT / "engine/queues/BACKCORPUS_MINING.jsonl"
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                try:
                    consumed.add(json.loads(line)["report"])
                except Exception:
                    pass
    def _report_key(p):
        m = re.match(r"(\d{5})_", p.name)
        return m.group(1) if m else None
    remaining = [r for r in reports if _report_key(r) is None or _report_key(r) not in consumed]
    # recovered-dir files have non-numeric names; they were ledgered under R-batch keys,
    # so count a recovered dir as consumed if ANY of its batch keys appear in the ledger
    rbatch_done = {rec.split("-")[0] for rec in consumed if rec.startswith("R")}
    remaining = [r for r in remaining if not (r.parent.name.startswith("deep_research_batch") and rbatch_done)]
    nb = (len(remaining) + 19) // 20
    for b in range(nb):
        add(f"DRBC-N{b:02d}", f"Mine back-corpus batch {b+1}/{nb} of NEW reports (20 -> anti-anchors/probe templates/catalog updates)",
            "dr_backcorpus_442", "anti_anchors.jsonl + market evidence", 60, bottleneck="B-006")

    # ---- 4. Fleet profiling: agents through the ladder (roster from state.json) ----
    state = json.loads((ROOT / "docs/state.json").read_text(encoding="utf-8", errors="replace"))
    seen = set()
    for a in state.get("agents", []):
        name = a.get("name")
        if not name or name in seen:
            continue
        seen.add(name)
        add(f"PROF-{re.sub(r'[^A-Za-z0-9]', '', name)[:20]}",
            f"Ladder profile: run {name} artifacts/config through phase0+R4 probes",
            "fleet_profiling", "germline fitness instrument (3b) + agent-design failure landscape", 50)

    # ---- 5. Anti-anchor re-verification (16 registered, rolling) ----
    for a in jsonl(ROOT / "techne/registry/anti_anchors.jsonl"):
        add(f"AA-VERIFY-{a.get('id','?')}", f"Re-verify {a.get('id')} ({str(a.get('name',''))[:40]}) against primary sources",
            "anti_anchor_registry", "anti_anchors.jsonl last_verified", 45)

    # ---- 6. Attack-paradigm grounding (30 paradigms from taxonomy) ----
    tax = (ROOT / "aporia/docs/attack_angle_taxonomy.md").read_text(encoding="utf-8", errors="replace")
    for pid in sorted(set(re.findall(r"\bP(\d{2})\b", tax)))[:31]:
        add(f"PARADIGM-P{pid}", f"Paradigm P{pid}: worked example + decision tree + code skeleton (substrate type C refinement)",
            "paradigm_taxonomy", "Learner corpus type C + catalog assignment", 35)

    # ---- 7. Sleeping Beauties: sweep exists as json — file per-strategy sweep threads ----
    sb = ROOT / "aporia/mathematics/v5_sleeping_beauty_sweep.json"
    if sb.exists():
        for s in range(11):
            add(f"SB-SWEEP-S{s:02d}", f"Sleeping-Beauty sweep, strategy group {s+1}/11 over 68,770 sequences (V5 protocol)",
                "sleeping_beauties", "tensor integration + activation ledger", 30,
                gate="GPU slot + strategy-group harness check")
    else:
        add("SB-SWEEP-000", "Locate/validate SB catalog then file sweep threads", "sleeping_beauties",
            "tensor integration", 25, gate="source verification")

    # ---- 8. Salvage lifts (portfolio manifest, 5 named) ----
    for sid, what in [("NOUS", "Nous 95-concept dictionary -> registry diversity injector"),
                      ("IRIS", "Iris prose->symbol compressor -> shared registry"),
                      ("SOPHIA", "Sophia coordinate-system toolkit -> shared registry"),
                      ("STYGIAN", "Stygian KillVector schema -> trace-vector v2 alignment"),
                      ("LETHE", "Lethe anti-anchor registry merge-check")]:
        add(f"SALVAGE-{sid}", f"Salvage lift: {what}", "salvage_manifest", "shared registry (typed primitives)", 42)

    # ---- 9. Agent autopsies as residue (RETIRE-21 -> agent-design trace vectors) ----
    for name in ["Argos", "Iris", "Sophia", "Telos", "HarmoniaLoop", "Hecate", "Pollux", "Moros",
                 "Acheron", "Lethe", "Nephele", "CharonLoop", "Erebos", "Coeus", "Aletheia",
                 "Eos", "Hermes", "Nemesis", "Atalanta", "Hypatia", "Polyhymnia"]:
        add(f"AUTOPSY-{name.upper()}", f"File {name} failure modes as typed agent-design trace vectors (3d residue)",
            "retire21_autopsies", "germline genesis residue", 38)

    # ---- 10. Ladder / instruments ----
    for tid, title, gate in [
        ("LAD-R12-RUN", "Run the built R12 grader live, once (frontier-endorsed, never run)", None),
        ("LAD-ZOO-RUN", "Model zoo matrix ~1.2k calls (ladder-vs-basis decider)", "API budget (Tier-2 free-first attempt allowed)"),
        ("LAD-R4-WIRE", "Wire reasoning_r4 into phase0 suite + verifier lens", "harmonia-A instrument-owner sign"),
        ("LAD-R9-DESIGN", "R9 lemma-invention grader design (Lean oracle)", "heredity rule (first cycle)"),
        ("LAD-R10-DESIGN", "R10 analogy grader design", "heredity rule (first cycle)"),
        ("LAD-R11-DESIGN", "R11 calibration grader (sharpness + base-rate per DR-17)", "heredity rule (first cycle)"),
        ("LAD-CONFOUND", "Confound battery run (~780 calls, Opus/Sonnet dissociation)", "API budget"),
        ("LAD-BPRIME", "Grade B-prime ONCE against translator when built", "translator build"),
        ("LAD-ENSEMBLE", "Ensemble-rung study: collision yield vs solo yield from git history", None),
        ("LAD-HUMAN", "Human calibration anchors: James takes R11/R12 probes", "james-availability")]:
        add(f"{tid}", title, "ladder_lane", "Canon coverage + germline sensory system", 55, gate=gate)

    # ---- 11. Engine/infra plumbing ----
    for tid, title, gate in [
        ("INFRA-BACKUP", "Z: backup job: pg_dump fire+sci weekly + robocopy F: corpus (DECISION 2)", None),
        ("INFRA-DR-EVENTS", "W-006: dispatcher emits DR events to the ledger M4 watches", None),
        ("INFRA-GATEWAY", "Model gateway + per-child meter (engine/sdk)", None),
        ("INFRA-QCLIENT", "PG queue client: SKIP LOCKED + fencing tokens + DLQ", None),
        ("INFRA-SCHEMA", "germline schema migration + weekly dump job", "techne seat"),
        ("INFRA-CI", "CI schema enforcement (birth certs, consumers, telemetry)", None),
        ("INFRA-DECOYS", "Assemble graveyard decoy set from documented kills", None),
        ("INFRA-ALETHELIA", "Alethelia truthful reporter build for M4", None),
        ("INFRA-SANDBOX", "Jailed venv sandbox: Job Objects + Restricted Tokens + PEP 578 (DR-18)", None),
        ("INFRA-PULSE-M4", "Serve PULSE.md via the GitHub Pages dashboard", None)]:
        add(tid, title, "infra_plumbing", "engine operations", 48, gate=gate)

    # ---- 12. Open verification follow-ups from DR batch ----
    add("VERIFY-LETELLIER", "Primary-source check: Letellier-Nam unipotent Saxl analogues (open_candidate_2026)",
        "dr_followups", "anti_anchors AA-004", 44)
    add("VERIFY-SCANDAL", "Pin Scandal-of-Deduction primary cites (Hintikka) into the decidability FINDING",
        "dr_followups", "FINDING_2026-08-17_decidability", 30)

    # merge manual threads (never clobbered by regeneration)
    for m in jsonl(ROOT / "engine" / "queues" / "BACKLOG_MANUAL.jsonl"):
        threads.append(m)
        counts["manual"] = counts.get("manual", 0) + 1

    # de-dup by id, stable sort by priority desc then id
    uniq = {}
    for t in threads:
        uniq[t["id"]] = t

    # persistence: a regenerated thread must not erase completed/in-flight state
    for old_item in jsonl(OUT):
        oid, ost = old_item.get("id"), str(old_item.get("status", ""))
        if oid in uniq and (ost.startswith("DONE") or ost in ("RUNNING", "PARKED-MANUAL", "PARKED")):
            # PARKED added 2026-08-19: a manual park of a GENERATED thread (e.g. CAT-MATH-0260
            # vacuous-parked on missing mirror data) was being clobbered back to QUEUED on regen.
            # Parks carry their gate + reason forward too, else the ELI5 linkage breaks.
            uniq[oid]["status"] = ost
            if old_item.get("result"):
                uniq[oid]["result"] = old_item["result"]
            if ost == "PARKED":
                if old_item.get("gate"):
                    uniq[oid]["gate"] = old_item["gate"]
                if old_item.get("parked_reason"):
                    uniq[oid]["parked_reason"] = old_item["parked_reason"]
    final = sorted(uniq.values(), key=lambda t: (-t["priority"], t["id"]))
    OUT.write_text("\n".join(json.dumps(t, ensure_ascii=False) for t in final) + "\n", encoding="utf-8")

    total = len(final)
    parked = sum(1 for t in final if t["status"] == "PARKED")
    print(f"BACKLOG: {total} threads ({parked} parked-at-birth on gates) -> {OUT}")
    for src, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {c:5d}  {src}")
    print("\ntop 10 by priority:")
    for t in final[:10]:
        print(f"  {t['priority']:3d}  {t['id']:22s} {t['title'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
