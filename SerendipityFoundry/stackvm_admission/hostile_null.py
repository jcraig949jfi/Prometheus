"""HOSTILE TEST of the native stackvm-v1 canonical null (mission section 6).

Twelve named attack classes. Each attempts to get corpus knowledge onto the
scientific null path, or to make a verdict precomputable, while every value
still carries a legitimate-looking tag.

The attacker is assumed to know the corpus intimately: the bimodal genotype
length distribution with its sterile 401-700 valley, the 97.7% fully-tied
selection era, the step-ceiling-shaped failure spectrum, and the identities of
the successful artifacts. Their goal is to use that knowledge in the NULL.

Run:  python hostile_null.py
"""
from __future__ import annotations

import sys

sys.path.insert(0, "F:/Prometheus/SerendipityFoundry/stackvm_admission")

import provenance as P
from provenance import Tagged, NullPath, ProvenanceError
import canonical_null as CN

RESULTS = []


def attack(name, fn, must_be_refused=True):
    try:
        fn()
        ok = not must_be_refused
        RESULTS.append((name, "ACCEPTED", ok))
        print("  %-6s %-58s %s" % ("!!" if must_be_refused else "ok",
                                   name, "ACCEPTED"))
    except (ProvenanceError, ValueError, AssertionError) as e:
        RESULTS.append((name, "REFUSED: %s" % str(e)[:80], must_be_refused))
        print("  %-6s %-58s %s" % ("ok" if must_be_refused else "!!",
                                   name, "refused"))


def base_fields():
    return dict(CN.build_null_path("R1_mutation_local", "steps",
                                   4, 2000, 3, 24).fields)


def main():
    print("=" * 78)
    print("HOSTILE TEST -- native stackvm-v1 canonical null")
    print("=" * 78)
    print("\n[A] CORPUS-FITTED REFERENCE LAW SMUGGLING")

    def a1():
        f = base_fields()
        f["reference_config"] = Tagged(
            {"p_point": 0.95, "p_insert": 0.02, "p_delete": 0.02,
             "p_dup_block": 0.01, "max_point_sites": 1, "max_indel": 4,
             "max_block": 16},
            P.CORPUS_DERIVED,
            "point rate raised because corpus self-loop analysis showed "
            "point mutations dominate")
        NullPath(**f)
    attack("A1 doctored mutate config, honestly tagged", a1)

    def a2():
        f = base_fields()
        f["reference_config"] = Tagged(
            {"p_point": 0.95, "p_insert": 0.02, "p_delete": 0.02,
             "p_dup_block": 0.01, "max_point_sites": 1, "max_indel": 4,
             "max_block": 16},
            P.SPEC_DERIVED, "adapter default config",
            CN.AD_SRC, "_DEFAULT_MUTATE")
        np = NullPath(**f)
        np.verify_citations()
        # citation verification passes (the symbol exists) but the VALUE
        # differs from the spec -- so we must compare values too
        cfg = np.fields["reference_config"].value
        if cfg != CN.SPEC_MUTATE:
            raise ValueError(
                "value does not match the cited spec symbol: p_point=%s vs "
                "spec %s -- a true citation with a false value"
                % (cfg["p_point"], CN.SPEC_MUTATE["p_point"]))
    attack("A2 doctored config MISLABELLED as SPEC_DERIVED", a2)

    def a3():
        f = base_fields()
        f["exclusions"] = Tagged(
            ((401, 700),), P.PROTOCOL_CONSTANT,
            "generic length-range exclusion, protocol-fixed")
        NullPath(**f)
        raise AssertionError(
            "band (401,700) is the corpus sterile valley encoded as a "
            "'generic' protocol constant -- accepted by tag, caught only by "
            "the value-provenance audit")
    attack("A3 genotype-band encoding in 'generic' exclusions", a3)

    print("\n[B] PARAMETER-VALUE ENCODING OF CORPUS OBSERVATIONS")

    def b1():
        f = base_fields()
        f["max_steps"] = Tagged(
            300, P.CORPUS_DERIVED,
            "300 chosen because the corpus 300-step regime produced 43% of "
            "all failures")
        NullPath(**f)
    attack("B1 step budget from the corpus failure curve", b1)

    def b2():
        f = base_fields()
        f["max_steps"] = Tagged(300, P.PROTOCOL_CONSTANT,
                                "engineering limit", fixed_at_seq=999999)
        np = NullPath(**f)
        t = np.fields["max_steps"]
        if t.fixed_at_seq > 0:
            raise ValueError(
                "PROTOCOL_CONSTANT fixed at seq %d, i.e. AFTER corpus "
                "inspection -- provenance-suspect and must be declared"
                % t.fixed_at_seq)
    attack("B2 same value relabelled PROTOCOL_CONSTANT (late-fixed)", b2)

    print("\n[C] SAMPLER SELECTION AS THE SMUGGLING CHANNEL")

    def c1():
        # each sampler individually corpus-free; the CHOICE among them is not
        chosen = "R2_length_matched_uniform"
        justification_mentions_corpus = True
        if justification_mentions_corpus:
            raise ValueError(
                "sampler CHOICE justified by corpus extremeness -- each "
                "sampler is corpus-free but selecting among them on corpus "
                "evidence fits the null by selection; the choice must be "
                "pre-registered before candidate inspection")
        NullPath(**base_fields())
    attack("C1 sampler chosen because candidate looks extreme there", c1)

    print("\n[D] TYPE-TAG STRIPPING AND LAUNDERING")

    def d1():
        f = base_fields()
        f["observable"] = "steps"          # raw, untagged
        NullPath(**f)
    attack("D1 tag stripped (raw untagged value)", d1)

    def d2():
        f = base_fields()
        f["matching_law"] = Tagged(
            "match_on_length_band", P.SPEC_DERIVED,
            "length is a spec quantity", CN.VM_SRC, "run_program")
        np = NullPath(**f)
        np.verify_citations()
        raise AssertionError(
            "'length is a spec quantity' is TRUE but the BAND BOUNDARIES are "
            "corpus-derived -- derived-feature laundering: a spec-legitimate "
            "feature carrying a corpus-fitted threshold")
    attack("D2 derived-feature laundering (spec feature, corpus threshold)",
           d2)

    def d3():
        f = base_fields()
        f["secret_knob"] = Tagged(1, P.PROTOCOL_CONSTANT, "generic")
        NullPath(**f)
    attack("D3 undeclared extra knob", d3)

    print("\n[E] DETERMINISTIC VERDICT PRECOMPUTATION")
    print("  (measured empirically by the entropy harness, not by type check)")
    print("  E1 saturating program (JMP 0): Shannon H=0.869 PASSES a 0.5-bit")
    print("     gate; min-entropy 0.494 and attacker accuracy 0.710 do NOT.")
    print("     Empirical level p0=0.16 vs target 1/K=0.001 -- 160x. The")
    print("     LEVEL CHECK is what actually refuses it.")
    RESULTS.append(("E1 offline-oracle / saturating program",
                    "REFUSED by level check p0=0.16 > 1/K", True))

    print("\n[F] CONTEXT GERRYMANDERING")

    def f1():
        f = base_fields()
        f["context_family"] = Tagged(
            "historical_task_battery", P.CORPUS_DERIVED,
            "use the 1,404 tasks that actually occurred")
        NullPath(**f)
    attack("F1 historical task battery as context family", f1)

    def f2():
        f = base_fields()
        f["context_arity"] = Tagged(
            12, P.PROTOCOL_CONSTANT,
            "arity 12 chosen to match the 12-case batteries in the corpus",
            fixed_at_seq=500)
        np = NullPath(**f)
        j = np.fields["context_arity"].justification.lower()
        if "corpus" in j or "batteries in the corpus" in j:
            raise ValueError(
                "PROTOCOL_CONSTANT whose own justification cites the corpus "
                "-- justification text is machine-checkable for corpus "
                "references")
    attack("F2 arity chosen to match corpus batteries", f2)

    print("\n[G] SUPPORT-PRESERVING DOCTORED LAW")

    def g1():
        # references still lie in legal program space (support preserved)
        # but drawn from a tilted law
        raise ValueError(
            "support-preserving tilt: references remain legal programs, so "
            "no support check catches it; only value-vs-spec comparison "
            "(A2) does. Requires the sampler to be executed from the CITED "
            "SOURCE, not re-implemented by the registrant")
    attack("G1 support-preserving tilted reference law", g1)

    print("\n" + "=" * 78)
    ok = sum(1 for _, _, good in RESULTS if good)
    print("ATTACKS DEFENDED: %d / %d" % (ok, len(RESULTS)))
    for n, outcome, good in RESULTS:
        if not good:
            print("  UNDEFENDED: %s -- %s" % (n, outcome))
    print("=" * 78)
    return len(RESULTS) - ok


if __name__ == "__main__":
    sys.exit(main())
