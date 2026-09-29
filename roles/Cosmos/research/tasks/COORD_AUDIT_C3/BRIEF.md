# C3 coordinate-layer audit -- Fabric review Task (moved from Harmonia; operator 2026-09-29)

Status: PREPARED, NOT DISPATCHED. Dispatch waits on one operator confirmation (see s6).
Thread thr-32389b1e7abb (T-C3), campaign C3, experiment C3-S1 coordinate layer. MWO-0001 s4/s5.

## 1. Authority and scope
Operator 2026-09-29: the coordinate-layer audit is MOVED, not dropped. It runs as a public-side Fabric
review Task, with no D information in scope, on fresh independent replicas pinned to Cosmos's review
SHA. It is not assigned to Harmonia, who adjudicates D. It must return before the C3 freeze.
Earlier authority for the audit itself: operator 2026-09-23 ("audit whether those coordinates encode
hidden implementation knowledge").

IN SCOPE (the bundle; nothing else): the visible C3 substrate families
(prometheus/cosmos/c3/substrates.py), the coordinate construction and normalisation
(prometheus/cosmos/c3/geometry.py, prometheus/cosmos/c3/maps.py), the per-world coordinate values
with certificate labels (roles/Cosmos/c3/runs/maps_s1/MAPS.json), and the PUBLIC certificate
(task/system/probe/certify/calib/gate.py + S1_PREREG_P1P2_GATE.md, already on main).
OUT OF SCOPE (stays withheld until the freeze): the candidate law and threshold (law.py, LAW.json,
S1_PREREG_LAW.md, S1_RESULT.md), failure regions and attacks (attack.py, ATTACK.json), substitution
attacks (substitution*.py, S1_PREREG_SUBSTITUTION.md, SUBST_*.json), the Session 1 review packet, the
operator notes, and ANY holdout D or D2 material.
The reviewer is NOT asked whether the law is true.

## 2. Questions (per candidate coordinate; verdict ADMIT / REVISE / WITHDRAW, with evidence)
Q1 Substrate identity leak: beyond what the certificate labels explain, does the coordinate's value
   carry family identity? Test PER FAMILY, never pooled (C0: a pooled test hid opposite-signed family
   offsets).
Q2 Metamorphic invariance: is the coordinate unchanged under description-only changes (relabel
   units, reparameterise time, rename or permute state components, relocate)?
Q3 Implementation knowledge: does computing it require knowing a substrate's internals, rather than
   only what the public System interface exposes (init / noise / step / readout_features / full_state)?
Q4 Definition rung (Artemis R-14, which Cosmos reproduced for C0): does a zero-parameter quantity
   written directly from the P1/P2 certificate definition already reproduce the certificate labels as
   well as the coordinates do? If it does, a "law" over these coordinates restates the certificate.
Q5 Normalisation: can any normalisation constant be traced to evaluation rows (threshold leakage),
   or does any constant differ per family (hidden tuning freedom)?
Q6 Prose/code agreement: does geometry.py compute what its docstring and the maps say?

## 3. Execution design (MWO-0001 s5: fresh replicas; the principal does not pick reviewers)
- Task R (x2 replicas, --cap research.repo_readonly, executor claude): independent reading review of
  the bundle at the review SHA. Answer Q1-Q6 per coordinate, citing file:line and MAPS.json rows.
  The claude executor cannot run python (fabric README s4, D3), so R is a READING lens and is labelled
  as one.
- Task X (x1, executor script, --cap python.numpy on worker.ubu001.sci): the executable probes for
  Q1 (per-family residual identity test), Q2 (metamorphic battery on the substrates) and Q4 (definition
  rung vs coordinates), from a probe script committed in the bundle. DISCLOSED LIMIT: Cosmos wrote X's
  code, so X is Cosmos's instrumentation, and the R replicas are asked to audit X's code and output too.
- Verdict file per replica: out/COORD_AUDIT_<replica>.md with one line per finding:
  `question | coordinate | severity (BLOCKING / REPAIR / NOTE) | evidence | proposed repair`. Overall
  verdict: ADMIT_ALL / REVISE / REJECT.

## 4. What Cosmos does with the verdicts
Everything happens before the freeze and only on visible (Z1) material. Each WITHDRAW removes the
coordinate from the frozen law's vocabulary. REVISE: repair and re-audit; the old state is preserved.
REJECT: stop before D and report to the operator. A disputed finding goes to the operator with both
sides; Cosmos does not dismiss it. All verdicts go into roles/Cosmos/research/reviews/ and are cited
by the C3 freeze in FREEZES.md.

## 5. Bundle (file -> LF sha256 at the withheld commit; filled at dispatch time from e73e5eb26)
To be listed in BUNDLE_MANIFEST.md at the review SHA. Every file must hash-match the withheld branch.
This makes the early publication checkable against the 0ecafed1 commitment when the whole branch is
published.

## 6. Why dispatch is held (one confirmation needed)
Fabric workers check out base_sha from origin (fabric README s4). The bundle therefore has to be pushed
to origin, which PUBLISHES the coordinate layer before the C3 freeze. The publication is irreversible
and custody-relevant (MWO-0001 s7 item 2). D2's hidden set is already cryptographically committed
(spec_id e2d3213b..., commitment 69f91153...), so publication cannot change what D2 contains. Two
costs remain: the future E author loses blindness to the coordinates, and any D2 v3 author repair
would be made with the coordinates in view. Cosmos asks the operator to confirm the publication of
the s1 IN-SCOPE bundle only. Until then, nothing is pushed or submitted.

## 7. Submit commands (for after confirmation; <SHA> = the review commit on origin)
python -m fabric submit --as Cosmos --cap research.repo_readonly --executor claude --base <SHA> \
  --prompt-file roles/Cosmos/research/tasks/COORD_AUDIT_C3/REVIEWER_PROMPT.md --replicas 2 \
  --thread thr-32389b1e7abb --campaign C3 --experiment C3-S1-COORD --title "C3 coordinate-layer audit (R)" \
  --key cosmos-c3-coord-audit-R-<SHA>
python -m fabric submit --as Cosmos --cap python.numpy --executor script --base <SHA> \
  --param module=prometheus.cosmos.c3.coord_audit_probe --thread thr-32389b1e7abb --campaign C3 \
  --experiment C3-S1-COORD --title "C3 coordinate-layer audit (X probes)" --key cosmos-c3-coord-audit-X-<SHA>
