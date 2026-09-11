"""The gate. Deterministic predicates G1-G7 over an emitted ladder plus its
frozen packet. Preregistration s5.

No model adjudicates here. Every verdict below is a predicate over bytes.

Written and committed BEFORE any ladder for this season exists, so the gate
cannot be tuned to the output it will judge.

Usage:
    python roles/Hypatia/science/season1/verify_ladder.py <ladder.jsonl> <packet.json>
    python roles/Hypatia/science/season1/verify_ladder.py --selftest
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REQUIRED_FIELDS = ("step", "kind", "claim", "reasoning_class",
                   "provenance", "depends_on", "certainty")
KINDS = ("evidence", "inference", "gap", "terminal")
CLASSES = ("R1", "R2", "R3", "R4", "R5")
CERTAINTIES = ("asserted", "uncertain")
SPECIFIC_DENSITY_FLOOR = 0.50      # preregistration s5.1

# ---------------------------------------------------------------------------
# G5 specific extraction. Fixed set, stated in the preregistration.
# Detects INVENTED SPECIFICS, not semantic entailment.
# ---------------------------------------------------------------------------
RE_NUMBER = re.compile(r"\d+(?:\.\d+)?(?::\d+)?%?")
RE_QUOTED = re.compile(r'"([^"]{2,})"')
RE_PATH = re.compile(r"[A-Za-z0-9_./-]+\.(?:py|json|jsonl|md|bat|txt)(?::\d+)?")
RE_CAPS = re.compile(r"\b[A-Z][A-Z0-9_-]{3,}\b")
RE_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")


def extract_specifics(claim: str):
    out = []
    for rx in (RE_PATH, RE_NUMBER, RE_CAPS, RE_SNAKE):
        out.extend(m.group(0) for m in rx.finditer(claim))
    out.extend(m.group(1) for m in RE_QUOTED.finditer(claim))
    seen, uniq = set(), []
    for s in out:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).lower()


def verify(ladder_path, packet_path):
    packet = json.loads(pathlib.Path(packet_path).read_text(encoding="utf-8"))
    ev = {u["id"]: u["text"] for u in packet["evidence"]}
    req_tokens = (packet.get("terminal_ruling", {}).get("required_tokens")
                  or packet.get("required_tokens") or [])

    raw = pathlib.Path(ladder_path).read_text(encoding="utf-8")
    lines = [l for l in raw.splitlines() if l.strip()]

    # ---- G1 parseability -------------------------------------------------
    steps, parse_fail = [], []
    for i, l in enumerate(lines, 1):
        try:
            steps.append(json.loads(l))
        except Exception as e:
            parse_fail.append({"line": i, "error": str(e)[:120],
                               "text": l[:160]})
    g1 = {"pass": not parse_fail, "lines": len(lines),
          "parsed": len(steps), "failures": parse_fail}

    # ---- G2 schema -------------------------------------------------------
    schema_err = []
    for s in steps:
        sid = s.get("step")
        for f in REQUIRED_FIELDS:
            if f not in s:
                schema_err.append({"step": sid, "why": "missing field %s" % f})
        if s.get("kind") not in KINDS:
            schema_err.append({"step": sid, "why": "bad kind %r" % s.get("kind")})
        if s.get("reasoning_class") not in CLASSES:
            schema_err.append({"step": sid,
                               "why": "bad reasoning_class %r" % s.get("reasoning_class")})
        if s.get("certainty") not in CERTAINTIES:
            schema_err.append({"step": sid,
                               "why": "bad certainty %r" % s.get("certainty")})
        if not isinstance(s.get("provenance"), list) or \
           not isinstance(s.get("depends_on"), list):
            schema_err.append({"step": sid, "why": "provenance/depends_on not lists"})
    nums = [s.get("step") for s in steps]
    if nums != list(range(1, len(steps) + 1)):
        schema_err.append({"step": None, "why": "step numbers not 1..n contiguous"})
    g2 = {"pass": not schema_err, "errors": schema_err}

    by_id = {s.get("step"): s for s in steps}

    # ---- G3 provenance completeness --------------------------------------
    prov_err, dangling = [], []
    for s in steps:
        k = s.get("kind")
        prov = s.get("provenance") or []
        for p in prov:
            if p not in ev:
                dangling.append({"step": s.get("step"), "id": p})
        if k in ("evidence", "inference", "terminal") and not prov:
            prov_err.append({"step": s.get("step"),
                             "why": "kind %s with empty provenance" % k})
    g3 = {"pass": not prov_err and not dangling,
          "errors": prov_err, "dangling": dangling,
          "percent": round(100.0 * (len(steps) - len(prov_err) - len(dangling))
                           / len(steps), 1) if steps else 0.0}

    # ---- G4 acyclic, strictly-earlier order ------------------------------
    order_err = []
    for s in steps:
        for d in (s.get("depends_on") or []):
            if not isinstance(d, int) or d >= (s.get("step") or 0) or d < 1:
                order_err.append({"step": s.get("step"), "bad_dep": d})
            elif d not in by_id:
                order_err.append({"step": s.get("step"), "bad_dep": d})
    g4 = {"pass": not order_err, "errors": order_err}

    # ---- G5 grounded specifics -------------------------------------------
    req_lower = {t.lower() for t in req_tokens}

    def ruling_name_exempt(spec):
        """AMENDMENT A-1 (preregistration, 2026-09-11, before any season
        ladder existed). s4 defines R5 as introducing a name NOT PRESENT in
        the evidence, and s3.4 keeps the ruling out of the evidence, so the
        class name in the TERMINAL step can never be grounded. Exempt it --
        and only it: the specific's alphabetic tokens must be a subset of the
        packet's required_tokens. An invented number, path or identifier in a
        terminal claim is still UNSUPPORTED."""
        toks = {x for x in re.split(r"[^A-Za-z]+", spec.lower()) if x}
        return bool(toks) and toks.issubset(req_lower)

    unsupported, with_specifics = [], 0
    for s in steps:
        claim = s.get("claim") or ""
        specs = extract_specifics(claim)
        if specs:
            with_specifics += 1
        cited = " ".join(ev.get(p, "") for p in (s.get("provenance") or []))
        cited_n = norm(cited)
        missing = [sp for sp in specs if norm(sp) not in cited_n]
        if s.get("kind") == "terminal":
            missing = [sp for sp in missing if not ruling_name_exempt(sp)]
        if missing:
            unsupported.append({"step": s.get("step"), "missing": missing,
                                "claim": claim[:140]})
    density = (with_specifics / len(steps)) if steps else 0.0
    rate = (len(unsupported) / len(steps)) if steps else 0.0
    g5_indeterminate = density < SPECIFIC_DENSITY_FLOOR
    g5 = {"pass": (not unsupported) and not g5_indeterminate,
          "indeterminate": g5_indeterminate,
          "unsupported_step_rate": round(rate, 4),
          "specific_density": round(density, 4),
          "steps_with_specifics": with_specifics,
          "unsupported": unsupported}

    # ---- G7 R5 discipline ------------------------------------------------
    r5_err = [{"step": s.get("step")} for s in steps
              if s.get("reasoning_class") == "R5" and s.get("kind") != "terminal"]
    g7 = {"pass": not r5_err, "errors": r5_err}

    # ---- G6 terminal reconstruction --------------------------------------
    admissible_ids = set()
    bad = {e["step"] for e in unsupported} | {e["step"] for e in r5_err}
    for s in steps:
        if s.get("step") not in bad:
            admissible_ids.add(s.get("step"))

    terms = [s for s in steps if s.get("kind") == "terminal"]
    g6 = {"pass": False, "clause": None, "terminal_steps": len(terms)}
    if len(terms) != 1:
        g6["clause"] = "(a) expected exactly one terminal step, found %d" % len(terms)
    else:
        t = terms[0]
        claim_n = norm(t.get("claim") or "")
        missing_tok = [tok for tok in req_tokens if tok.lower() not in claim_n]
        if missing_tok:
            g6["clause"] = "(b) terminal claim missing required tokens %s" % missing_tok
        else:
            # transitive closure
            seen, stack = set(), list(t.get("depends_on") or [])
            while stack:
                d = stack.pop()
                if d in seen or d not in by_id:
                    continue
                seen.add(d)
                stack.extend(by_id[d].get("depends_on") or [])
            kinds = {by_id[d].get("kind") for d in seen}
            if "evidence" not in kinds:
                g6["clause"] = "(c) terminal does not transitively depend on any evidence step"
            elif "gap" in kinds:
                g6["clause"] = "(d) terminal transitively depends on a gap step"
            elif not seen.issubset(admissible_ids) or t.get("step") not in admissible_ids:
                g6["clause"] = "(e) terminal rests on inadmissible steps %s" % sorted(
                    (seen | {t.get("step")}) - admissible_ids)
            else:
                g6["pass"] = True
        g6["support_size"] = len(seen) if len(terms) == 1 and not missing_tok else 0

    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "G7": g7}
    overall = all(g["pass"] for g in gates.values())
    return {
        "ladder": str(ladder_path).replace("\\", "/").split("season1/")[-1],
        "packet": packet["packet_id"],
        "step_count": len(steps),
        "gap_count": sum(1 for s in steps if s.get("kind") == "gap"),
        "class_histogram": {c: sum(1 for s in steps
                                   if s.get("reasoning_class") == c) for c in CLASSES},
        "gates": gates,
        "all_gates_pass": overall,
    }


def make_payload_reader_ladder(packet_path, out_path):
    """CHEAT-2: the degenerate decomposer, PayloadReader shape
    (roles/Nemesis/science/cheatlib.py). Copies the ruling into one step and
    cites everything. Performs no reasoning. Built to be accepted.
    The gate MUST reject it; if it does not, every PASS above it is void."""
    p = json.loads(pathlib.Path(packet_path).read_text(encoding="utf-8"))
    ruling = (p.get("terminal_ruling", {}).get("text")
              or p.get("supplied_conclusion", ""))
    step = {"step": 1, "kind": "terminal",
            "claim": ruling,
            "reasoning_class": "R5",
            "provenance": [u["id"] for u in p["evidence"]],
            "depends_on": [], "certainty": "asserted"}
    pathlib.Path(out_path).write_text(json.dumps(step) + "\n", encoding="utf-8")
    return out_path


def selftest():
    """Negative, positive and cheat controls for the GATE itself."""
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp())
    pkt = {"packet_id": "PKT-SELFTEST", "case_id": "selftest",
           "terminal_ruling": {"text": "WIDGET-ROT", "required_tokens": ["widget", "rot"]},
           "evidence": [
               {"id": "EV1", "text": "the widget ran 42 times and produced 0 rows"},
               {"id": "EV2", "text": "every run recorded status widget_rot in the log"},
           ]}
    pp = tmp / "pkt.json"
    pp.write_text(json.dumps(pkt), encoding="utf-8")

    results = {}

    # POSITIVE: a well-formed, fully grounded ladder must PASS.
    good = [
        {"step": 1, "kind": "evidence", "claim": "the widget ran 42 times and produced 0 rows",
         "reasoning_class": "R1", "provenance": ["EV1"], "depends_on": [], "certainty": "asserted"},
        {"step": 2, "kind": "evidence", "claim": "every run recorded status widget_rot",
         "reasoning_class": "R1", "provenance": ["EV2"], "depends_on": [], "certainty": "asserted"},
        {"step": 3, "kind": "terminal", "claim": "the case is WIDGET-ROT",
         "reasoning_class": "R5", "provenance": ["EV1", "EV2"], "depends_on": [1, 2],
         "certainty": "asserted"},
    ]
    gp = tmp / "good.jsonl"
    gp.write_text("\n".join(json.dumps(s) for s in good) + "\n", encoding="utf-8")
    r = verify(gp, pp)
    results["positive_accepts_valid"] = r["all_gates_pass"]

    # NEGATIVE: an invented specific must be caught by G5.
    bad = [dict(good[0]), dict(good[1]), dict(good[2])]
    bad[0] = dict(bad[0]); bad[0]["claim"] = "the widget ran 99 times and produced 0 rows"
    bp = tmp / "bad.jsonl"
    bp.write_text("\n".join(json.dumps(s) for s in bad) + "\n", encoding="utf-8")
    r = verify(bp, pp)
    results["negative_catches_invented_number"] = (
        not r["all_gates_pass"] and not r["gates"]["G5"]["pass"])

    # PARSE: a malformed line must fail G1, not be cleaned up.
    pf = tmp / "parse.jsonl"
    pf.write_text(json.dumps(good[0]) + "\n" + '{"step": 2, "depends_on": [cite: 1]}\n',
                  encoding="utf-8")
    r = verify(pf, pp)
    results["parse_failure_is_failure"] = not r["gates"]["G1"]["pass"]

    # CHEAT: the payload reader must be REJECTED.
    cp = tmp / "cheat.jsonl"
    make_payload_reader_ladder(pp, cp)
    r = verify(cp, pp)
    results["cheat_rejects_payload_reader"] = not r["all_gates_pass"]
    results["cheat_rejection_clause"] = r["gates"]["G6"]["clause"]

    # GAP: a terminal resting on a gap must be rejected (uncertainty preserved).
    gapl = [
        {"step": 1, "kind": "gap", "claim": "the packet does not say whether rows were produced",
         "reasoning_class": "R1", "provenance": ["EV1"], "depends_on": [], "certainty": "uncertain"},
        {"step": 2, "kind": "terminal", "claim": "the case is WIDGET-ROT",
         "reasoning_class": "R5", "provenance": ["EV1"], "depends_on": [1], "certainty": "asserted"},
    ]
    xp = tmp / "gap.jsonl"
    xp.write_text("\n".join(json.dumps(s) for s in gapl) + "\n", encoding="utf-8")
    r = verify(xp, pp)
    results["gap_blocks_terminal"] = not r["gates"]["G6"]["pass"]

    print("GATE SELF-CONTROLS")
    for k, v in results.items():
        print("  %-36s %s" % (k, v))
    ok = all(v for k, v in results.items() if isinstance(v, bool))
    print("\n%s" % ("all gate self-controls pass" if ok
                    else "GATE SELF-CONTROL FAILURE -- the gate is not trustworthy"))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    print(json.dumps(verify(sys.argv[1], sys.argv[2]), indent=2))
