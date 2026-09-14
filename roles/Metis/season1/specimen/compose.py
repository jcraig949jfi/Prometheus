"""Metis Season 1 -- the composition specimen.

Consumes an evidence bundle reconstructed at a historical cutoff and emits
structure: dependence groups, surviving competing explanations, vetoes, and
the cheapest cutoff-available discriminator that partitions what is left.

It does NOT emit a confidence number. That is out of scope by the season
prompt, and there is no scalar anywhere in this file by design.

Deterministic. No learned weights, no model call, no aggregate score.
Every judgement it makes is a set operation over declared structure, and
every declared structure carries a justification string that a reader can
falsify against the cited source.

Vocabulary implemented (v0, on probation -- see SEASON1_PREREGISTRATION s5):
    DEPENDENT, ORTHOGONAL, STALE, INSTRUMENT_SUSPECT,
    BASE_RATE_CONFOUNDED, CHEAP_KILL_AVAILABLE, VETO
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Availability grades that the cutoff rule admits (PREREG s4).
ADMISSIBLE = {"COMMIT", "EXTERNAL", "INTERNAL"}

# Ordinal cost ladder. Deliberately coarse: the record does not support
# more precision, and fabricating it is forbidden by the season prompt.
COST_RANK = {"TRIVIAL": 0, "MINUTES": 1, "HOURS": 2, "DAYS": 3, "WEEKS": 4}


@dataclass(frozen=True)
class Instrument:
    id: str
    # A metric pinned at a degenerate boundary in every stratum observed,
    # while the process feeding it is independently known to be active, is
    # producible by instrument failure as well as by the phenomenon.
    degenerate_boundary: bool = False
    generator_known_active: bool = False
    invalidated_at: str | None = None   # ISO date the instrument was found broken
    note: str = ""

    def suspect_at(self, cutoff: str) -> tuple[bool, str]:
        if self.degenerate_boundary and self.generator_known_active:
            return True, (
                f"instrument {self.id}: metric pinned at its degenerate boundary in "
                f"every observed stratum while its generator is independently "
                f"measured active -- measurement failure explains the observation "
                f"as well as the phenomenon does"
            )
        if self.invalidated_at and self.invalidated_at <= cutoff:
            return True, (
                f"instrument {self.id}: known invalid as of {self.invalidated_at}, "
                f"at or before this cutoff"
            )
        return False, ""


@dataclass(frozen=True)
class Evidence:
    id: str
    supports: str                     # explanation id this item is read as supporting
    availability: str                 # COMMIT | EXTERNAL | INTERNAL | UNAVAILABLE_UNPROVEN
    upstream: frozenset[str]          # load-bearing causal ancestry tokens
    rules_out: frozenset[str] = frozenset()   # explanations its OBSERVED value eliminates
    justification: str = ""           # why rules_out is what it is, citing the value
    instrument: Instrument | None = None
    # Negative-existence claims (the C-05 class).
    negative_existence: bool = False
    search_domain: str | None = None
    enumeration_complete: bool = False
    # Staleness: contrary information that existed at or before the cutoff.
    contrary_available_at: str | None = None
    contrary_incorporated: bool = False
    source: str = ""                  # committed path or dated external artifact


@dataclass(frozen=True)
class Discriminator:
    id: str
    available_at_cutoff: bool
    cost: str                         # key of COST_RANK
    # Explanations this test would eliminate, per outcome branch. A test whose
    # branches do not differ has no discriminatory power and is dropped.
    outcome_branches: tuple[frozenset[str], ...]
    note: str = ""

    def partitions(self, live: frozenset[str]) -> bool:
        """True if the branches split the live set differently from each other."""
        seen = {frozenset(live - b) for b in self.outcome_branches}
        return len(seen) > 1


@dataclass
class Bundle:
    episode: str
    decision: str
    cutoff: str
    claim: str
    explanations: dict[str, str]
    evidence: list[Evidence]
    discriminators: list[Discriminator] = field(default_factory=list)
    baseline_experiment_cost: str | None = None   # what was actually run


@dataclass
class Result:
    episode: str
    cutoff: str
    claim: str
    admitted: list[str]
    dropped_unavailable: list[str]
    groups: list[dict]
    live_explanations: list[str]
    vetoes: list[dict]
    unknowns: list[dict]
    discriminator: dict | None
    rejected_discriminators: list[dict]

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, sort_keys=True, default=list)


def _group_by_shared_upstream(items: list[Evidence]) -> list[list[Evidence]]:
    """Union-find over shared load-bearing upstream tokens.

    Two items are DEPENDENT when their causal ancestries intersect. Items in
    one group are ONE reason to believe, however many names they carry.
    """
    parent: dict[str, str] = {e.id: e.id for e in items}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if a.upstream & b.upstream:
                union(a.id, b.id)

    out: dict[str, list[Evidence]] = {}
    for e in items:
        out.setdefault(find(e.id), []).append(e)
    return list(out.values())


class BundleError(ValueError):
    """A bundle that refers to an explanation it never declared."""


def validate(bundle: Bundle) -> None:
    """Fail loud on an undeclared explanation id.

    Found by running the specimen on E1: `rules_out: ["PURE_FORMAT_ONLY"]`
    named nothing, eliminated nothing, and raised nothing -- a typo silently
    weakened the mechanism in the permissive direction. That is the exact
    defect class this seat has been tracking in other people's code
    (metis.py's `except: pass`, metis_portfolio.py's "(state.json reports
    up)"), so it is not tolerated here. Unknown token is an error, never a
    no-op.
    """
    declared = set(bundle.explanations)
    if bundle.claim not in declared:
        raise BundleError(f"claim {bundle.claim!r} is not a declared explanation")
    for e in bundle.evidence:
        if e.supports not in declared:
            raise BundleError(
                f"{e.id}: supports {e.supports!r}, which is not declared")
        unknown = set(e.rules_out) - declared
        if unknown:
            raise BundleError(
                f"{e.id}: rules_out names undeclared explanation(s) {sorted(unknown)}")
    for d in bundle.discriminators:
        for b in d.outcome_branches:
            unknown = set(b) - declared
            if unknown:
                raise BundleError(
                    f"{d.id}: outcome branch names undeclared {sorted(unknown)}")


def compose(bundle: Bundle) -> Result:
    validate(bundle)
    # --- 1. Availability filter (PREREG s4d): unproven availability is unusable.
    admitted = [e for e in bundle.evidence if e.availability in ADMISSIBLE]
    dropped = [e.id for e in bundle.evidence if e.availability not in ADMISSIBLE]

    vetoes: list[dict] = []
    unknowns: list[dict] = []

    # --- 2. Search completeness (the C-05 rule). A negative-existence claim
    # without an enumeration guarantee is UNKNOWN, never ABSENT. It is removed
    # from the supporting evidence entirely -- it cannot support anything.
    usable: list[Evidence] = []
    for e in admitted:
        if e.negative_existence and not e.enumeration_complete:
            unknowns.append({
                "kind": "ABSENCE_UNPROVEN",
                "evidence": e.id,
                "search_domain": e.search_domain,
                "detail": (
                    "negative existence claimed without exhaustive enumeration of the "
                    "declared search domain; downgraded to UNKNOWN and withheld from "
                    "the supporting set"
                ),
            })
            continue
        usable.append(e)

    # --- 3. Dependence grouping. Support is counted in GROUPS, never in items.
    supporting = [e for e in usable if e.supports == bundle.claim]
    groups = _group_by_shared_upstream(supporting)
    group_view = []
    for g in sorted(groups, key=lambda g: sorted(x.id for x in g)[0]):
        shared = frozenset.intersection(*[x.upstream for x in g]) if len(g) > 1 else frozenset()
        group_view.append({
            "members": sorted(x.id for x in g),
            "shared_upstream": sorted(shared),
            "independent_reason_count_contribution": 1,
        })
        if len(g) > 1:
            vetoes.append({
                "kind": "AGREEMENT_NOT_ADDITIVE",
                "members": sorted(x.id for x in g),
                "shared_upstream": sorted(shared),
                "detail": (
                    f"{len(g)} evidence items collapse to ONE independent reason: they "
                    f"share load-bearing upstream {sorted(shared)}. Agreement among them "
                    f"is a property of the shared ancestor, not corroboration."
                ),
            })

    # --- 4. Live competing explanations. An explanation dies only when some
    # usable item's OBSERVED value eliminates it.
    eliminated: set[str] = set()
    for e in usable:
        eliminated |= set(e.rules_out)
    live = frozenset(x for x in bundle.explanations if x != bundle.claim and x not in eliminated)

    for x in sorted(live):
        vetoes.append({
            "kind": "CONFIDENCE_VETO",
            "explanation": x,
            "detail": (
                f"competing explanation {x} ({bundle.explanations[x]}) is not eliminated "
                f"by any admitted evidence item; confidence in '{bundle.claim}' must not "
                f"be compounded until it is"
            ),
        })

    # --- 5. Instrument vetoes.
    for e in usable:
        if e.instrument is None:
            continue
        suspect, why = e.instrument.suspect_at(bundle.cutoff)
        if suspect:
            vetoes.append({
                "kind": "INSTRUMENT_VETO",
                "evidence": e.id,
                "detail": why,
            })

    # --- 6. Staleness: contrary information available at cutoff, unincorporated.
    for e in usable:
        if e.contrary_available_at and not e.contrary_incorporated \
                and e.contrary_available_at <= bundle.cutoff:
            vetoes.append({
                "kind": "STALE_VETO",
                "evidence": e.id,
                "detail": (
                    f"contrary information was available at {e.contrary_available_at}, "
                    f"at or before this cutoff, and is not incorporated"
                ),
            })

    # --- 7. Cheapest discriminator with actual discriminatory power.
    chosen = None
    rejected: list[dict] = []
    viable = []
    for d in bundle.discriminators:
        if not d.available_at_cutoff:
            rejected.append({"id": d.id, "reason": "NOT_AVAILABLE_AT_CUTOFF"})
            continue
        if not live:
            rejected.append({"id": d.id, "reason": "NOTHING_LIVE_TO_DISCRIMINATE"})
            continue
        if not d.partitions(live):
            rejected.append({
                "id": d.id,
                "reason": "NO_DISCRIMINATORY_POWER",
                "detail": "every outcome branch leaves the same live set; both "
                          "hypotheses predict it equally",
            })
            continue
        if bundle.baseline_experiment_cost is not None and \
                COST_RANK[d.cost] >= COST_RANK[bundle.baseline_experiment_cost]:
            rejected.append({
                "id": d.id,
                "reason": "NOT_CHEAPER_THAN_BASELINE",
                "detail": f"cost {d.cost} >= baseline {bundle.baseline_experiment_cost}",
            })
            continue
        viable.append(d)

    if viable:
        viable.sort(key=lambda d: (COST_RANK[d.cost], d.id))
        d = viable[0]
        chosen = {
            "kind": "CHEAP_KILL_AVAILABLE",
            "id": d.id,
            "cost": d.cost,
            "eliminates_by_branch": [sorted(b) for b in d.outcome_branches],
            "note": d.note,
        }

    return Result(
        episode=bundle.episode,
        cutoff=bundle.cutoff,
        claim=bundle.claim,
        admitted=sorted(e.id for e in usable),
        dropped_unavailable=sorted(dropped),
        groups=group_view,
        live_explanations=sorted(live),
        vetoes=vetoes,
        unknowns=unknowns,
        discriminator=chosen,
        rejected_discriminators=rejected,
    )


# --------------------------------------------------------------------------
# Bundle loading (JSON on disk -> dataclasses). Kept dumb on purpose.
# --------------------------------------------------------------------------

def load_bundle(path: str | Path) -> Bundle:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    ev = []
    for e in d["evidence"]:
        inst = None
        if e.get("instrument"):
            i = e["instrument"]
            inst = Instrument(
                id=i["id"],
                degenerate_boundary=i.get("degenerate_boundary", False),
                generator_known_active=i.get("generator_known_active", False),
                invalidated_at=i.get("invalidated_at"),
                note=i.get("note", ""),
            )
        ev.append(Evidence(
            id=e["id"],
            supports=e["supports"],
            availability=e["availability"],
            upstream=frozenset(e.get("upstream", [])),
            rules_out=frozenset(e.get("rules_out", [])),
            justification=e.get("justification", ""),
            instrument=inst,
            negative_existence=e.get("negative_existence", False),
            search_domain=e.get("search_domain"),
            enumeration_complete=e.get("enumeration_complete", False),
            contrary_available_at=e.get("contrary_available_at"),
            contrary_incorporated=e.get("contrary_incorporated", False),
            source=e.get("source", ""),
        ))
    disc = [
        Discriminator(
            id=x["id"],
            available_at_cutoff=x["available_at_cutoff"],
            cost=x["cost"],
            outcome_branches=tuple(frozenset(b) for b in x["outcome_branches"]),
            note=x.get("note", ""),
        )
        for x in d.get("discriminators", [])
    ]
    return Bundle(
        episode=d["episode"],
        decision=d["decision"],
        cutoff=d["cutoff"],
        claim=d["claim"],
        explanations=d["explanations"],
        evidence=ev,
        discriminators=disc,
        baseline_experiment_cost=d.get("baseline_experiment_cost"),
    )


def render(r: Result) -> str:
    """Human-readable rendering. Structure only; no score anywhere."""
    L = [f"EPISODE {r.episode}", f"CUTOFF  {r.cutoff}", f"CLAIM   {r.claim}", ""]
    L.append(f"ADMITTED EVIDENCE ({len(r.admitted)}): {', '.join(r.admitted) or '(none)'}")
    if r.dropped_unavailable:
        L.append(f"DROPPED (availability unproven): {', '.join(r.dropped_unavailable)}")
    L.append("")
    L.append(f"INDEPENDENT REASONS: {len(r.groups)} "
             f"(from {sum(len(g['members']) for g in r.groups)} supporting items)")
    for g in r.groups:
        tag = "DEPENDENT" if len(g["members"]) > 1 else "single"
        L.append(f"  [{tag}] {', '.join(g['members'])}"
                 + (f"   shared: {', '.join(g['shared_upstream'])}" if g["shared_upstream"] else ""))
    L.append("")
    L.append(f"LIVE COMPETING EXPLANATIONS: {', '.join(r.live_explanations) or '(none)'}")
    L.append("")
    if r.vetoes:
        L.append(f"VETOES ({len(r.vetoes)}):")
        for v in r.vetoes:
            head = v.get("explanation") or v.get("evidence") or ", ".join(v.get("members", []))
            L.append(f"  {v['kind']}: {head}")
            L.append(f"      {v['detail']}")
    else:
        L.append("VETOES: none -- composition permitted")
    if r.unknowns:
        L.append("")
        L.append(f"UNKNOWNS ({len(r.unknowns)}):")
        for u in r.unknowns:
            L.append(f"  {u['kind']}: {u['evidence']}  domain={u['search_domain']}")
    L.append("")
    if r.discriminator:
        d = r.discriminator
        L.append(f"NEXT DISCRIMINATOR: {d['id']}  (cost {d['cost']})")
        if d["note"]:
            L.append(f"      {d['note']}")
    else:
        L.append("NEXT DISCRIMINATOR: none proposed")
    if r.rejected_discriminators:
        for x in r.rejected_discriminators:
            L.append(f"  rejected {x['id']}: {x['reason']}")
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(render(compose(load_bundle(p))))
        print("\n" + "=" * 74 + "\n")
