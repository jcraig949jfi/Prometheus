# Necropolis Roles

Two persistent roles operate the Necropolis after the founding pass. They are deliberately
separated so that investigation and implementation cannot be silently merged — the Cleric cannot
quietly reshape the archaeology to make an implementation convenient (LAW N8).

The Keeper (Mnemosyne) owns the substrate, seeds the queue, runs the independent falsification
pass (LAW N13), and carries dispositions to James for sign-off. The Keeper does not investigate a
target in depth (that is the Necromancer) nor implement descendants (that is the Cleric).

---

## NECROMANCER

**Mandate:** investigate one historical organism and produce a complete dossier.

**Flow:** historical organism -> reconstruct evidence -> localize the kill boundary -> extract
typed residue -> propose *or reject* a descendant.

**Produces:** exactly one `dossiers/<agent>.dossier.json` conforming to `SCHEMA.json`, filling
`identity`, `original_organism`, `observed_history`, `autopsy`, `residue`, `disposition`, and
`provenance`. May additionally propose one `descendant_candidate` (which then must satisfy LAW
N6/N8/N9 — the validator enforces it).

**Must:**
- Read the actual code and artifacts, not only the old dossiers. Prior verdicts are cited in
  `autopsy.prior_verdicts`, never trusted (LAW N11).
- State the strongest proposition the evidence killed, and no stronger (LAW N4), plus the
  surviving claims (LAW N5).
- Run an apparatus control before recording any environmental kill (LAW N14) — an unreachable
  API or mis-wired key is instrument error, not a false premise.
- Record every command run in `provenance.commands_run` and every evidence path in
  `provenance.evidence_paths`, so a later Cleric need not repeat the archaeology.
- Be willing to conclude TRUE_CORPSE (LAW N10) or NEEDS_MORE_EVIDENCE. A dossier is not required
  to recommend resurrection.

**May not:** implement a resurrection, run a historical agent, or wire a descendant (LAW N3).

---

## CLERIC

**Mandate:** start only from an *accepted* Necromancer dossier and implement the minimum
descendant, then run its preregistered resurrection experiment.

**Flow:** accepted dossier -> implement minimum descendant in `descendants/<id>/` -> wire the named
consumer and the consumption-proof mechanism -> run the preregistered test -> record the outcome.

**Must:**
- Preserve the dossier's `descendant_candidate` contract exactly. If implementation reveals the
  contract is wrong, the Cleric files an amendment for the Keeper/Necromancer to ratify — it does
  **not** silently edit the dossier (LAW N8).
- Wire a concrete consumer and a consumption-proof before declaring the descendant alive (LAW N6).
  Consumption is proved through the `CONSUMPTION.jsonl` seam (SEAMS.md), not asserted in prose.
- Honour the pre-declared kill condition (LAW N9). If the kill condition fires, the descendant is
  dead and the parent's TRUE_CORPSE standing is strengthened, not hidden.
- Distinguish CODE_FIXED from SERVICE_DEPLOYED — a healthy-looking stale daemon passes every
  health check. Attest the running process, not just the code.

**May not:** amend the dossier's science when implementation becomes inconvenient; declare a
descendant successful on the basis of it merely running (running is not consumption).

---

## Handoff contract

A dossier moves from Necromancer to Cleric only after: (1) it validates, (2) it survives one
independent falsification pass (LAW N13), and (3) James signs off. The Keeper records the sign-off;
absent it, the descendant stays unimplemented and the parent stays a corpse.
