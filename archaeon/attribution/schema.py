"""Attribution v0 -- an event-level record for reproduction-like events in any engine (NPE, BEE, Archaeon, ...).

The record is a plain dict (JSON-serialisable). Its axes are kept apart because each one has been conflated with another in a
documented Prometheus error:

  carrier      WHO performed the operation (performers, with kinds: organism code, host, neighbour, harness, migration,
               recombination operator, transplant, world physics, ...), plus WHERE the executing code sat and WHAT material it was.
               (v0.3 three-referent governance, B6.)
  production   the physical PROCESS that wrote the child/state (an executed write, a harness copy, a migration copy, an operator
               splice, a transplant insertion, a mutation, a physics rule). Its CHANNEL is organism / infrastructure / physics.
  material     where the child's material came from, PER LOCUS (identity by descent, IBD). Any number of donors. No parent field.
  state        what the child RESEMBLES (identity by state, IBS). Never evidence of descent on its own.
  dependence   named counterfactuals: intervention -> outcome -> result. "X caused Y" is not representable without one.
  capability   what the resulting entity DEMONSTRABLY does, under recorded conditions (inputs, neighbour, scaffold), by an EXECUTED
               test with a named ruler. Labels are not capability evidence.
  contrast     the baseline any share / difference / dependence is measured against.
  aggregation  every organism- or lineage-level label, with the rule that produced it and whether it is a convention. A singular
               parent_id may appear only here, only under rule SINGULAR_MATERIAL_PARENT, and only when the material supports it.

Why this is not the four-axis (CARRIER / RELATION / CONTRAST / AGGREGATION) model: see ATTRIBUTION_V0.md s2. In short, RELATION had
to split into material (IBD), state (IBS), production and dependence, which have different chaining behaviour; and capability is a
property of an entity under conditions, not a relation between events, so it is a fifth axis.

`check(rec)` returns a list of violations (empty = valid). Rule ids are A1..A15; each is documented at its test.
"""
from __future__ import annotations

from typing import Dict, List

SCHEMA = "attribution-v0"
NI = "NOT_IDENTIFIABLE"

PERFORMER_KINDS = {"organism_code", "host_organism", "neighbour_organism", "harness", "migration", "recombination_operator",
                   "transplant", "inflow", "world_physics", "mutation", "unknown"}
ORGANISM_KINDS = {"organism_code", "host_organism", "neighbour_organism"}
PROCESSES = {
    # process                 channel           performer kinds that can carry it
    "executed_write":         ("organism",       ORGANISM_KINDS),
    "harness_copy":           ("infrastructure", {"harness"}),
    "migration_copy":         ("infrastructure", {"migration", "harness"}),
    "recombination_operator": ("infrastructure", {"recombination_operator", "harness"}),
    "transplant_insertion":   ("infrastructure", {"transplant", "harness"}),
    "inflow_injection":       ("infrastructure", {"inflow", "harness"}),
    "mutation_only":          ("physics",        {"mutation", "world_physics"}),
    "physics_rule":           ("physics",        {"world_physics"}),
    "unknown":                ("unknown",        PERFORMER_KINDS),
}
SOURCE_KINDS = {"entity", "new_mutation", "new_input", "new_constant", "new_computed", "new_unspecified", "unknown"}
# how a material source was established; a location / executor / context reading is NOT material evidence (J21 carried over)
MATERIAL_VIA = {"taint", "provenance_log", "harness_log", "replay_taint", "operator_log", "by_construction"}
FORBIDDEN_VIA = {"location", "pc", "executor", "context", "label", "resemblance", "ibs"}
CAPABILITIES = {"exact_self_copy", "approximate_self_copy", "conditional_copy", "host_assisted_copy", "scaffold_dependent_copy",
                "transmits_capability", "none_demonstrated"}
CAP_METHODS_OK = {"executed", "replayed"}
DEP_RESULTS = {"ceases", "persists", "altered", "not_tested"}
DEP_TARGETS = {"material", "machinery", "execution_context", "scaffold", "control_state", "carrier", "input", "other"}
DESCENT_LABELS = {"descends_from", "parent_id", "lineage_member", "self_copy", "self_reproduction", "offspring_of", "SELF_COPY"}
SELF_LABELS = {"self_copy", "self_reproduction", "SELF_COPY", "self_construction", "spontaneous_replicator"}
REPRO_LABELS = {"reproduction", "replicator", "self_reproduction", "spontaneous_replicator", "causal_reproduction"}
RECOMB_LABELS = {"recombinant", "mixed_parent"}
SINGULAR_MIN = 0.75          # declared convention: one donor supplies >= 75% of units ...
SECOND_MAX = 0.10            # ... and no other donor supplies >= 10%
TOP_KEYS = {"schema", "event_id", "engine", "source", "native", "subject", "carrier", "production", "material", "state", "dependence",
            "capability", "contrast", "aggregation"}


def record(event_id, engine, subject, *, source="", native=None, carrier=None, production=None, material=None, state=None,
           dependence=None, capability=None, contrast=None, aggregation=None) -> dict:
    return {"schema": SCHEMA, "event_id": event_id, "engine": engine, "source": source, "native": native or {}, "subject": subject,
            "carrier": carrier or {"performers": [], "exec_where": NI, "exec_what": NI},
            "production": production or {"process": "unknown", "evidence": ""},
            "material": material or {"unit": "byte", "n_units": 0, "resolution": NI, "segments": []},
            "state": state or {"resemblance": []}, "dependence": dependence or [], "capability": capability or [],
            "contrast": contrast or {"baseline": "", "kind": "none_needed"}, "aggregation": aggregation or []}


def seg(lo, hi, kind="entity", entity=None, src_lo=None, via="taint"):
    """material segment: child loci [lo, hi) came from `entity` loci [src_lo, src_lo + hi - lo) (kind 'entity'), or are new."""
    return {"loci": [lo, hi], "source_kind": kind, "entity": entity, "src_loci": None if src_lo is None else [src_lo, src_lo + hi - lo],
            "via": via}


# ------------------------------------------------------------------ derived quantities
def donors(rec) -> Dict[str, float]:
    """material donors -> share of the child's units (IBD). Two segments from one entity are ONE donor (self-cross collapse)."""
    m = rec["material"]; n = m.get("n_units") or 0; out: Dict[str, float] = {}
    if not n: return out
    for s in m["segments"]:
        if s["source_kind"] == "entity" and s.get("entity") is not None:
            out[s["entity"]] = out.get(s["entity"], 0.0) + (s["loci"][1] - s["loci"][0]) / n
    return {k: round(v, 6) for k, v in out.items()}


def new_share(rec) -> float:
    m = rec["material"]; n = m.get("n_units") or 0
    return round(sum(s["loci"][1] - s["loci"][0] for s in m["segments"] if s["source_kind"].startswith("new_")) / n, 6) if n else 0.0


def channel(rec) -> str:
    return PROCESSES.get(rec["production"]["process"], ("unknown",))[0]


def performers(rec, kinds=None) -> List[dict]:
    return [p for p in rec["carrier"]["performers"] if kinds is None or p["kind"] in kinds]


def producer_ids(rec) -> set:
    return {p.get("id") for p in rec["carrier"]["performers"] if p.get("role", "performer") == "performer"}


def producer_ne_donor(rec) -> bool:
    """True when some material donor did not perform the production (or an infrastructure performer did)."""
    d = set(donors(rec)); prod = producer_ids(rec)
    return bool(d) and (bool(d - prod) or channel(rec) != "organism")


def singular_parent(rec):
    """(entity, share) when the material genuinely supports a singular MATERIAL parent under the declared convention, else None."""
    d = sorted(donors(rec).items(), key=lambda kv: -kv[1])
    if not d or d[0][1] < SINGULAR_MIN: return None
    if len(d) > 1 and d[1][1] >= SECOND_MAX: return None
    return d[0]


def singular_loss(rec) -> dict:
    """what a singular-parent description would drop: other donors' material, new material, a producer that is not the donor."""
    d = sorted(donors(rec).items(), key=lambda kv: -kv[1]); top = d[0][1] if d else 0.0
    return {"other_donor_share": round(sum(v for _, v in d[1:]), 6), "new_share": new_share(rec), "producer_ne_donor": producer_ne_donor(rec),
            "n_donors": len(d), "lossless": bool(d) and len(d) == 1 and top >= 0.999 and not producer_ne_donor(rec)}


def capability_of(rec, cap, **cond) -> object:
    """True / False from an EXECUTED claim matching `cap` (and any given condition values); None when not tested."""
    for c in rec["capability"]:
        if c["capability"] != cap or c.get("method") not in CAP_METHODS_OK: continue
        if all(c.get("conditions", {}).get(k) == v for k, v in cond.items()): return c["result"]
    return None


def reproduces(rec, autonomous=None) -> object:
    """any executed positive copy capability (optionally restricted to autonomous = zero neighbour / no scaffold)."""
    seen = False
    for c in rec["capability"]:
        if c.get("method") not in CAP_METHODS_OK or c["capability"] in ("none_demonstrated", "transmits_capability"): continue
        seen = True
        auto = c.get("conditions", {}).get("neighbour") in (None, "zero") and not c.get("conditions", {}).get("scaffold")
        if c["result"] and (autonomous is None or auto == autonomous): return True
    return False if seen else None


# ------------------------------------------------------------------ validator
def check(rec) -> List[str]:
    v: List[str] = []
    # A1 shape; no universal parent field anywhere but aggregation
    miss = TOP_KEYS - set(rec)
    if miss: v.append("A1 missing keys %s" % sorted(miss))
    extra = set(rec) - TOP_KEYS
    if extra: v.append("A1 unknown top-level keys %s (no universal parent field)" % sorted(extra))
    if miss: return v
    for part in ("carrier", "production", "material", "state"):
        for k in rec[part]:
            if "parent" in k.lower(): v.append("A1 %s.%s: parent fields are allowed only as an aggregation convention" % (part, k))
    # A2 production / carrier consistency: the process must be carried by a performer of a matching kind (harness-leak guard)
    proc = rec["production"].get("process")
    if proc not in PROCESSES: v.append("A2 unknown process %r" % proc)
    else:
        ch, kinds = PROCESSES[proc]
        pk = {p["kind"] for p in rec["carrier"]["performers"]}
        bad = pk - PERFORMER_KINDS
        if bad: v.append("A2 unknown performer kinds %s" % sorted(bad))
        if proc != "unknown" and not (pk & kinds):
            v.append("A2 process %s needs a performer of kind %s; got %s" % (proc, sorted(kinds), sorted(pk)))
        if ch == "infrastructure" and pk and pk <= ORGANISM_KINDS:
            v.append("A2 infrastructure process %s credited only to organisms (harness leak)" % proc)
    # A3 carrier WHAT must be material, never filled from WHO/WHERE (J21)
    ew = rec["carrier"].get("exec_what", NI)
    if isinstance(ew, dict) and ew.get("via") in FORBIDDEN_VIA:
        v.append("A3 carrier.exec_what sourced from %s (a WHO/WHERE reading, not material)" % ew.get("via"))
    # A4 material: per-locus segments tile the child; sources established by material evidence
    m = rec["material"]; n = m.get("n_units") or 0
    if m.get("resolution") == "per_locus":
        cov = [0] * n
        for s in m["segments"]:
            lo, hi = s["loci"]
            if not (0 <= lo < hi <= n): v.append("A4 segment %s outside [0,%d)" % (s["loci"], n)); continue
            for p in range(lo, hi): cov[p] += 1
        if any(c != 1 for c in cov): v.append("A4 per-locus segments must tile the child exactly (gaps/overlaps at %d loci)" % sum(c != 1 for c in cov))
    for s in m["segments"]:
        if s["source_kind"] not in SOURCE_KINDS: v.append("A4 unknown source kind %r" % s["source_kind"])
        if s["source_kind"] == "entity" and not s.get("entity"): v.append("A4 entity segment without an entity")
        if s.get("via") in FORBIDDEN_VIA: v.append("A5 material at %s sourced from %s (not material evidence)" % (s["loci"], s["via"]))
        elif s["source_kind"] == "entity" and s.get("via") not in MATERIAL_VIA: v.append("A5 material via %r is not a recognised material channel" % s.get("via"))
    # A6 dependence names the intervention AND the outcome
    for i, d in enumerate(rec["dependence"]):
        if not d.get("intervention"): v.append("A6 dependence[%d] names no intervention" % i)
        if not d.get("outcome"): v.append("A6 dependence[%d] names no outcome" % i)
        if d.get("result") not in DEP_RESULTS: v.append("A6 dependence[%d] result %r" % (i, d.get("result")))
        if d.get("target") not in DEP_TARGETS: v.append("A6 dependence[%d] target %r" % (i, d.get("target")))
        if d.get("result") != "not_tested" and not d.get("contrast"): v.append("A10 dependence[%d] has no contrast" % i)
    # A7 capability is demonstrated by execution under recorded conditions with a named ruler; labels are not capability
    for i, c in enumerate(rec["capability"]):
        if c.get("capability") not in CAPABILITIES: v.append("A7 capability[%d] %r" % (i, c.get("capability")))
        if c.get("result") and c.get("method") not in CAP_METHODS_OK:
            v.append("A7 capability[%d] positive claim by %r (must be executed/replayed, not inferred from a label)" % (i, c.get("method")))
        if c.get("method") in CAP_METHODS_OK and (not c.get("ruler") or "conditions" not in c):
            v.append("A7 capability[%d] executed claim without ruler/conditions" % i)
    # A8 descent labels need material descent; resemblance alone is IBS, not IBD
    labels = {a.get("label") for a in rec["aggregation"]}
    if labels & DESCENT_LABELS and not donors(rec):
        v.append("A8 descent label %s with no material donor (IBS is not IBD)" % sorted(labels & DESCENT_LABELS))
    for a in rec["aggregation"]:
        if a.get("label") in DESCENT_LABELS and a.get("value") is not None and a["value"] not in donors(rec):
            v.append("A8 descent label %s=%r names an entity that supplied no material" % (a["label"], a["value"]))
    # A14 a reproduction label that is not a declared convention needs an executed positive copy capability in this record
    for a in rec["aggregation"]:
        if a.get("label") in REPRO_LABELS and not a.get("convention") and not reproduces(rec):
            v.append("A14 %s asserted without an executed copy capability (labels are not capability)" % a["label"])
    # A15 recombinant labels need two or more distinct material donors (a self-cross is one donor)
    if labels & RECOMB_LABELS and len(donors(rec)) < 2:
        v.append("A15 %s with %d distinct material donor(s)" % (sorted(labels & RECOMB_LABELS), len(donors(rec))))
    # A9 self-labels need organism production by the donor itself
    if labels & SELF_LABELS:
        if channel(rec) != "organism": v.append("A9 self label %s on a %s-channel event" % (sorted(labels & SELF_LABELS), channel(rec)))
        elif producer_ne_donor(rec): v.append("A9 self label %s but a material donor is not the producer" % sorted(labels & SELF_LABELS))
    # A11 a singular parent_id is a convention the material must support
    for a in rec["aggregation"]:
        if not a.get("rule"): v.append("A11 aggregation %r has no rule" % a.get("label"))
        if "convention" not in a: v.append("A11 aggregation %r does not declare convention true/false" % a.get("label"))
        if a.get("label") == "parent_id":
            sp = singular_parent(rec)
            if a.get("rule") != "SINGULAR_MATERIAL_PARENT": v.append("A11 parent_id must use rule SINGULAR_MATERIAL_PARENT")
            elif sp is None: v.append("A11 parent_id but the material has no singular parent (donors %s)" % donors(rec))
            elif a.get("value") != sp[0]: v.append("A11 parent_id %r is not the singular material donor %r" % (a.get("value"), sp[0]))
    # A12 contrast is named whenever shares, resemblance or dependence are reported
    if (m["segments"] or rec["state"]["resemblance"] or rec["dependence"]) and not rec["contrast"].get("baseline"):
        v.append("A12 shares/resemblance/dependence reported with no contrast baseline")
    # A13 resemblance entries name their reference and units
    for r in rec["state"]["resemblance"]:
        if not r.get("reference") or r.get("ibs") is None: v.append("A13 resemblance entry lacks reference or ibs")
    return v
