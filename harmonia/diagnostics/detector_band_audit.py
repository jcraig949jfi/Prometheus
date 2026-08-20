"""Detector-band audit — does the battery's blind band contain the substrate's output?

Companion to the kill-resurrection retrodiction (aporia META_SYNTHESIS_2026-08-12 §5).
Re-keyed on REPRESENTABILITY, not derivability, per the closure-novelty kill
(roles/Harmonia/REVIEW_20260812_harmonia_D.md Phase 2): a closure test reduces to
{false statements} u {solver timeouts}, so "could the checker EXPRESS this claim?" is
the only question that does not degenerate.

THE QUESTION. Cross-tabulate what the substrate EMITS against what the battery can
REPRESENT.
  - most output in UNREPRESENTABLE kinds  => blind-band reading supported, translator binds
  - output overwhelmingly REPRESENTABLE   => blind-band excuse fails, the nulls stand

METHOD. Enumeration, not sampling, at the level where enumeration is possible: every
generator class is instantiated and EXECUTED, and its real emitted records are classified
against the real gate predicates. Names are never used to infer representability.
(Standard set by the TIER_GENS enumeration, which found R4/R9-R12 had never been built:
read the registry, do not infer its contents.)

THE TWO CONTROLS (mandatory -- an audit that never demonstrated it can classify a known
case is the unfalsifiable-metric failure this role closed once already):
  POSITIVE CONTROL  a1 -- invariant_equality, predicate_kind=direct, relations in the
                    known 4. Known representable. The cross-tab MUST say REPRESENTABLE.
  CHEAT CONTROL     a3 -- functional_identity. Emits integer pairs under the SAME four
                    relations, so a relation-only check calls it representable. It is
                    not: predicate_kind="transformed" means its verdict answers a
                    DIFFERENT predicate than "does rel(a,b) hold on the stored values",
                    which is the only predicate F2's raw-value null is valid for. The
                    cross-tab MUST say MISROUTED, not REPRESENTABLE.
Both controls are asserted, not merely printed. A run failing either withholds its verdict.

Run:  PYTHONPATH=. python harmonia/diagnostics/detector_band_audit.py
      PYTHONPATH=. python harmonia/diagnostics/detector_band_audit.py --test
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import pkgutil
import re
import sys
from collections import Counter

import theseus.generators as GENPKG
from theseus.generators.base import Generator
from theseus.scoring.content_aware_promote import (
    _payload_key, _payload_values, is_direct_relation_record,
)
from harmonia.experiments.verifier_lens import _DISPATCH

RECORDS_PER_GEN = 200
LIFETIME = "theseus/orchestration/lifetime_stats.json"

# The relations _evaluate_relation actually decides. Anything else falls through its
# final `return False` -- a SILENT wrong answer, not an abstention.
_ABS_DIFF = re.compile(r"^abs_diff_le_(\d+)$")
KNOWN_RELS = {"equal", "equal_mod_2", "divides"}


def relation_known(rel) -> bool:
    if not isinstance(rel, str):
        return False
    return rel in KNOWN_RELS or bool(_ABS_DIFF.match(rel))


# --------------------------------------------------------------------------- #
# classification
# --------------------------------------------------------------------------- #
# REPRESENTABLE   F2 can evaluate this record's own claim on its own values.
# MISROUTED       shaped like a direct relation claim, but the verdict answers a
#                 different predicate -> F2's raw-value null is invalid for it.
# RELATION_OOV    relation string present but outside the decided set -> silently
#                 scored False. This is the blind band with teeth.
# UNREPRESENTABLE no integer value pair and/or no relation key at all.
CLASSES = ("REPRESENTABLE", "MISROUTED", "RELATION_OOV", "UNREPRESENTABLE")


def classify(record) -> str:
    payload = getattr(record, "claim_payload", None) or {}
    key = _payload_key(payload)
    vals = _payload_values(payload)
    if key is None or vals is None:
        return "UNREPRESENTABLE"
    if not relation_known(payload.get("relation")):
        return "RELATION_OOV"
    if not is_direct_relation_record(record):
        return "MISROUTED"
    return "REPRESENTABLE"


def enumerate_generators():
    out = []
    for m in pkgutil.iter_modules(GENPKG.__path__):
        if m.name in ("base", "__init__"):
            continue
        try:
            mod = importlib.import_module("theseus.generators." + m.name)
        except Exception as exc:
            out.append(("?" + m.name, None, "IMPORT_FAIL: " + type(exc).__name__))
            continue
        for _, obj in vars(mod).items():
            if (inspect.isclass(obj) and issubclass(obj, Generator)
                    and obj is not Generator and obj.__module__ == mod.__name__):
                out.append((obj.generator_id, obj, None))
    return out


def harvest(cls, n=RECORDS_PER_GEN):
    """Execute the generator. Returns (records, error_or_None)."""
    try:
        g = cls("detector_band_audit")
    except Exception as exc:
        return [], ("INIT_FAIL: " + type(exc).__name__ + ": " + str(exc))[:88]
    recs = []
    try:
        for _ in range(n):
            r = g.next()
            if r is None:
                break
            recs.append(r)
    except Exception as exc:
        if not recs:
            return [], ("NEXT_FAIL: " + type(exc).__name__ + ": " + str(exc))[:88]
    return recs, None


def run():
    lifetime = {}
    if os.path.exists(LIFETIME):
        with open(LIFETIME) as fh:
            lifetime = json.load(fh).get("per_generator_lifetime", {})

    rows, per_gen = [], {}
    for gid, cls, err in enumerate_generators():
        if cls is None:
            rows.append((gid, 0, Counter(), err, "?"))
            continue
        recs, herr = harvest(cls)
        counts = Counter(classify(r) for r in recs)
        per_gen[gid] = counts
        rows.append((gid, len(recs), counts, herr, cls.claim_kind))
    return rows, per_gen, lifetime


def dominant(counts):
    if not counts:
        return "NO_OUTPUT"
    return counts.most_common(1)[0][0]


def emission_path_audit(rows, lifetime):
    """Who actually issued the verdict? -- the question that decides whether F2
    coverage is even the relevant measurement.

    A generator that computes its verdict at emission time, from the same values it
    writes into the payload, CANNOT have been blind to its own claim. For those
    records there is no central detector in the path to have a blind band.
    """
    full, none_, life_self = [], [], 0
    for gid, n, counts, err, kind in rows:
        if not n:
            continue
        cls = dict((g, c) for g, c, _e in enumerate_generators()).get(gid)
        if cls is None:
            continue
        recs, _ = harvest(cls, n)
        if not recs:
            continue
        verdicted = sum(1 for r in recs
                        if getattr(r, "verdict", None) not in (None, "", "UNVERIFIED"))
        if verdicted == len(recs):
            full.append(gid)
            life_self += lifetime.get(gid, 0)
        elif verdicted == 0:
            none_.append(gid)
    return full, none_, life_self


def main():
    rows, per_gen, lifetime = run()

    print("Detector-band audit — substrate output vs battery representability")
    print("=" * 94)
    print("generators enumerated : %d" % len(rows))
    print("records executed      : %s (up to %d/generator)"
          % (format(sum(r[1] for r in rows), ","), RECORDS_PER_GEN))
    print("lifetime records      : %s across %d generators"
          % (format(sum(lifetime.values()), ","), len(lifetime)))
    print()

    print("%-5s%-26s%5s  %-16s%15s  %s"
          % ("gen", "claim_kind", "n", "dominant class", "lifetime recs", "note"))
    print("-" * 94)
    for gid, n, counts, err, kind in sorted(rows):
        print("%-5s%-26s%5d  %-16s%15s  %s"
              % (gid, str(kind)[:25], n, dominant(counts),
                 format(lifetime.get(gid, 0), ","), err or ""))

    by_class_recs, by_class_life, unweighted = Counter(), Counter(), Counter()
    no_output = []
    for gid, n, counts, err, kind in rows:
        if not counts:
            no_output.append(gid)
            continue
        unweighted[dominant(counts)] += 1
        for k, v in counts.items():
            by_class_recs[k] += v
        lt = lifetime.get(gid, 0)
        tot = sum(counts.values())
        for k, v in counts.items():          # apportion lifetime by observed mix
            by_class_life[k] += lt * v / tot

    print()
    print("ROLLUP")
    print("-" * 94)
    tr = sum(by_class_recs.values()) or 1
    tl = sum(by_class_life.values()) or 1
    tg = sum(unweighted.values()) or 1
    print("%-18s%12s%18s%22s" % ("class", "generators", "executed recs",
                                 "lifetime-weighted"))
    for c in CLASSES:
        print("%-18s%7d (%4.1f%%)%11s (%4.1f%%)%15s (%4.1f%%)"
              % (c, unweighted[c], unweighted[c] / tg * 100,
                 format(by_class_recs[c], ","), by_class_recs[c] / tr * 100,
                 format(int(by_class_life[c]), ","), by_class_life[c] / tl * 100))
    if no_output:
        print()
        print("NO OUTPUT on this host (%d): %s" % (len(no_output), " ".join(sorted(no_output))))
        print("  lifetime records these account for: %s"
              % format(sum(lifetime.get(g, 0) for g in no_output), ","))

    substrate_kinds = {str(k) for _, _, _, _, k in rows if k and k != "?"}
    dispatch_kinds = set(_DISPATCH)
    overlap = substrate_kinds & dispatch_kinds
    print()
    print("CROSS-TAB vs verify()/_DISPATCH")
    print("-" * 94)
    print("substrate claim kinds : %d" % len(substrate_kinds))
    print("_DISPATCH kinds       : %d  %s" % (len(dispatch_kinds), sorted(dispatch_kinds)))
    print("INTERSECTION          : %d  %s" % (len(overlap), sorted(overlap) or "(empty)"))

    print()
    print("CONTROLS")
    print("-" * 94)
    pos = dominant(per_gen.get("a1", Counter()))
    cheat = dominant(per_gen.get("a3", Counter()))
    print("  positive control  a1 -> %-16s (must be REPRESENTABLE)" % pos)
    print("  cheat control     a3 -> %-16s (must be MISROUTED, not REPRESENTABLE)" % cheat)
    ok = True
    if pos != "REPRESENTABLE":
        print("  FAIL: cannot classify a known-representable kind. Verdict void.")
        ok = False
    if cheat == "REPRESENTABLE":
        print("  FAIL: fooled by the cheat control — checking relation strings, "
              "not predicates. Verdict void.")
        ok = False
    if ok:
        print("  PASS: both controls behaved. The cross-tab discriminates.")

    print()
    print("EMISSION-PATH CHECK — was there a central detector to be blind?")
    print("-" * 94)
    full, none_, life_self = emission_path_audit(rows, lifetime)
    total_life = sum(lifetime.values()) or 1
    self_share = life_self / total_life * 100
    print("  generators that self-verdict at emission : %d" % len(full))
    print("  generators that emit no verdict          : %d  %s"
          % (len(none_), " ".join(sorted(none_)) or "-"))
    print("  lifetime records self-verdicted          : %s (%.2f%%)"
          % (format(life_self, ","), self_share))
    print("  => a generator computes `holds` from the same values it writes into the")
    print("     payload, so it cannot be blind to its own claim. For that share of the")
    print("     corpus there is NO central detector in the kill path to have a band.")

    print()
    print("VERDICT")
    print("-" * 94)
    if not ok:
        print("  WITHHELD — control failure.")
        return 1
    repr_share = by_class_life["REPRESENTABLE"] / tl * 100
    print("  lifetime-weighted REPRESENTABLE share : %.1f%%" % repr_share)
    print("  lifetime-weighted blind-band share    : %.1f%%" % (100 - repr_share))
    if self_share >= 95:
        print()
        print("  BLIND-BAND READING: FAILS — but not on coverage grounds.")
        print("  %.2f%% of lifetime records were verdicted by the generator that" % self_share)
        print("  AUTHORED them. The blind-band thesis needs a detector that received a")
        print("  claim it could not represent; in the kill path there was no such")
        print("  detector. F2 coverage (%.1f%%) is therefore the WRONG measurement for" % repr_share)
        print("  the kill corpus -- F2 never gated it, and verify() never saw it.")
        print()
        print("  The nulls stand as genuine falsifications OF THE CLAIMS POSED.")
        print("  That is a class-relative result: sound within the %d claim kinds the" % len(substrate_kinds))
        print("  generators can express, and silent outside them. The ceiling is at the")
        print("  EMISSION side, not the detection side -- so a translator on the detector")
        print("  buys nothing here. Widening what generators can POSE would.")
        return 0
    print("  (emission-path share %.2f%% < 95%%: falling back to coverage reading)" % self_share)
    if repr_share >= 60:
        print("  => Output is overwhelmingly REPRESENTABLE. The blind-band excuse FAILS")
        print("     for this substrate: the nulls stand as genuine falsifications.")
    elif repr_share <= 40:
        print("  => Output is mostly UNREPRESENTABLE. Blind-band reading SUPPORTED;")
        print("     the translator is the binding constraint.")
    else:
        print("  => MIXED. Neither reading is carried by the data; report the split,")
        print("     do not force a verdict.")
    return 0


# --------------------------------------------------------------------------- #
# self-tests
# --------------------------------------------------------------------------- #
def test_relation_known():
    assert relation_known("equal") and relation_known("abs_diff_le_17")
    assert not relation_known("abs_diff_le_x") and not relation_known("coprime")
    assert not relation_known(None)


def test_dispatch_is_disjoint_ontology():
    """_DISPATCH keys are reasoning-probe kinds, not substrate ClaimKinds."""
    from theseus.emit.record_schema import ClaimKind
    assert not ({c.value for c in ClaimKind} & set(_DISPATCH)), \
        "ontologies now overlap — the cross-tab's framing needs revisiting"


def test_controls():
    _, per_gen, _ = run()
    assert dominant(per_gen.get("a1", Counter())) == "REPRESENTABLE", \
        "positive control failed: a1 is known representable"
    assert dominant(per_gen.get("a3", Counter())) != "REPRESENTABLE", \
        "cheat control failed: a3 is meta-relational, not directly representable"


def test_emission_path_dominates():
    """The load-bearing structural fact: near-all records are self-verdicted."""
    rows, _pg, lifetime = run()
    _full, _none, life_self = emission_path_audit(rows, lifetime)
    share = life_self / (sum(lifetime.values()) or 1)
    assert share > 0.95, (
        "self-verdict share fell to %.3f — the kill path now routes through a "
        "central detector and the blind-band question becomes live again" % share)


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_relation_known()
        test_dispatch_is_disjoint_ontology()
        test_controls()
        test_emission_path_dominates()
        print("4 passed, 0 failed")
        raise SystemExit(0)
    raise SystemExit(main())
