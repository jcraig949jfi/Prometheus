"""Attribution classes and candidate REPRODUCTION definitions over attribution-v0 records.

production_class(rec)  answers "through which channel, by whom, from whose material". It is the TH-014 known-answer target: records
                       with byte-identical children but different histories must get different classes.
DEFINITIONS            candidate reproduction predicates, deliberately including ones that are too weak and too narrow. They are
                       scored against intended verdicts in fixtures.ADVERSARIAL; none is frozen as THE definition.
transmission(rec)      the three transmissions, reported separately: MATERIAL (IBD from an entity), CAPACITY (the child demonstrably
                       has a copy capability the donor had), HEREDITARY (a named variant intervention on the donor is transmitted to a
                       still-capable child).
"""
from __future__ import annotations

from archaeon.attribution import schema as S


def production_class(rec) -> str:
    ch = S.channel(rec); proc = rec["production"]["process"]
    if ch == "infrastructure":
        return {"harness_copy": "HARNESS_COPY", "migration_copy": "MIGRATION_COPY", "recombination_operator": "OPERATOR_RECOMBINATION",
                "transplant_insertion": "TRANSPLANT_INSERTION", "inflow_injection": "INFLOW_INJECTION"}[proc]
    if ch == "physics": return "PHYSICS_" + proc.upper()
    if ch != "organism": return "UNKNOWN_PRODUCTION"
    d = S.donors(rec); prod = S.producer_ids(rec); kinds = {p["kind"] for p in S.performers(rec)}
    if not d:
        m = rec["material"]; n = m.get("n_units") or 1
        unk = sum(x["loci"][1] - x["loci"][0] for x in m["segments"] if x["source_kind"] == "unknown") / n
        return "MATERIAL_NOT_IDENTIFIED" if unk >= 0.5 else "ORGANISM_WRITTEN_NEW_MATERIAL"   # else painter / originator
    if len(d) > 1:
        return "ORGANISM_RECOMBINATION" + ("_SELF_INCLUDED" if set(d) & prod else "_BY_THIRD_PARTY")
    (donor, _), = d.items()
    if donor in prod: return "SELF_CONSTRUCTED" if kinds <= {"organism_code"} else "SELF_CONSTRUCTED_WITH_HELP"
    if "host_organism" in kinds: return "HOST_WRITTEN"                                   # host code copies another's material
    if "neighbour_organism" in kinds: return "NEIGHBOUR_WRITTEN"                          # a neighbour's code wrote the child
    return "ORGANISM_WRITTEN_OTHERS_MATERIAL"


def transmission(rec, theta=0.5) -> dict:
    d = S.donors(rec); top = max(d.values()) if d else 0.0
    material = top > 0.0
    child_cap = S.reproduces(rec)                                        # donor capability = executed claims ABOUT the donor
    capacity = None if child_cap is None else bool(child_cap and material and any(S.donor_capable(rec, k) for k in d))
    her = [x for x in rec["dependence"] if x.get("target") == "material" and "variant" in x.get("intervention", "")]
    hereditary = None if not her or all(x["result"] == "not_tested" for x in her) else any(x["result"] == "persists" for x in her)
    return {"material": material, "material_top_share": round(top, 6), "capacity": capacity, "hereditary": hereditary}


def _resemblance_max(rec):
    return max((r["ibs"] for r in rec["state"]["resemblance"]), default=0.0)


def _ibs_to(rec, ent):
    for r in rec["state"]["resemblance"]:
        if r["reference"] == ent: return r["ibs"]
    return None


# Each definition: rec -> bool. The docstring says what it accepts.
def D1_RESEMBLANCE(rec):
    """child resembles an existing entity (IBS >= 0.9). Copying = looking alike."""
    return _resemblance_max(rec) >= 0.9


def D2_MATERIAL(rec):
    """some entity supplied >= half of the child's material (IBD). Any channel."""
    return max(S.donors(rec).values(), default=0.0) >= 0.5


def D3_BYTE_IDENTITY(rec):
    """the child is byte-identical to its main material donor (IBD 1.0 and IBS 1.0)."""
    d = S.donors(rec)
    if not d: return False
    top = max(d, key=d.get)
    return d[top] >= 0.999 and (_ibs_to(rec, top) or 0.0) >= 0.999


def D3F_FOUNDER_MATERIAL(rec):
    """the child still carries >= half its bytes as lineage-FOUNDER material (the deep-block TH-007 reading)."""
    return rec["native"].get("founder_share", 0.0) >= 0.5 and D2_MATERIAL(rec)


def D4_ORGANISM_MATERIAL(rec):
    """organism-channel production AND a donor supplied >= half the material. Copying by organisms."""
    return S.channel(rec) == "organism" and D2_MATERIAL(rec)


def D5_CAPACITY(rec):
    """organism-channel production, material flow from a donor that could copy, AND the child demonstrably copies (Griesemer:
    the capacity to reproduce is transmitted with material)."""
    return S.channel(rec) == "organism" and bool(transmission(rec)["capacity"])


def D5T_CAPABLE_MATERIAL(rec, theta=0.5):
    """(added after Review 1) organism-channel production AND the child demonstrably copies AND capable donors supplied >= theta of
    the child's material (any loci, not only machinery)."""
    if S.channel(rec) != "organism" or not S.reproduces(rec): return False
    return sum(v for k, v in S.donors(rec).items() if S.donor_capable(rec, k)) >= theta


def D6_HEREDITARY(rec):
    """(not a reproduction predicate; kept in the table for contrast) organism channel AND the child copies AND a named variant
    introduced in the donor reaches a still-capable child. Built on no other definition (Review 1 CX-3b found it built on D5)."""
    return S.channel(rec) == "organism" and bool(S.reproduces(rec)) and transmission(rec)["hereditary"] is True


def machinery_ibd(rec):
    """share of the child's machinery loci (from its positive executed capability claims) whose material descends from a donor that
    could copy. None when no positive claim lists machinery or the machinery is empty. (Review 1 CX-3a: the former 'RELATIONAL'
    pass for empty machinery let a universal copier make inert junk 'reproduce'; a Tierra parasite HAS local machinery.)"""
    caps = [c for c in rec["capability"] if c.get("method") in S.CAP_METHODS_OK and c["result"] and c.get("machinery_loci")
            and S.about(rec, c) == rec["subject"]]
    if not caps: return None
    loci = sorted({p for c in caps for p in c["machinery_loci"]})
    ok = {k: S.donor_capable(rec, k) for k in S.donors(rec)}; src = {}
    for s_ in rec["material"]["segments"]:
        for p in range(*s_["loci"]): src[p] = s_.get("entity") if s_["source_kind"] == "entity" else None
    return sum(1 for p in loci if src.get(p) is not None and ok.get(src[p])) / len(loci)


def D7_MACHINERY_IBD(rec, theta=0.5):
    """organism-channel production AND the child demonstrably copies AND >= theta of the loci its copying depends on (knockout-
    defined machinery) descend from a capable donor."""
    if S.channel(rec) != "organism" or not S.reproduces(rec): return False
    m = machinery_ibd(rec)
    return m is not None and m >= theta


def D7_STRICT(rec):
    """D7 with theta = 1.0: every machinery byte must descend."""
    return D7_MACHINERY_IBD(rec, 1.0)


DEFINITIONS = {"D1_RESEMBLANCE": D1_RESEMBLANCE, "D2_MATERIAL": D2_MATERIAL, "D3_BYTE_IDENTITY": D3_BYTE_IDENTITY,
               "D3F_FOUNDER_MATERIAL": D3F_FOUNDER_MATERIAL, "D4_ORGANISM_MATERIAL": D4_ORGANISM_MATERIAL, "D5_CAPACITY": D5_CAPACITY,
               "D5T_CAPABLE_MATERIAL": D5T_CAPABLE_MATERIAL,
               "D6_HEREDITARY": D6_HEREDITARY, "D7_MACHINERY_IBD": D7_MACHINERY_IBD, "D7_STRICT": D7_STRICT}


def qualifier(rec) -> str:
    """how the child's demonstrated capability is conditioned: AUTONOMOUS / SCAFFOLDED / HOST_ASSISTED / NONE / UNTESTED."""
    caps = [c for c in rec["capability"] if c.get("method") in S.CAP_METHODS_OK and c["result"] and S.about(rec, c) == rec["subject"]
            and c["capability"] not in ("none_demonstrated", "transmits_capability")]
    if not caps: return "UNTESTED" if S.reproduces(rec) is None else "NONE"
    if any(c.get("conditions", {}).get("neighbour") in (None, "zero") and not c.get("conditions", {}).get("scaffold") for c in caps):
        return "AUTONOMOUS"
    if any(c["capability"] == "host_assisted_copy" or str(c.get("conditions", {}).get("neighbour", "")).startswith("host") for c in caps):
        return "HOST_ASSISTED"
    return "SCAFFOLDED"
