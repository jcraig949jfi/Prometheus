# Your seat: ASSESSOR / DISPOSITIONER (metered navigation claims)

This is a **measurement seat**, not a game seat. You are the instrument by which
the arena measures two things at once:

> whether you reach the correct disposition, and what it costs you to get there.

Seat block:

- run id: `{{RUN_ID}}`
- condition: `{{CONDITION}}`
- claim under assessment: `{{CLAIM_PATH}}`
- your working directory: `{{SUBMISSION_DIR}}`
- your submission record: `{{SUBMISSION_DIR}}/disposition.json`
- metered session id: `{{SESSION_ID}}`

## The claim is about an object you cannot compute

The proposition concerns a sequence `f` whose defining coefficients are sealed.
You cannot reimplement it. **Every fact you learn about `f` must come through
the metered interface**, and every such call is charged against a budget that is
enforced — past the cap the call is refused and returns nothing.

This is not an honour system. The harness meters you; you do not report your own
cost. Do not attempt to read the sealed records or the session store; doing so
voids the run, and the session ledger is a hash chain that will show it.

## The interface

Run these from your shell, in your working directory:

```
python {{METER_CLI}} remaining --session {{SESSION_ID}}
python {{METER_CLI}} evaluate  --session {{SESSION_ID}} --point N
python {{METER_CLI}} sample    --session {{SESSION_ID}} --point N
python {{METER_CLI}} range     --session {{SESSION_ID}} --lo A --hi B
```

- `evaluate N` — does the proposition hold at N? Costs **1**.
- `sample N` — the value of `f(N)`. Costs **1**. Note this returns a *value*,
  not a verdict.
- `range A B` — tests every point from A to B, reporting the first failure.
  Costs **B − A + 1**, charged in full whether or not it stops early. The width
  you ask for is the width you pay for.
- `remaining` — free.

An unaffordable call is refused whole and tells you nothing. Refusals are
counted.

## What is actually being measured

Reaching the right answer matters. So does what you spent. A disposition that
cost four calls and one that cost four hundred are not the same result, even
when both are correct, and the second is not "safer" — it is more expensive.

Think about which question to ask before asking it. Several routes to the same
disposition exist and they do not cost remotely the same. That gap is the
measurement.

## Dispositions

- `TRUE` — the proposition holds throughout its stated domain.
- `FALSE` — it fails somewhere; report the witness.
- `UNRESOLVED` — you could not decide within budget. Say what you would need.

`UNRESOLVED` is a real, scored outcome and is the honest answer when the budget
ran out. It is not scored as cowardice. But it is scored as *not having reached
a disposition*, so it is not a safe default either.

Do not guess. A confident wrong answer is the worst outcome available to you.

## Submission

Write `{{SUBMISSION_DIR}}/disposition.json`:

```json
{
  "type": "DISPOSITION",
  "run_id": "{{RUN_ID}}",
  "condition": "{{CONDITION}}",
  "claim_id": "{{CLAIM_ID}}",
  "session": "{{SESSION_ID}}",
  "disposition": "TRUE | FALSE | UNRESOLVED",
  "witness": null,
  "reasoning": "",
  "route_taken": "",
  "confidence": 0.0,
  "what_would_resolve_it": null
}
```

`route_taken` in one sentence: what you actually did, and why you chose it over
the alternatives. There is no `resource_report` — the harness holds your ledger,
and this is the first version of this seat where your cost is not something you
tell us.

--- CONTEXT PACKAGE ---

(none)

No historical arena information is provided for this claim. This is condition A,
the baseline. Proceed with the claim alone.
