---
name: GATE_VERDICT
type: signature
version: 1
version_timestamp: 2026-04-21T00:10:00Z
immutable: true
status: active
previous_version: null
precision:
  schema_form: tuple with three required fields + one optional
  enumerated_verdicts:
    - CLEAR    # passes the gate; no annotation needed
    - WARN     # passes with annotation; downstream consumers see the warning
    - BLOCK    # halts the operation; conductor override required to proceed
  field_dtypes:
    verdict: str ∈ {CLEAR, WARN, BLOCK}
    rationale: str (one sentence; what triggered the verdict)
    raised_by: symbol_id or pattern_id (e.g. Pattern_30@cb57f4afe, NULL_BSWCD@v2)
    override_token: str sha256 or null (null until/unless conductor override applied)
  override_protocol: |
    If verdict = BLOCK and conductor judges override warranted, the
    override is recorded as a hash of (verdict, rationale, raised_by,
    conductor_signature, justification_text) and stored alongside the
    SIGNATURE that would have been blocked. No silent bypass.
  rationale_max_length: 280 chars (prevent prose bloat per Pattern 17)
proposed_by: Harmonia_M2_sessionA@pending
promoted_commit: pending
references:
  - Pattern_30@cb57f4afe
  - NULL_BSWCD@v2
  - SIGNATURE@v2
redis_key: symbols:GATE_VERDICT:v1:def
implementation: null
---

## Definition

**Standardized three-valued filter output.** Every filter in the substrate (gen_06 Pattern 30/20/19 sweeps; gen_11 candidate-axis filter; gen_02 null-family discordance gate; future Pattern 21 automation) emits a verdict on each input. Without a standard, each filter would invent its own verdict vocabulary, and downstream consumers would handle them inconsistently. GATE_VERDICT@v1 pins the vocabulary so any filter result is mechanically interpretable.

**Canonical descriptor:**
```
GATE_VERDICT@v1[
    verdict ∈ {CLEAR, WARN, BLOCK},
    rationale: <one sentence, ≤ 280 chars>,
    raised_by: <Pattern_NN@c<commit> | SYMBOL@v<N>>,
    override_token: <sha256 or null>
]
```

**Verdict semantics:**

- **`CLEAR`** — passes the gate, no annotation. The downstream operation proceeds with no record beyond a count of CLEAR verdicts (kept for filter-calibration retrospectives).
- **`WARN`** — passes the gate, but the result lands with a `sweep_warnings` annotation pointing to this verdict. Consumers reading the resulting cell or SIGNATURE see the warning. Filter-calibration retrospectives sample WARNs to check false-positive rate.
- **`BLOCK`** — halts the operation. The result does NOT land in the tensor / specimen registry / DAG without a recorded conductor override. Filter-calibration samples BLOCKs to check false-positive rate (if too many BLOCKs are overridden, the filter is over-tight and needs tuning).

**Override protocol:**
A conductor override on BLOCK is recorded as `override_token = sha256(verdict + rationale + raised_by + conductor_signature + justification_text)`. The override travels with the resulting SIGNATURE and is queryable at audit time. Silent overrides are forbidden by convention; the substrate must surface every override for retrospective review.

## Derivation / show work

The vocabulary emerged from gen_06 spec drafting (2026-04-20). gen_06's Pattern 30 / 20 / 19 sweeps each emit `{verdict: CLEAR|WARN|BLOCK, rationale: <text>, raised_by: <pattern>}` per the spec body (`docs/prompts/gen_06_pattern_autosweeps.md` §Process). gen_11's filter spec independently adopted the same three-valued vocabulary (`docs/prompts/gen_11_coordinate_invention.md` §Module 3).

Two specs converging on the same vocabulary independently is the textbook case for symbol promotion — without canonicalization, the third filter to be specified will drift (`{pass, flag, halt}` or `{ok, warning, error}` or any other near-synonym), and downstream consumers will have to handle the variants.

**Anchor case (worked example, prospective):** when gen_06 ships and runs the retrospective sweep on existing +1/+2 cells, the historical F043 SIGNATURE will produce:
```
GATE_VERDICT@v1[
    verdict=BLOCK,
    rationale="log_A contains -log_Sha as a definitional term (BSD identity rearrangement, Pattern 30 Level 3)",
    raised_by=Pattern_30@cb57f4afe,
    override_token=null
]
```

That's the correct gate firing on the canonical Pattern 30 anchor. Any sweep implementation that produces this verdict on F043's SIGNATURE is correctly calibrated.

## References

**Internal:**
- Pattern_30@cb57f4afe (the most aggressive consumer — every Pattern 30 sweep emits a GATE_VERDICT)
- NULL_BSWCD@v2 (a null verdict at z < threshold can be expressed as a CLEAR, but typically null-test verdicts use z-scores directly; GATE_VERDICT applies to *filter* gates, not measurement gates)
- SIGNATURE@v2 (when a SIGNATURE carries `sweep_warnings`, each entry is a GATE_VERDICT; when a SIGNATURE was blocked-then-overridden, the override_token lives in SIGNATURE provenance)

**Adjacent (consumers — specs):**
- `docs/prompts/gen_06_pattern_autosweeps.md` — three sweeps emit GATE_VERDICT
- `docs/prompts/gen_11_coordinate_invention.md` — three filter gates emit GATE_VERDICT
- Future `Pattern_21` discordance automation — null-family discordance > 10× emits GATE_VERDICT[WARN]

## Data / implementation

```python
from typing import Literal, Optional

VerdictType = Literal['CLEAR', 'WARN', 'BLOCK']

def make_verdict(
    verdict: VerdictType,
    rationale: str,
    raised_by: str,                       # 'Pattern_NN@c<sha>' or 'SYMBOL@v<N>'
    override_token: Optional[str] = None
) -> dict:
    if verdict not in {'CLEAR', 'WARN', 'BLOCK'}:
        raise ValueError(f"verdict must be CLEAR | WARN | BLOCK, got {verdict!r}")
    if len(rationale) > 280:
        raise ValueError("rationale exceeds 280 chars (Pattern 17 anti-bloat constraint)")
    return {
        'verdict': verdict,
        'rationale': rationale,
        'raised_by': raised_by,
        'override_token': override_token,
    }

def record_override(verdict_dict, conductor_signature, justification):
    import hashlib
    token = hashlib.sha256(
        f"{verdict_dict['verdict']}|{verdict_dict['rationale']}|"
        f"{verdict_dict['raised_by']}|{conductor_signature}|{justification}".encode()
    ).hexdigest()
    new = dict(verdict_dict)
    new['override_token'] = token
    return new
```

## Usage

**In a filter implementation (gen_06 Pattern 30 sweep):**
```python
def pattern_30_sweep(signature):
    coupling = dag.coupling_severity(signature.X, signature.Y)
    if coupling >= 3:
        return make_verdict('BLOCK',
                            f"X reduces to Y under DAG path of severity {coupling}",
                            raised_by='Pattern_30@cb57f4afe')
    if coupling == 2:
        return make_verdict('BLOCK',
                            "X shares a non-trivial factor with Y",
                            raised_by='Pattern_30@cb57f4afe')
    if coupling == 1:
        return make_verdict('WARN',
                            "X has weak algebraic dependence on Y",
                            raised_by='Pattern_30@cb57f4afe')
    return make_verdict('CLEAR', "no algebraic coupling detected",
                        raised_by='Pattern_30@cb57f4afe')
```

**In a SIGNATURE that landed with WARN annotations:**
```json
{
  "feature_id": "F<id>",
  ...
  "sweep_warnings": [
    {
      "verdict": "WARN",
      "rationale": "stratifier conductor_decile may not be claim-class-appropriate; suggest rank_bin",
      "raised_by": "NULL_BSWCD@v2",
      "override_token": null
    }
  ]
}
```

## Version history

- **v1** 2026-04-21T00:10:00Z — first canonicalization. Three verdicts pinned: CLEAR, WARN, BLOCK. Override protocol mandates recorded hash; silent bypass forbidden by convention. Field schema pinned (verdict, rationale, raised_by, override_token); rationale capped at 280 chars to prevent Pattern 17 bloat. Adding a verdict (e.g., a future RETRACT for post-promotion BLOCKs) is a v2 bump.
