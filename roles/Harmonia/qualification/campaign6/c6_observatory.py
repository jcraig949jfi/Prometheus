"""Campaign 6 observatory qualification.  OQ-1.0.0  2026-09-18.

Harmonia[m2-ca1148a0]. The operator's Campaign 6 charter (prompts/2026-09-18_
campaign6/00_OPERATOR_DIRECTIVE_CAMPAIGN_6_as_received_by_Harmonia.md) makes
the OBSERVATORY the object of study: "It fails if increasing generative
complexity makes SFE scientifically blind." This module is the part of that
charter this seat can make mechanical before a single Campaign 6 world runs.
It builds no world, organism, pressure or detector (Archaeon, Daedalus,
Proteus, Herakles own those); it decides what the observatory's output may be
QUOTED AS, and it holds the planted fixtures blind.

    1  PROVENANCE LABELS AND THE LLM-FREE FLOOR
       every run carries one of HUMAN_DIRECTED / LLM_PROPOSED / PROCEDURAL /
       EVOLUTION_GENERATED / MIXED; the LLM-free fraction (PROCEDURAL +
       EVOLUTION_GENERATED) is an ELIGIBILITY COUNT printed before any
       cross-lane sentence; below 0.25 the campaign's search-diversity class
       is INELIGIBLE, not "failed"; no single winner score across labels.
    2  FIXTURE CUSTODY (blind spots / anti-gravity)
       planted events are SEALED as sha256 commitments (spec + location +
       the class the observatory should assign) before the campaign opens;
       revealed after the detector firing table is frozen; the reveal is
       verified against the commitment. The operating seats never see the
       registry; this seat does not operate the campaign.
    3  OBSERVATORY RECALL
       detection / preservation / false-escalation / replay-success /
       causal-recovery / classification-accuracy / unknown-retention, each
       with its eligible count and a binomial interval; a detector stack
       that fires on everything scores recall 1.0 and is labelled VACUOUS
       by its false-escalation rate (the cheat control), never "perfect".
    4  ESCALATION ORDER
       preservation (the nine freezes + replay packet) is complete, hashed
       and timestamped BEFORE any classification is written; a
       classification whose timestamp precedes the last freeze is refused.
    5  CLASSIFICATION ADMISSION
       UNKNOWN_MECHANISM is the default; a named mechanism needs at least
       one replay (A/B/C) that reproduces the event AND one causal probe
       (D/E/F/G) that moves it; resemblance is not evidence.
    6  SUCCESS CLASSES
       six independent verdicts, each ELIGIBLE / SUPPORTED / UNSUPPORTED /
       INCONCLUSIVE / INELIGIBLE; a single PASS/FAIL over the campaign is
       refused.
    7  FORBIDDEN CONCLUSIONS
       the five sentences the charter forbids are refused mechanically when
       offered with only the evidence the charter names as insufficient.

Detector DISAGREEMENT and classifier NONE_OF_THE_ABOVE are event classes
(charter, DETECTORS) and are counted as such throughout.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
from dataclasses import dataclass, field, asdict

OQ_VERSION = "OQ-1.0.0"

# ------------------------------------------------------------- vocabularies

PROVENANCE = ("HUMAN_DIRECTED", "LLM_PROPOSED", "PROCEDURAL", "EVOLUTION_GENERATED", "MIXED")
LLM_FREE = ("PROCEDURAL", "EVOLUTION_GENERATED")
LLM_FREE_FLOOR = 0.25

DETECTORS = ("behavioral_novelty", "lineage_discontinuity", "unexpected_transfer", "structural_reuse",
             "environmental_modification", "niche_divergence", "persistence_through_regime_change",
             "sudden_gain_without_local_genotype_explanation", "unexpected_causal_dependence",
             "detector_disagreement", "classifier_failure_unknown_behavior")

FREEZES = ("organism", "parent", "recent_ancestors", "siblings_cousins", "world_state",
           "recent_pressure_history", "mutation_chain", "event_telemetry", "replay_packet")
REPLAYS = ("A_exact_replay", "B_lineage_replay", "C_world_seed_replay")
CAUSAL_PROBES = ("D_mutation_rollback", "E_mechanism_ablation", "F_transfer_held_out_worlds", "G_pressure_history_perturbation")

UNKNOWN_MECHANISM = "UNKNOWN_MECHANISM"
NONE_OF_THE_ABOVE = "NONE_OF_THE_ABOVE"
DISAGREEMENT = "DETECTOR_DISAGREEMENT"

SUCCESS_CLASSES = ("GENERATIVE_EXPANSION", "OBSERVATORY_RECALL", "FORENSIC_RECOVERABILITY",
                   "SEARCH_DIVERSITY", "UNKNOWN_YIELD", "SCALING_HEALTH")
VERDICTS = ("SUPPORTED", "UNSUPPORTED", "INCONCLUSIVE", "INELIGIBLE")

PRESSURE_KINDS = ("EXOGENOUS_PRESSURE", "ENDOGENOUS_PRESSURE", "UNLABELLED")


class ObservatoryRefused(Exception):
    pass


def _sha(obj) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def binomial_interval(k: int, n: int, z: float = 1.96) -> tuple:
    """Wilson interval; (nan, nan) when nothing could be counted."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ------------------------------------------- 1. provenance and the LLM-free floor

def provenance_census(runs) -> dict:
    """runs: iterable of {"run_id", "provenance"}. The LLM-free fraction is an
    eligibility count for SEARCH_DIVERSITY; it is never a score."""
    counts = {p: 0 for p in PROVENANCE}
    bad = []
    for r in runs:
        p = r.get("provenance")
        if p not in PROVENANCE:
            bad.append((r.get("run_id"), p))
            continue
        counts[p] += 1
    if bad:
        raise ObservatoryRefused("runs without a valid provenance label: %s" % bad[:5])
    n = sum(counts.values())
    free = sum(counts[p] for p in LLM_FREE)
    frac = free / n if n else float("nan")
    return {"n_runs": n, "counts": counts, "llm_free_runs": free, "llm_free_fraction": frac,
            "floor": LLM_FREE_FLOOR,
            "search_diversity_eligibility": ("NOTHING_COULD_FIRE" if n == 0 else
                                             "ELIGIBLE" if frac >= LLM_FREE_FLOOR else "INELIGIBLE_BELOW_FLOOR"),
            "note": "labels are compared as populations, never by one winner score (charter, LLM-FREE SEARCH LANES)"}


# -------------------------------------------------------- 2. fixture custody

@dataclass
class FixtureCommitment:
    fixture_id: str
    commitment: str            # sha256 over the sealed spec (class, location, expected observatory behaviour)
    sealed_at: str
    phenomenon_class: str = ""  # revealed later; empty while sealed


def seal_fixtures(fixtures, sealed_at: str = None) -> dict:
    """fixtures: list of {"fixture_id", "phenomenon_class", "location", "expected", "spec"}.
    Returns the registry that IS committed (commitments only) and the sealed
    file content that is NOT (kept by this seat, out of the operating seats'
    reach). Both carry the same fixture ids so a reveal can be matched."""
    at = sealed_at or _now()
    public, private = [], []
    for f in fixtures:
        for k in ("fixture_id", "phenomenon_class", "location", "expected", "spec"):
            if k not in f:
                raise ObservatoryRefused("fixture %s missing %s" % (f.get("fixture_id"), k))
        body = {k: f[k] for k in ("fixture_id", "phenomenon_class", "location", "expected", "spec")}
        c = _sha(body)
        public.append(asdict(FixtureCommitment(f["fixture_id"], c, at)))
        private.append(dict(body, commitment=c, sealed_at=at))
    return {"version": OQ_VERSION, "sealed_at": at, "n_fixtures": len(public),
            "public_registry": public, "private_registry": private,
            "registry_digest": _sha(public)}


def verify_reveal(public_registry, revealed) -> dict:
    """The reveal must reproduce every commitment; a fixture whose commitment
    does not match was changed after sealing and is VOID for recall."""
    by_id = {p["fixture_id"]: p["commitment"] for p in public_registry}
    out = {"verified": [], "void": [], "unrevealed": []}
    seen = set()
    for r in revealed:
        body = {k: r[k] for k in ("fixture_id", "phenomenon_class", "location", "expected", "spec")}
        seen.add(r["fixture_id"])
        if by_id.get(r["fixture_id"]) == _sha(body):
            out["verified"].append(r["fixture_id"])
        else:
            out["void"].append(r["fixture_id"])
    out["unrevealed"] = sorted(set(by_id) - seen)
    return out


# ------------------------------------------------------ 3. observatory recall

def recall_metrics(fixtures_revealed, firings, escalations, natural_events=()) -> dict:
    """fixtures_revealed: verified fixture dicts with "location" (a run/lineage locator the
    firing table also uses) and "phenomenon_class".
    firings: list of {"location", "detector", "score", "threshold", "fired": bool}.
    escalations: list of {"location", "freezes": {...bool per FREEZES}, "replays": {...bool},
                 "causal_probes": {...bool}, "classification": str, "classified_at", "preserved_at"}.
    natural_events: locations escalated that are NOT fixtures (for the false-escalation denominator
    they count as escalations of unknown truth, reported separately, never as false).

    Every rate carries its eligible count (the denominator it was computed on) and a
    Wilson interval. The cheat control lives here: a stack that fires on every location
    has detection 1.0 AND a false-escalation rate at the non-fixture base rate; the
    record labels such a stack VACUOUS rather than perfect."""
    fx = {f["location"]: f for f in fixtures_revealed}
    fired_locs = {f["location"] for f in firings if f.get("fired")}
    esc = {e["location"]: e for e in escalations}
    natural = set(natural_events)

    det_hit = [loc for loc in fx if loc in fired_locs]
    pres_ok = [loc for loc in det_hit if loc in esc and all(esc[loc]["freezes"].get(k) for k in FREEZES)]
    replay_ok = [loc for loc in pres_ok if any(esc[loc].get("replays", {}).get(k) for k in REPLAYS)]
    causal_ok = [loc for loc in replay_ok if any(esc[loc].get("causal_probes", {}).get(k) for k in CAUSAL_PROBES)]
    class_ok = [loc for loc in causal_ok if esc[loc].get("classification") == fx[loc]["phenomenon_class"]]
    unknown_fx = [loc for loc in fx if fx[loc]["phenomenon_class"] == UNKNOWN_MECHANISM]
    unknown_kept = [loc for loc in unknown_fx if loc in esc and esc[loc].get("classification") == UNKNOWN_MECHANISM]
    # false escalation: escalated locations that are neither fixtures nor declared natural events
    all_locs = {f["location"] for f in firings}
    non_fx_fired = [loc for loc in fired_locs if loc not in fx and loc not in natural]
    non_fx_total = [loc for loc in all_locs if loc not in fx and loc not in natural]

    def rate(k, n):
        lo, hi = binomial_interval(len(k), len(n))
        return {"count": len(k), "eligible": len(n), "rate": (len(k) / len(n)) if n else float("nan"),
                "wilson95": [lo, hi], "label": "NOTHING_COULD_FIRE" if not n else "MEASURED"}
    out = {"version": OQ_VERSION,
           "detection": rate(det_hit, list(fx)),
           "preservation": rate(pres_ok, det_hit),
           "replay_success": rate(replay_ok, pres_ok),
           "causal_recovery": rate(causal_ok, replay_ok),
           "classification_accuracy": rate(class_ok, causal_ok),
           "unknown_retention": rate(unknown_kept, unknown_fx),
           "false_escalation": rate(non_fx_fired, non_fx_total),
           "natural_events_escalated": sorted(natural & fired_locs),
           "missed_fixtures": sorted(set(fx) - set(det_hit)),
           "per_class_detection": {}}
    by_class = {}
    for loc, f in fx.items():
        by_class.setdefault(f["phenomenon_class"], [0, 0])
        by_class[f["phenomenon_class"]][1] += 1
        if loc in fired_locs:
            by_class[f["phenomenon_class"]][0] += 1
    out["per_class_detection"] = {c: {"hit": k, "planted": n} for c, (k, n) in sorted(by_class.items())}
    fe = out["false_escalation"]
    out["stack_label"] = ("VACUOUS_FIRES_ON_EVERYTHING" if fe["eligible"] and fe["rate"] >= 0.5 and out["detection"]["rate"] == 1.0
                          else "INFORMATIVE" if fe["eligible"] else "FALSE_ESCALATION_UNMEASURABLE")
    return out


def detector_table(firings) -> dict:
    """The firing table by detector, plus the two event classes the charter names:
    DISAGREEMENT (at one location some detectors fire and others with a score
    are silent) and NONE_OF_THE_ABOVE (classifier_failure fired)."""
    per = {d: {"evaluated": 0, "fired": 0} for d in DETECTORS}
    by_loc = {}
    for f in firings:
        d = f["detector"]
        if d not in DETECTORS:
            raise ObservatoryRefused("unknown detector %r; the eleven are fixed by the charter" % d)
        per[d]["evaluated"] += 1
        per[d]["fired"] += bool(f.get("fired"))
        by_loc.setdefault(f["location"], []).append((d, bool(f.get("fired"))))
    disagreements, none_above, multi = [], [], []
    for loc, ds in by_loc.items():
        fired = [d for d, x in ds if x]
        silent = [d for d, x in ds if not x]
        if fired and silent:
            disagreements.append(loc)
        if len(fired) >= 2:
            multi.append(loc)
        if "classifier_failure_unknown_behavior" in fired:
            none_above.append(loc)
    return {"per_detector": per, "locations": len(by_loc),
            "event_classes": {DISAGREEMENT: sorted(disagreements), NONE_OF_THE_ABOVE: sorted(none_above),
                              "MULTI_RULER": sorted(multi)},
            "note": "a single strong anomaly is preserved regardless of MULTI_RULER (charter, DETECTORS)"}


# --------------------------------------------------------- 4. escalation order

def check_escalation_order(escalation: dict) -> dict:
    """Preservation complete and timestamped before any classification. A
    classification with no preserved_at, or classified before the last freeze,
    is refused: 'Do not explain the event before preservation is complete.'"""
    fr = escalation.get("freezes", {})
    missing = [k for k in FREEZES if not fr.get(k)]
    if missing:
        raise ObservatoryRefused("escalation %s: preservation incomplete, missing %s"
                                 % (escalation.get("location"), missing))
    pa, ca = escalation.get("preserved_at"), escalation.get("classified_at")
    if escalation.get("classification") and (not pa or not ca or ca < pa):
        raise ObservatoryRefused("escalation %s: classification %r written at %s before preservation completed at %s"
                                 % (escalation.get("location"), escalation.get("classification"), ca, pa))
    return {"location": escalation.get("location"), "preserved_at": pa, "classified_at": ca,
            "freezes": len(FREEZES), "packet_digest": _sha(fr)}


# --------------------------------------------------- 5. classification admission

def admit_classification(escalation: dict, proposed: str) -> str:
    """UNKNOWN_MECHANISM always admissible. A named mechanism needs >= 1 replay that
    reproduced the event AND >= 1 causal probe that moved it. Resemblance to a
    literature mechanism is not among the admissible evidence kinds."""
    if proposed in (UNKNOWN_MECHANISM, NONE_OF_THE_ABOVE):
        return proposed
    rp = [k for k in REPLAYS if escalation.get("replays", {}).get(k)]
    cp = [k for k in CAUSAL_PROBES if escalation.get("causal_probes", {}).get(k)]
    if not rp or not cp:
        raise ObservatoryRefused("classification %r at %s refused: needs a reproducing replay (have %s) AND a causal "
                                 "probe that moved the event (have %s); return %s"
                                 % (proposed, escalation.get("location"), rp or "none", cp or "none", UNKNOWN_MECHANISM))
    if escalation.get("evidence_kind") == "RESEMBLANCE":
        raise ObservatoryRefused("classification %r rests on resemblance; forbidden (charter: 'mechanism X occurred' "
                                 "because a trajectory resembles X)" % proposed)
    return proposed


# ----------------------------------------------------------- 6. success classes

@dataclass
class SuccessClassVerdict:
    success_class: str
    verdict: str
    eligible_count: int
    evidence_paths: tuple
    note: str = ""


def campaign_return(verdicts) -> dict:
    """Six independent judgments. Refuses a missing class, an unknown verdict,
    a verdict with no evidence path, and any attempt to collapse them."""
    got = {v.success_class: v for v in verdicts}
    missing = [c for c in SUCCESS_CLASSES if c not in got]
    if missing:
        raise ObservatoryRefused("success classes missing: %s (all six are returned, none collapsed)" % missing)
    for v in verdicts:
        if v.verdict not in VERDICTS:
            raise ObservatoryRefused("%s: verdict %r not in %s" % (v.success_class, v.verdict, VERDICTS))
        if v.verdict != "INELIGIBLE" and not v.evidence_paths:
            raise ObservatoryRefused("%s: a verdict without evidence paths is an assertion" % v.success_class)
        if v.eligible_count == 0 and v.verdict not in ("INELIGIBLE",):
            raise ObservatoryRefused("%s: eligible_count 0 with verdict %s; nothing could fire" % (v.success_class, v.verdict))
    return {"version": OQ_VERSION, "classes": {c: asdict(got[c]) for c in SUCCESS_CLASSES},
            "collapsed_pass_fail": None,
            "note": "infrastructure success with zero natural discoveries is an acceptable result (charter, SUCCESS CLASSES)"}


def refuse_collapse(label: str):
    if label.upper() in ("PASS", "FAIL", "PASS/FAIL", "SUCCESS", "FAILURE"):
        raise ObservatoryRefused("Campaign 6 is not reduced to %s; return the six classes" % label)


# ------------------------------------------------------ 7. forbidden conclusions

FORBIDDEN = {
    "open-ended evolution failed": ("no_dramatic_discovery",),
    "intelligence emerged": ("large_scalar_improvement",),
    "mechanism x occurred": ("resemblance",),
    "nothing happened": ("flat_fitness",),
    "absence of phenomena": ("absence_of_detection_without_recall_calibration",),
}


def refuse_forbidden_conclusion(conclusion: str, evidence_kinds) -> str:
    """Refuses the charter's five sentences when offered with only the evidence
    the charter names as insufficient. With other evidence kinds present the
    sentence is not refused here; admit_classification and campaign_return
    still apply to it."""
    key = conclusion.strip().lower().rstrip(".")
    ek = set(evidence_kinds or ())
    for phrase, insufficient in FORBIDDEN.items():
        if phrase in key and ek and ek <= set(insufficient):
            raise ObservatoryRefused("forbidden conclusion %r on evidence %s alone (charter, FORBIDDEN CONCLUSIONS)"
                                     % (conclusion, sorted(ek)))
        if phrase in key and not ek:
            raise ObservatoryRefused("forbidden conclusion %r offered with no evidence kinds" % conclusion)
    return conclusion


# --------------------------------------------------- the complexity/recall curve

def recall_by_complexity(fixtures_revealed, firings, complexity_of) -> list:
    """The charter's last question, as a measurement: detection rate of planted
    events as a function of the world/organism complexity bin they were planted
    in. complexity_of: location -> bin label. One row per bin with its eligible
    count; a bin with no fixture is NOTHING_COULD_FIRE, never 'safe'."""
    fired = {f["location"] for f in firings if f.get("fired")}
    bins = {}
    for f in fixtures_revealed:
        b = complexity_of(f["location"])
        bins.setdefault(b, [0, 0])
        bins[b][1] += 1
        bins[b][0] += f["location"] in fired
    rows = []
    for b in sorted(bins):
        k, n = bins[b]
        lo, hi = binomial_interval(k, n)
        rows.append({"complexity_bin": b, "planted": n, "detected": k, "rate": k / n if n else float("nan"),
                     "wilson95": [lo, hi], "label": "MEASURED" if n else "NOTHING_COULD_FIRE"})
    return rows
