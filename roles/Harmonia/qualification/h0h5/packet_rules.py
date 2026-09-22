"""Packet governance rules for the Mechanism Archaeology lane.  PR-1.0.0  2026-09-18.

Harmonia[m2-ca1148a0]. Adopts the three rules of the operator's "refinery"
directive of 2026-09-18, section 4 (verbatim at roles/Nyx/prompts/
2026-09-18_refinery_directive/OPERATOR_DIRECTIVE_verbatim.md), each as a
refusal that fires on the particles-002 shape and stays silent on a clean
packet (tests/test_packet_rules.py). Every Harmonia ruler that adjudicates a
Nyx prediction packet calls these three before it returns a verdict.

    RULE 1  PLAN AMENDMENT. Any criterion change after a control failure --
            even an aggregator repair -- creates an AMENDMENT with a new hash.
            Provenance reads:
                PLAN_002 -> AMENDMENT_A (representation-level control repair; interventions_unseen=true)
            An amendment whose interventions_unseen is False is REVIEW_REQUIRED;
            a plan whose bytes changed with no amendment covering the new hash
            is refused (refuse_unamended_change).
    RULE 2  POWER IN THE FROZEN PACKET. For every STOCHASTIC comparative claim
            the packet carries a power statement. Without one the ruler may
            return DESCRIPTIVE_ESTIMATE and nothing stronger: never
            PREDICTION_FAILED, never CUT_SUPPORTED on that row
            (allowed_verdicts, refuse_verdict). EXACT rows (a kill condition
            that holds or fails deterministically, e.g. "R == 0 every seed")
            are exempt and say so.
    RULE 3  DISJOINT SEEDS. An extension of a preregistered arm uses seeds
            disjoint from the original's; a run whose seed set nests the
            original (seeds 1..400 over 1..50) is NESTED, not a replication,
            and is refused as one (refuse_nested_extension). extension_seeds()
            mints a disjoint block.

Nothing here adjudicates. These are gates on what a ruler may SAY.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from dataclasses import dataclass, asdict, field

PR_VERSION = "PR-1.0.0"

DESCRIPTIVE_ESTIMATE = "DESCRIPTIVE_ESTIMATE"
PREDICTION_FAILED = "PREDICTION_FAILED"
PREDICTION_INDETERMINATE = "PREDICTION_INDETERMINATE"
CUT_SUPPORTED = "CUT_SUPPORTED"
CUT_CHALLENGE = "CUT_CHALLENGE"
PREDICTION_PACKET_CHALLENGE = "PREDICTION_PACKET_CHALLENGE"

STRONG_VERDICTS = (PREDICTION_FAILED, CUT_SUPPORTED)          # need power on a stochastic row
ALWAYS_ALLOWED = (DESCRIPTIVE_ESTIMATE, PREDICTION_INDETERMINATE, CUT_CHALLENGE, PREDICTION_PACKET_CHALLENGE)

POWER_FIELDS = ("n_per_arm", "detectable_effect", "target_power", "method")


class PacketRefused(Exception):
    pass


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ------------------------------------------------------------ RULE 1: amendments

@dataclass
class Amendment:
    plan_id: str                      # e.g. PLAN_002
    amendment_id: str                 # A, B, ...
    parent_sha256: str                # the plan (or previous amendment) bytes it amends
    amended_sha256: str               # the bytes after the change
    kind: str                         # e.g. "representation-level control repair"
    reason: str                       # what failed and what changed, one sentence
    interventions_unseen: bool        # True iff no intervention arm had run when the change was made
    commit: str = ""                  # the commit carrying the change, once known
    created: str = field(default_factory=lambda: _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))

    @property
    def review(self) -> str:
        return "NO_REVIEW_NEEDED" if self.interventions_unseen else "REVIEW_REQUIRED"

    def provenance_line(self) -> str:
        return "%s -> AMENDMENT_%s (%s; interventions_unseen=%s)" % (
            self.plan_id, self.amendment_id, self.kind, "true" if self.interventions_unseen else "false")

    def as_dict(self):
        d = asdict(self)
        d["review"] = self.review
        d["provenance"] = self.provenance_line()
        return d


def amend(plan_id: str, parent_text: str, amended_text: str, kind: str, reason: str,
          interventions_unseen: bool, prior: list = None, commit: str = "") -> Amendment:
    """Mint the next amendment record. Refuses a no-op (identical bytes): a change
    that changed nothing is not an amendment and must not be recorded as one."""
    p, a = sha256_text(parent_text), sha256_text(amended_text)
    if p == a:
        raise PacketRefused("amendment to %s changes no bytes; nothing to record" % plan_id)
    prior = prior or []
    if prior and prior[-1].amended_sha256 != p:
        raise PacketRefused("amendment parent %s is not the latest recorded state %s of %s"
                            % (p[:19], prior[-1].amended_sha256[:19], plan_id))
    letter = chr(ord("A") + len(prior))
    return Amendment(plan_id, letter, p, a, kind, reason, interventions_unseen, commit)


def provenance_chain(plan_id: str, amendments: list) -> str:
    if not amendments:
        return "%s (no amendments)" % plan_id
    return "; ".join(a.provenance_line() for a in amendments)


def refuse_unamended_change(plan_id: str, frozen_sha256: str, current_text: str, amendments: list) -> str:
    """The plan bytes at adjudication must equal the frozen hash or the latest
    amendment's hash. Anything else is a silent post-plan change."""
    cur = sha256_text(current_text)
    latest = amendments[-1].amended_sha256 if amendments else frozen_sha256
    if cur != latest:
        raise PacketRefused("%s bytes at adjudication (%s) match neither the frozen plan (%s) nor the latest "
                            "amendment (%s); record an amendment or restore the plan"
                            % (plan_id, cur[:19], frozen_sha256[:19], latest[:19]))
    return cur


# ------------------------------------------------------------- RULE 2: power

def validate_power_statement(ps: dict) -> list:
    """A power statement names the per-arm n, the effect it can detect at the band
    edge, the target power, and the method (simulation | analytic) with its
    basis. Missing fields are named, not guessed."""
    missing = [f for f in POWER_FIELDS if f not in (ps or {})]
    if missing:
        raise PacketRefused("power statement missing %s" % ", ".join(missing))
    if not (0.0 < float(ps["target_power"]) < 1.0):
        raise PacketRefused("target_power %r is not in (0, 1)" % ps["target_power"])
    if int(ps["n_per_arm"]) <= 0:
        raise PacketRefused("n_per_arm must be positive")
    return list(POWER_FIELDS)


def allowed_verdicts(row: dict) -> tuple:
    """row: {"claim_id", "stochastic": bool, "power_statement": dict|None}.
    EXACT rows (stochastic False) may receive any verdict. Stochastic rows
    without a valid power statement may receive only the ALWAYS_ALLOWED set."""
    if not row.get("stochastic", True):
        return ALWAYS_ALLOWED + STRONG_VERDICTS
    ps = row.get("power_statement")
    if not ps:
        return ALWAYS_ALLOWED
    try:
        validate_power_statement(ps)
    except PacketRefused:
        return ALWAYS_ALLOWED
    return ALWAYS_ALLOWED + STRONG_VERDICTS


def refuse_verdict(row: dict, verdict: str) -> str:
    ok = allowed_verdicts(row)
    if verdict not in ok:
        raise PacketRefused("verdict %s refused on stochastic row %r with no valid power statement in the "
                            "frozen packet; allowed: %s (directive 2026-09-18 s4 rule 2)"
                            % (verdict, row.get("claim_id"), ", ".join(ok)))
    return verdict


# ---------------------------------------------------------- RULE 3: seeds

def seed_relation(original, extension) -> dict:
    o, e = set(int(s) for s in original), set(int(s) for s in extension)
    inter = o & e
    if not inter:
        rel = "DISJOINT"
    elif o <= e:
        rel = "NESTED"                 # the original sits inside the extension: 1..50 in 1..400
    elif e <= o:
        rel = "SUBSET"
    else:
        rel = "OVERLAPPING"
    return {"relation": rel, "n_original": len(o), "n_extension": len(e), "n_shared": len(inter)}


def refuse_nested_extension(original, extension, label: str = "extension") -> dict:
    rel = seed_relation(original, extension)
    if rel["relation"] != "DISJOINT":
        raise PacketRefused("%s seeds are %s with the original (%d shared of %d); an extension is a "
                            "replication only on DISJOINT seeds (directive 2026-09-18 s4 rule 3)"
                            % (label, rel["relation"], rel["n_shared"], rel["n_original"]))
    return rel


def extension_seeds(original, n: int, start: int = None) -> list:
    """Mint n seeds disjoint from `original`, contiguous from max(original)+1
    (or `start`), so the block is reproducible from the original alone."""
    o = set(int(s) for s in original)
    s = (max(o) + 1) if start is None else int(start)
    out = []
    while len(out) < n:
        if s not in o:
            out.append(s)
        s += 1
    return out


# ---------------------------------------------------------------- the gate

def packet_gate(plan_id: str, frozen_plan_sha256: str, current_plan_text: str, amendments: list,
                rows: list, proposed: dict, seed_sets: dict = None) -> dict:
    """Run all three rules before a ruler returns. rows: list of row dicts (RULE 2);
    proposed: {claim_id: verdict}; seed_sets: {claim_id: (original, extension)}
    for any row that extends a preregistered arm. Returns the record the ruler
    prints; raises PacketRefused on the first violation."""
    rec = {"version": PR_VERSION, "plan_id": plan_id,
           "plan_sha256_at_adjudication": refuse_unamended_change(plan_id, frozen_plan_sha256, current_plan_text, amendments),
           "provenance": provenance_chain(plan_id, amendments),
           "amendments_review": [a.review for a in amendments],
           "verdicts": {}, "seeds": {}}
    for row in rows:
        cid = row["claim_id"]
        if cid in proposed:
            rec["verdicts"][cid] = refuse_verdict(row, proposed[cid])
    for cid, (orig, ext) in (seed_sets or {}).items():
        rec["seeds"][cid] = refuse_nested_extension(orig, ext, label=cid)
    return rec
