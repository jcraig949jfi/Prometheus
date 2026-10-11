# RED-TEAM REVIEW: E5-N FROZEN PRE-REGISTRATION (before any outcome)

Beta-03 (C-011). Reviewer: red-team subagent, 2026-10-08. Scope: beta03/windows/E5N_PREREG.md, engine/v2b/b03_e5.py,
beta03/FREEZE_E5N.json, beta03/runs/E5N/E5N_KNOWN.json, engine/w5p/{W5P_DESIGN.md, donor.py, promote.py, harness.py},
and the reused E1 assay (E1_PREREG.md + AMENDMENT A1, b03.py, b02.py). Read-only except this file. No donor and no walk
was run. The only computation was a scratch script (under 1 CPU-min) that calls the frozen `promote.instantiate`,
`tier3d.instantiate` and `Promoted.from_schema` on three inherited schemas.

State checked:
- beta03/runs/E1 does not exist.
- beta03/runs/E5N holds only E5N_KNOWN.json.
- PLAN_B.json has not been generated yet.

No E1 or E5 outcome exists, so every "amend before data" item below is still permissible.

## Scratch check: what a "depth-2" schema is in the first W5P generation (diagnostic)
Setup:
- Inherited S is promoted to P.
- The pass-2 derivation over folded bodies P(a1), P(a2) yields P(lgg(a1, a2)).
- The plain pass over (S[a1], S[a2]) yields S[lgg(a1, a2)] from the SAME class members.
- Both are kept: derive_schemas takes the union with no deduplication by expansion (promote.py:562-579).
- The design's own DEPENDENCY test documents this twin: `(first * (acc - {H}))` next to `(first * P1({H}))`.
- K5c shows it on exposed data: the derived `P(math.gcd(abs({H}), abs(v)))` alongside the selected plain
  `(acc - math.gcd(abs({H}), abs(v)))`.

| inherited S | P-twin (depth 2 when selected) | expansion == plain twin | W5P bodies of P-twin | W5 bodies of plain twin | P-only bodies (all outside G5) |
|---|---|---|---|---|---|
| (acc + {H}) | P(({H} * v)) | yes | 161 | 6 | 155 |
| (acc - {H}) | P(math.gcd(abs({H}), abs(v))) | yes | 161 | 6 | 155 |
| ({H} + v) | P((acc * {H})) | yes | 161 | 6 | 155 |

- `Promoted.from_schema(twin)` gives depth 2 in every case.
- The bare P({H}) instantiates to exactly S's 161 in-space bodies, with 0 extra. So D2 re-expressions are harmless
  duplicates.

Conclusions:
- In generation 1, a "depth-2" schema is a re-spelling of a W5 substitution-extension S[H := x]. Plain W5 already
  produces these: E1 review E1-1 found Beta-02 pairs 42->66 and 33->57, each acquiring 5 common families.
- The re-spelling adds 155 base-DSL bodies outside G5. These come from the W5P shape rule counting P as one node.
- Whether a depth-2 selection did anything beyond renaming therefore depends entirely on whether those P-only bodies
  produced the acquisition. The frozen rules never check this.

---

## Findings

### E5N-1 BLOCKER: SECOND-LEVEL certifies notational twins, so a YES can rest on renaming
- **Where:** b03_e5.py:124-132 (`_nontrivial_depth2`) and :163-165, plus prereg s5 SECOND-LEVEL and D4.
  - `dag_depth_selected >= 2` means exactly that "the selected schema contains a promoted node". donor.py:334-363
    registers the selected schema into out_reg, which gives 1 + max(dep depth).
  - The only promoted nodes available are those of `reg`, which come from the START library. So the dependency is
    indeed on an INHERITED primitive, and depth is not inflated by self-registration. That part is fine.
  - The defect is that nothing checks:
    - whether the depth-2 schema's expansion is simply the plain-pass twin S[H := x];
    - whether the pair's common-residual acquisition came from that schema's P-only bodies at all.
- **Failure scenarios:**
  1. Arm D selects P((({H} + v))) in pair n. Its acquired family is hit by one of the 6 bodies it shares with the
     plain twin. That plain twin is something arm B, under ordinary W5, can and does select (Beta-02 pair 42->66).
     SECOND-LEVEL still counts pair n.
  2. Arm D selects SCHEMA_ALL. Any depth-2 member counts (`selected_promoted` lists every member,
     donor.py:334-340), even if the hit came from a depth-1 member.
- **Consequence:** this violates the directive in s6 ("a promotion that only renames an existing expression is not a
  successful second-order mechanism") and in s8 ("depends computationally on a previously learned abstraction").
  The E6 sham swap (E5N-2) cannot catch it.
- **Action: amend before data.** A SECOND-LEVEL pair must satisfy all of the following. All are computable offline
  from recorded rows and walks; walk results carry `program`.
  - For >= 1 acquired common-residual family, the first qualified program's body lies in the depth-2 schema's W5P
    instantiation.
  - That body is not in `tier3d.instantiate(expansion)`, the plain twin.
  - That body is not in G5. This is an EXTEND gain in the sense of W5P_DESIGN s6(b), which the runner does not
    implement either.
  - Report, per pair and per arm, the REORDER/EXTEND decomposition, plus whether the selected depth-2 schema's
    expansion equals a pass-1 derived schema. This requires E5N-5's receipt.
  - The same attributed depth must feed the kill-criterion depth (E5N-6).

### E5N-2 MAJOR: the E6 positive-branch attack is not discriminating, and parts of it are not mechanical
- **Where:** prereg s6.
- **Problems:**
  - **The sham swap:** "replace the inherited primitive with arm F's primitive, re-walk, CONFIRMED iff acquisition
    drops in >= 2/3".
    - Almost any substitution changes every P-only body, so the hit body disappears and the attack is close to
      guaranteed to "confirm".
    - It tests whether this exact schema was needed, not whether the dependency was more than notational.
  - **"Keep base-grammar expressivity"** is vacuous at walk level. The walker evaluates the expansion, so inlining P
    gives byte-identical bodies and identical acquisition. The dependency exists only in PROPOSAL (the W5P shape and
    filler rule), so the expressivity-preserving disable must be defined there.
  - **"Drop" is undefined.** Which per-pair count, and against which reference?
  - **"Arm F's primitive"** is ambiguous when D's schema contains more than one inherited primitive (a SCHEMA_ALL
    donor library promotes several).
  - **The 8 unseen seeds (LIN 120+)** have no supply freeze, no donor mapping (the d+24 pairing ends at 119), and no
    decision rule.
  - **The directive's "scramble irrelevant artifact labels"** is missing.
- **Action: amend before data.**
  - **(a) INLINE control:** replace the depth-2 entry with its plain twin's W5 instantiation (`tier3d.instantiate`
    of the expansion), keeping the same start, cells and cap.
  - **(b) Sham swap,** with "drop" defined as a strictly lower common-residual count than arm D in that pair, and the
    primitive to replace chosen by a fixed rule (for example, lowest id among the inherited deps).
  - **DEPENDENCY_CONFIRMED** iff (a) AND (b) both drop in >= 2/3 of the SECOND-LEVEL pairs.
  - **Unseen-seed replication:** freeze the generator call and supply hash before running, fix the donor mapping
    (for example, block-A donors 72-79 -> recipients 120-127), and either give a rule or declare it descriptive.
  - **Label scramble:** P ids and entry names never enter walked bodies, and the keyed order depends only on body
    strings (fair.key). Either state that the scramble is vacuous by construction, or permute candidate names and
    check that the selection is unchanged.

### E5N-3 MAJOR: the sham arm is neither residual-clean nor guaranteed to be a sham
- **Where:** b03_e5.py:44-58 and :139-162, plus E1 b03.py:95-98.
- **Not residual-clean:**
  - The common residual excludes only families that the L_g11, L_I0 and L_P STARTS reach. The L_SHAM start is never
    in that construction.
  - Arm F's selected library is [new] + its sham start, so F is credited for families its INHERITED sham reaches.
  - That inflates F, which biases SHAM toward failure (toward NO).
  - It can also pass the positive control spuriously, since `best` ranges over all tags including F (:161-162). A NO
    is then emitted on an assay validated by inherited reach rather than acquisition.
- **Not guaranteed to be a sham:**
  - Panel key PA is `({H} + v)`, which is a schema g11 itself learns: 3 of 22 Beta-02 R8 L_g11 libraries.
  - Promoted ids are content-addressed, so in a pair where the seeded draw picks PA and the donor learned
    `({H} + v)`, arms D and F promote the SAME primitive.
  - The E6 swap would then replace P with itself.
- **Action: amend before data.**
  - Score SHAM, and F's acquisition, on common(n) minus the families START|L_SHAM reaches. The sham start walks
    already exist by stage design. Apply the same restricted set to D in the D-F test.
  - Exclude F from the PC best-arm maximum.
  - Make the seeded sham draw exclude panel keys whose normalised schema equals any template in that pair's L_g11 or
    L_I0. The draw stays deterministic and outcome-free.

### E5N-4 MAJOR: "NO" absorbs untestable and unattainable cases, and has no enabling known-positive
- **Where:** b03_e5.py:153-188, prereg s5 and s8.
- **P2 costs P1 power without being used:**
  - holm([P1, P2]) is computed, but only holm[0] (P1) enters the label. P2 is never used.
  - So P1 must reach p <= 0.025 unless P2 is smaller and itself rejected.
  - The exact sign-flip minimum one-sided p is 2^-k. P1 needs k >= 6 nonzero pairs, all positive (1/64).
  - Under the W01 tie pattern (k = 5, 1/4/15), P1 is UNATTAINABLE at Holm's first step: 1/32 = 0.031.
  - SHAM (one-sided 0.05) needs k >= 5.
- **YES is structurally impossible in some cases, yet NO is still emitted:**
  - when no D pair derives a non-bare depth-2 schema (CANDIDACY);
  - when common-residual slots are tiny.
- **There is no known-positive for "promotion enables acquisition" in this world.** The PC validates acquisition
  measurement, not the enabling channel, and E5-H is separate. NO is therefore interpretable only as "not shown
  here".
- **Action: amend before data.**
  - Make P1 the sole confirmatory test, with P2 descriptive. Otherwise give P2 a role in the label.
  - Emit NO with mandatory qualifiers:
    - `P1_attainable` (the attainable min p <= the applicable alpha);
    - `second_level_channel` = TESTED / UNTESTABLE_NO_DEPTH2_DERIVED;
    - `SHAM_attainable`.
  - **Report-only caveat:** state that a natural-world NO does not enter the directive s10 / Hestia retirement
    criterion until E5-H shows that second-level mechanisms are attainable and detectable.

### E5N-5 MAJOR: the pre-registered negative diagnosis needs receipts the runner does not record
- **Where:** harness.py:277-281 returns only selected_*, n_observed, n_derived, classes, meta_charges and w5p.
  donor_w5p computes `selection_table` (donor.py:348) but harness drops it. Only `derived_with_promoted` is kept, not
  the full derived list.
- **Consequence:**
  - Prereg s6 step 2, "derived, eligible and rejected by g11 -> SELECTION", cannot be computed from recorded rows.
  - Neither can the twin check in E5N-1.
  - The E1 recipients have these receipts (`_donor_full`, red-team E1-6), so the E5 arms would be asymmetrically
    diagnosable.
- **Action: amend before data.**
  - Add `selection_table` and `derived_schemas` (all, in promoted form) to the harness row. This is an output-only
    change.
  - Re-hash, and re-run K5a/K5b. The gate keys are unaffected.

### E5N-6 MAJOR: the Hestia kill criterion is not pre-registered mechanically, and notational twins would block it
- **Where:** prereg s5 and the Hestia dossier, lines 397-408.
- **What the dossier requires:** >= 20 paired unseen seeds; improvement not greater (one-sided p >= 0.05 or sum <= 0)
  AND depth 1 in >= 90% of seeds after two generations.
- **What E5N does:**
  - It needs only >= 18 pairs (inherited from E1).
  - It reports `dag_depth_selected_ge2_by_arm` but derives no KILL field.
  - It does not say which measure stands for "improvement" (common acquisition or own-start).
- **Why twins matter here:** from the scratch check, any selected substitution-extension P-twin counts as depth 2.
  Raw depth >= 2 in > 10% of pairs is therefore plausible without any second rung, and that alone would keep the
  kill criterion from firing.
- **Note:** "two generations" maps correctly here. The donors were W5 and are identical to W5P with a pristine start,
  so the recipient is generation 2. Hestia's "accept by MDL" is absent; report it as a deviation.
- **Action: amend before data.** Add `KILL_CRITERION_HESTIA` to E5N_RESULT, computed as:
  - `n_pairs >= 20`, otherwise NOT_ADJUDICABLE;
  - AND (P1 one-sided p >= 0.05 OR sum <= 0), with the measure named;
  - AND attributed depth (E5N-1) < 2 in >= 90% of D pairs.

### E5N-7 MINOR: the billing claim is true but the ledgers are partial
- **What holds** (b03_e5.py:105-121):
  - Transfer reach uses the unchanged `r7e._walk` -> `walk.first_qualified(FR.KLib(selected_entries))`.
  - Each candidate costs 1 charge.
  - Libraries hold expanded bodies only. P-form `schemas` in SCHEMA_ALL entries expand to nothing via
    fair.expand_schema, which is harmless.
  - Out-of-G5 bodies walk correctly (CONFORMANCE: 941 bodies).
  - So no macro is ever one free operation.
- **The gaps:**
  - The expanded and promoted execution ledgers cover the DONOR phase only. The transfer endpoint has no
    execution-size ledger.
  - An out-of-G5 depth-4 body costs the same 1 charge as a depth-1 body.
  - The 27x larger twin entries (161 vs 6 bodies) delay the G5 fallback. That is honest, but it biases D toward NO
    (a SEARCH_BUDGET-type confound).
- **Action: report-only caveat.** Optionally compute `Meter.walk_units` offline on the recorded transfer charges, as
  pure arithmetic with no walks.

### E5N-8 no action: the no-op gate is sound and unlikely to fail spuriously
- **Why it holds:**
  - `fair.pristine()` has no `schema` or `schemas`, so the registry is empty and form_map is empty.
  - Arms A and C both receive the L_P entries explicitly, so held = [] in both.
  - Lib keys are content hashes (b02._key), so C's walks dedupe against E1's.
  - Both row sets pass through the same JSON round-trip.
  - MeteredCell only proxies cost().
- **Caveats (report-only):**
  - The gate validates only the empty-registry path.
  - Because C is identical to A, P1 (D - C) is effectively "promotable L_g11 vs pristine-ordinary". The control for
    "any promoted prefix gets the shape relaxation" is SHAM (D - F), which is why E5N-3 matters.
  - P2 (D - B) is a representation-condition contrast (W5P_DESIGN s6(e)) that includes the shape-rule relaxation.
    Label it as such.

## Summary
| id | severity | action |
|---|---|---|
| E5N-1 | BLOCKER | amend before data: SECOND-LEVEL requires an acquisition hit on a P-only, out-of-G5 body of the depth-2 schema; report twin and REORDER/EXTEND |
| E5N-2 | MAJOR | amend before data: add the INLINE (plain-twin) control and define "drop", the primitive choice, the unseen-seed supply, mapping and rule, and the label scramble |
| E5N-3 | MAJOR | amend before data: score D-F on common minus L_SHAM-start reach; exclude F from PC; redraw shams equal to the pair's learned templates |
| E5N-4 | MAJOR | amend before data: make P1 the sole confirmatory test; NO carries attainability and channel qualifiers; caveat that a natural-world NO does not trigger retirement without E5-H |
| E5N-5 | MAJOR | amend before data: record selection_table and all derived schemas in the harness row; re-hash and re-run K5 |
| E5N-6 | MAJOR | amend before data: add a mechanical KILL_CRITERION_HESTIA (>= 20 pairs, named measure, attributed depth) |
| E5N-7 | MINOR | report-only caveat: the transfer endpoint has no execution-size ledger, and entry bloat delays the fallback |
| E5N-8 | none | no action: the gate is sound; caveat that C is identical to A and P2 is a representation-condition contrast |
