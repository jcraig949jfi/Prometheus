THEO-REQ-004  (to Vivarium, kind contract + result validator; cc Herakles,
               evca library)  issued 2026-09-14, round 2

attempted experiment:
    Step-B cell exp/W599/P_d40 (spec_hash sha256:09fe40008f014..., row
    theo:...:rou1, phase round2): a single-density ensemble on the
    majority-0 side where the rule fails ~65% of ICs.
currently representable:
    Executes. The result carries misclassified_ic / witness bounded at 64
    entries plus witness_truncated.
blocked operation:
    (1) DEFECT: one repeat produced EXACTLY 64 wrong of 100. The library
        sets witness_truncated = (wrong.size > 64) = False, and the
        Vivarium result validator refused the row: "misclassified_ic is
        exactly at its declared maximum 64 and the executor declared no
        truncation". The whole cell FAILED (EXECUTOR_ERROR) after 6 of 8
        repeats. A complete vector of length 64 is legal by the library's
        definition; the validator's boundary is off by one. Retried at
        n_ic=50 x 16 repeats (ADAPTIVE_RECORD_02) as a workaround.
    (2) CAPABILITY: the per-IC realised density and per-IC success are not
        in the result at all above 64 failures; the signed-margin response
        curve (THEO-SPEC-001) therefore has to be re-derived OFFLINE by
        re-executing every fossil's ICs (validated bit-exact, but it is a
        second execution, not the fossil).
minimal missing capability:
    (1) the validator accepts a witness of length exactly 64 with
        witness_truncated False; (2) a per-IC success BITMASK (n_ic bits,
        hex) and per-IC one-count vector in the result -- or, at minimum,
        the correct-mask digest is already there, so the bitmask itself is
        the only addition.
evidence:
    ledgers/rows.jsonl row theo:*:rou1 error text; herakles/evca/core.py
    classify(): witness_truncated = wrong.size > witness_limit;
    round2/per_ic_validation.json (59/59 offline re-derivations match).
smallest interface change believed sufficient:
    (1) `>=` -> `>` in the bound check (or the library sets truncated at
    == 64; either owner decides, the two must agree); (2) result_schema
    field `success_mask_hex: string` on ca_density_v0.
downstream experiment unlocked:
    Margin-response phenotypes for every historical and bench fossil
    without re-execution; one-class-collapse detection as a standing
    Vivarium/Archaeon check rather than a Theophrastus offline pass.
