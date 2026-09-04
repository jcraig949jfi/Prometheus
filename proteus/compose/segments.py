"""Segment (primitive) identity, composition identity, and exact ablation.

WHAT A PRIMITIVE IS HERE
------------------------
A segment is a contiguous run of whole instructions. That is the smallest thing the frozen
runtime can be said to contain, and it is a STRUCTURAL primitive, never a semantic one: nothing
in this module knows or asks what a segment computes. Directive section 5 permits exactly this.

WHY COMPOSITION IS CONCATENATION AND NOTHING ELSE
-------------------------------------------------
The runtime executes `op = tape[ip] mod N_OPCODES` from ip=0 with ip advancing by 4 and wrapping
modulo tape_words. Laying components end to end is therefore the only join that needs no new
runtime semantics. No graph language, no dispatcher, no conditional glue: directive section 6
says not to build one until A+B proves it necessary, and A+B does not.

WHY ABLATION IS NOP-SUBSTITUTION AND NOT DELETION
--------------------------------------------------
Deleting a component's words would shift every later component's tape address. The runtime
addresses the tape by `r[b] mod tape_words` (LD/ST) and jumps by signed instruction offsets, so a
shift silently changes what every surviving instruction reads and where every jump lands. The
ablated system would then differ from the original in the removed component AND in the addresses
of everything after it -- exactly the confound directive section 7 forbids. NOP-substitution
preserves length, offsets and every other component's words byte for byte, so the only declared
difference is that the named component no longer executes.

THE RESIDUAL CONFOUND, MEASURED NOT ASSUMED
--------------------------------------------
NOP-substitution is still not perfectly inert. The genome is copied into the tape
(vm.Player.fresh_state), so an opcode word is also a DATUM that LD can read. Substituting it
changes that datum's value. `ablation_report` therefore certifies an ablation only after the
NOP-ALIAS DIFFERENTIAL: every word w with w mod N_OPCODES == 0 decodes to NOP, so ablating to 0,
to N_OPCODES and to 2*N_OPCODES are three instruction-identical, data-different operations. If
the transcripts agree the ablation is certified EXACT on that ensemble; if they disagree the
ablation is reported CONFOUNDED_BY_DATA_CHANNEL and is never silently passed.

That certificate is ensemble-relative and is a LOWER BOUND on confounding: it detects a data
dependence only if the dependence reaches the transcript on the probes actually run.
"""
from __future__ import annotations

from proteus.foundry.affordances import CATEGORY, N_OPCODES, NOP, STORAGE_BOUNDS
from proteus.foundry.identity import hash_obj
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes, run_ensemble
from proteus.foundry.vm import SCHEMA as MANIFEST_SCHEMA
from proteus.foundry.vm import Meter, ManifestError, validate_manifest

SEGMENT_SCHEMA = "proteus.segment.v0"
COMPOSITION_SCHEMA = "proteus.composition.v0"
IW = STORAGE_BOUNDS["instruction_words"]
MASK32 = 0xFFFFFFFF

#: Words that are instruction-identical to NOP and data-distinct. Used by the alias differential.
NOP_ALIASES = (NOP, N_OPCODES, 2 * N_OPCODES)

#: The only glue V0 admits. Named so a future glue is an explicit contract change, not a default.
GLUE_CONCAT = "concat.v0"


class CompositionError(ValueError):
    """Fail closed. A composition that cannot be reconstructed exactly is not a composition."""


# --------------------------------------------------------------------------- segments

class Segment(dict):
    """A segment document. dict so it serialises canonically with no custom encoder."""


def segment_from_instructions(words, label=None):
    """Build a segment from a flat word list. `label` is instrumentation only and is NOT hashed."""
    if not isinstance(words, list) or len(words) == 0 or len(words) % IW != 0:
        raise CompositionError("segment words must be a non-empty multiple of %d" % IW)
    for w in words:
        if not isinstance(w, int) or isinstance(w, bool) or not 0 <= w <= MASK32:
            raise CompositionError("segment words must be integers in [0, 2^32)")
    seg = Segment({"schema_version": SEGMENT_SCHEMA, "words": list(words)})
    if label is not None:
        # kept OUTSIDE the hashed document on purpose: a rename must not change identity
        seg.label = label
    return seg


def segment_id(seg):
    """Content identity of a segment: sha256 over the canonical document. Labels excluded."""
    if seg.get("schema_version") != SEGMENT_SCHEMA:
        raise CompositionError("segment schema mismatch")
    return hash_obj({"schema_version": SEGMENT_SCHEMA, "words": list(seg["words"])})


def segment_instructions(seg):
    return len(seg["words"]) // IW


# --------------------------------------------------------------------------- composition

def compose(components, envelope, glue=GLUE_CONCAT):
    """Order-sensitive concatenation of segments into one composition document.

    `components` is a list of (component_name, segment). The name is a LOCAL handle used to talk
    about a slot; identity comes from the segment's own content hash, so two slots holding the
    same bytes have the same segment_id and are distinguished only by their offset.

    `envelope` supplies the non-genome manifest fields (n_regs, tape_words, code_writable,
    persist, tick_budget, out_cap). The composition owns the genome and nothing else.
    """
    if glue != GLUE_CONCAT:
        raise CompositionError("unknown glue %r; V0 admits only %s" % (glue, GLUE_CONCAT))
    if not components:
        raise CompositionError("a composition needs at least one component")
    names = [n for n, _ in components]
    if len(set(names)) != len(names):
        raise CompositionError("component names must be unique within a composition")

    placed, words, off = [], [], 0
    for name, seg in components:
        sid = segment_id(seg)
        n_instr = segment_instructions(seg)
        placed.append({"component": name, "segment_id": sid,
                       "offset_instructions": off, "n_instructions": n_instr})
        words.extend(seg["words"])
        off += n_instr

    doc = {
        "schema_version": COMPOSITION_SCHEMA,
        "glue": glue,
        "components": placed,
        "envelope": _checked_envelope(envelope),
    }
    doc["manifest"] = _manifest_from(doc, words)
    doc["composition_id"] = composition_id(doc)
    return doc


def _checked_envelope(env):
    required = ("n_regs", "tape_words", "code_writable", "persist", "tick_budget", "out_cap")
    missing = [k for k in required if k not in env]
    if missing:
        raise CompositionError("envelope missing %s" % missing)
    extra = [k for k in env if k not in required]
    if extra:
        raise CompositionError("envelope has unknown fields %s" % extra)
    return {k: env[k] for k in required}


def _manifest_from(doc, words):
    m = dict(doc["envelope"])
    m["schema_version"] = MANIFEST_SCHEMA
    m["genome"] = list(words)
    try:
        validate_manifest(m)
    except ManifestError as e:
        raise CompositionError("composed genome is not a valid manifest: %s" % e)
    return m


def composition_id(doc):
    """Identity of the COMPOSITION (which parts, in which order, under which envelope).

    Distinct from the resulting player's organism_id, which is the hash of the emitted manifest.
    Two different compositions can emit the same manifest -- concatenation is not injective on
    component boundaries -- so both identities are recorded and neither substitutes for the other.
    """
    return hash_obj({"schema_version": COMPOSITION_SCHEMA,
                     "glue": doc["glue"],
                     "components": [{k: c[k] for k in
                                     ("component", "segment_id", "offset_instructions",
                                      "n_instructions")} for c in doc["components"]],
                     "envelope": doc["envelope"]})


def decompose(doc):
    """Recover each component's exact words from the composed manifest. Round-trip check."""
    g = doc["manifest"]["genome"]
    out = []
    for c in doc["components"]:
        lo = c["offset_instructions"] * IW
        hi = lo + c["n_instructions"] * IW
        seg = {"schema_version": SEGMENT_SCHEMA, "words": list(g[lo:hi])}
        if segment_id(seg) != c["segment_id"]:
            raise CompositionError(
                "component %r does not round-trip: composed bytes hash to %s, manifest records %s"
                % (c["component"], segment_id(seg)[:16], c["segment_id"][:16]))
        out.append((c["component"], seg))
    return out


# --------------------------------------------------------------------------- ablation

def ablate(doc, component, null_word=NOP):
    """Position-preserving removal of one component. Returns a new composition document.

    Only the opcode word of each instruction in the named component is rewritten; operands are
    preserved, length is preserved, and every other component's words are untouched.
    """
    if null_word % N_OPCODES != 0:
        raise CompositionError("null_word must decode to NOP (word mod N_OPCODES == 0)")
    target = [c for c in doc["components"] if c["component"] == component]
    if not target:
        raise CompositionError("no component named %r" % component)
    t = target[0]
    g = list(doc["manifest"]["genome"])
    lo = t["offset_instructions"] * IW
    for i in range(lo, lo + t["n_instructions"] * IW, IW):
        g[i] = null_word

    new = {
        "schema_version": COMPOSITION_SCHEMA,
        "glue": doc["glue"],
        "components": [dict(c) for c in doc["components"]],
        "envelope": dict(doc["envelope"]),
        "ablated": {"component": component, "null_word": null_word,
                    "parent_composition_id": doc["composition_id"]},
    }
    for c in new["components"]:
        if c["component"] == component:
            lo2 = c["offset_instructions"] * IW
            hi2 = lo2 + c["n_instructions"] * IW
            c["segment_id"] = segment_id({"schema_version": SEGMENT_SCHEMA,
                                          "words": list(g[lo2:hi2])})
            c["ablated"] = True
    new["manifest"] = _manifest_from(new, g)
    new["composition_id"] = composition_id(new)
    return new


def ablation_report(doc, component, cfg=DEFAULT_ENSEMBLE, probes=None):
    """Certify (or refuse to certify) that ablating `component` changed only that component.

    Structural checks are exact and unconditional. The alias differential is ensemble-relative
    and is reported as such: PASS means no data-channel dependence was DETECTED on these probes,
    never that none exists.
    """
    probes = build_probes(cfg) if probes is None else probes
    base_g = doc["manifest"]["genome"]
    t = [c for c in doc["components"] if c["component"] == component]
    if not t:
        raise CompositionError("no component named %r" % component)
    t = t[0]
    lo = t["offset_instructions"] * IW
    hi = lo + t["n_instructions"] * IW

    ab = ablate(doc, component)
    ab_g = ab["manifest"]["genome"]

    changed = [i for i in range(len(base_g)) if base_g[i] != ab_g[i]]
    outside = [i for i in changed if not (lo <= i < hi)]
    non_opcode = [i for i in changed if i % IW != 0]
    others_intact = all(
        base_g[c["offset_instructions"] * IW:
               c["offset_instructions"] * IW + c["n_instructions"] * IW] ==
        ab_g[c["offset_instructions"] * IW:
             c["offset_instructions"] * IW + c["n_instructions"] * IW]
        for c in doc["components"] if c["component"] != component)

    # NOP-alias differential
    hashes = []
    for w in NOP_ALIASES:
        v = ablate(doc, component, null_word=w)
        _, h = run_ensemble(v["manifest"], probes, cfg)
        hashes.append(h)
    alias_invariant = len(set(hashes)) == 1

    _, base_h = run_ensemble(doc["manifest"], probes, cfg)

    if outside or non_opcode or not others_intact:
        verdict = "STRUCTURALLY_INEXACT"
    elif not alias_invariant:
        verdict = "CONFOUNDED_BY_DATA_CHANNEL"
    else:
        verdict = "EXACT"

    return {
        "composition_id": doc["composition_id"],
        "ablated_component": component,
        "ablated_composition_id": ab["composition_id"],
        "ablated_organism_id": hash_obj(ab["manifest"]),
        "base_organism_id": hash_obj(doc["manifest"]),
        "structural": {
            "words_changed": len(changed),
            "instructions_in_component": t["n_instructions"],
            "changes_outside_declared_range": len(outside),
            "changes_to_operand_words": len(non_opcode),
            "other_components_byte_identical": others_intact,
            "length_preserved": len(base_g) == len(ab_g),
            "offsets_preserved": ([c["offset_instructions"] for c in doc["components"]] ==
                                  [c["offset_instructions"] for c in ab["components"]]),
            "envelope_preserved": doc["envelope"] == ab["envelope"],
        },
        "alias_differential": {
            "aliases": list(NOP_ALIASES),
            "distinct_transcripts": len(set(hashes)),
            "invariant": alias_invariant,
            "ensemble_identity": hash_obj({"cfg": cfg, "probes": probes}),
        },
        "transcript_changed_by_ablation": base_h != hashes[0],
        "verdict": verdict,
    }


def activation_evidence(doc, component, cfg=DEFAULT_ENSEMBLE, probes=None):
    """Did the component's instructions EXECUTE? Differential, no runtime instrumentation.

    If a component never executes, ablating it to NOP cannot change anything the runtime does,
    so the per-category op counts are identical. Any difference in those counts therefore proves
    execution. The converse has one declared exception: a component consisting only of
    halt_yield-class instructions is already NOP-class, so its ablation is a no-op for the counter
    and execution cannot be distinguished this way -- reported INDETERMINATE rather than guessed.
    """
    probes = build_probes(cfg) if probes is None else probes
    t = [c for c in doc["components"] if c["component"] == component]
    if not t:
        raise CompositionError("no component named %r" % component)
    t = t[0]
    lo = t["offset_instructions"] * IW
    g = doc["manifest"]["genome"]
    ops = [g[i] % N_OPCODES for i in range(lo, lo + t["n_instructions"] * IW, IW)]
    only_halt_yield = all(CATEGORY[o] == "halt_yield" for o in ops)

    def counts(manifest):
        m = Meter()
        run_ensemble(manifest, probes, cfg, m)
        return dict(sorted(m.by_category.items()))

    base = counts(doc["manifest"])
    abl = counts(ablate(doc, component)["manifest"])

    if only_halt_yield:
        verdict = "INDETERMINATE_COMPONENT_IS_ALREADY_NOP_CLASS"
    elif base != abl:
        verdict = "ACTIVATED"
    else:
        verdict = "NOT_ACTIVATED"
    return {"component": component, "verdict": verdict,
            "base_ops_by_category": base, "ablated_ops_by_category": abl,
            "component_opcode_classes": sorted({CATEGORY[o] for o in ops})}
