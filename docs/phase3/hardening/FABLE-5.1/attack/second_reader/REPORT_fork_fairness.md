# Report of the second reader's fork: fairness to the sources

Verbatim, as it was returned.

---

Fork report: fairness of document 1 (and statements about B, C, O in documents 2, 3 and the README) against the sources. Every item below was checked by opening the source at the line cited. Nothing was written; one read-only run recomputed the run-2 medians from the receipt.

Abbreviations: D1/D2/D3 = documents 1/2/3; RM = `00_README.md` of the package. B-rep = `reports\Wind tunnel charter review.md`; B-val = `VALIDATION.md`. C01/C02/C03/C05/C06 = the `chatgpt56_0x` files. O03/O04 = the two O files. A-R1/A-R2/A-R3 = RESPONSE_1/2/3; A-CF = `counterfeit\README.md`.

## Defects

**BLOCKER**

1. **D1 L81-83, section 1 "checked by" row.** B's cell reads "its author's source anchors; a documentary consistency check", beside A's "three adversarial readers".
   - B-val L75-78: "## Adversarial review and adjudication ... A read-only validation subagent examined the report against sources 01/02/06. It reported ... seven editorial concerns." B-val L94: "This is a documentary adversarial pass".
   - B is shown as never attacked. This is by omission; downgrade to MAJOR if omission does not count as "said to lack".
   - Fix: add "one read-only adversarial pass, seven concerns adjudicated" to B's cell.

2. **D1 L389-392, section 8 "FROM BOTH".** C is said to have left out, from both reviews, (a) a gate refusing a verdict quoted without its setting and (b) a rule that an analyst's filter on worlds is registered. Neither review contains either.
   - A-R1 L991-993 only says "REPORT THE SETTING WITH THE RESULT". B-rep L169-170 only says "Preserve its full conditioning variables." C carries both.
   - For (b), A has a finding about its own run (A-R1 L842-846), not a rule. B-rep L72-76 names "repeated analyst selection" and prescribes custody, which C carries (C02 L56, L81).
   - D2 L323-325 itself marks SELECTION "(No gate yet.)", so both are new in this package.
   - Fix: delete the "FROM BOTH" block or retitle it "NEW IN MY VERSION".

**MAJOR**

3. **D3 L461-465.** "B's experiment 5: build the cargo compiler and the genuine learned updater ... count false promotions and false rejections under B's clamp and swap. Both B's plan and the package's plan already hold it."
   - C's plan holds only the cargo half: C05 L42 "Expand R8 with nested-compiler cargo and flattening attacks"; C05 L54 "Attempt strong-recursion qualification only if a genuine positive has been constructed."
   - No build of the updater, no false-rejection count, no clamp anywhere in C (grep "clamp", "mediat": no hits). It also contradicts D1 L381-383, which lists the clamp and the false-rejection count as left out by C.
   - Fix: "B's plan holds it; the package's plan holds only the cargo and flattening attacks."

4. **D1 L283-290 (also D1 L291-292, L523-524 "from B, A"; D2 L250-252; RM L41-42).** "Its control for cargo is [the fixed-updater sentence]. That is an exclusion against a registered class of fixed updaters ... B's own unresolved question 1 concedes the result may be relative to it".
   - The quoted sentence is one of four in item 4 of a six-item repair list (B-rep L473-494). It is hedged "where feasible" and speaks of "controls", not a class or an exclusion.
   - Question 1 in full, B-rep L686-690: "Is improved learner construction causally identifiable beyond a useful re-description of ordinary meta-learning? The distinction must survive cargo controls, compiler flattening and legitimate conventional positives. If only an operational intervention-relative notion survives, adopt it openly and drop stronger ontological language."
   - It says intervention-relative, not class-relative. It is a conditional open question, not a concession. "Cargo controls" is plural.
   - The nearest real support is uncited: B-rep L610 "A clean fixture result qualifies only the tested attack classes."
   - Fix: cite L610, replace "concedes ... relative to it" with B's own words, say "one of B's cargo controls", and mark "name the class you exclude" as this author's reading (section 11 row 6: "new, after B and A").

5. **D1 L204-208, section 4 item 2.** "B has exact truth in W0 and says of richer worlds: 'A few strong baselines do not bound all cheap policies.' ... A adds one tool that is still exact outside W0".
   - The quoted sentence is from B's W2 paragraph (B-rep L387-391). B's W1 family has exact cases: B-rep L359-361 "small exactly solvable cases and larger related cases".
   - D1's own L349 says "exact class values A and B".
   - Fix: "B has exact truth in W0 and small exactly solvable cases in W1; for W2 it narrows the claim. A adds the random key, exact in a world of any richness."

6. **D1 L214-216, section 4 item 4.** "B asks for native positive witnesses in W0."
   - B also requires them beyond W0. B-rep L287-289: "Before a search-based null receives a meaningful ceiling: - Use several structurally distinct witnesses". B-rep L387-388: "Maintain matched positive feasibility checks at admitted settings". B-rep L696-698: "matched feasibility witnesses must separate these explanations before a new engine or a larger world is authorized."
   - Fix: state those three, then what A adds (one entry rule per physics, a matched impostor, door two).

7. **D1 L228-229, section 4 item 7.** "Seven of A's nine carry a quantity and a day."
   - In A-R1 L1294-1337, seven carry a quantity (1, 2, 3, 4, 5, 7, 8). Only two carry a day (1 "By day 45", 7 "By day 90").
   - D1's own L107 says "seven carry a number".
   - Fix: "seven carry a quantity; two of them a day."

8. **D1 L141-142 and RM L43-44.** "Three (5, 6 and 8) are rules ... that nothing yet tests" and "I take nine into what runs or into the registration".
   - Point 12 (D1 L193-194, "TAKEN: native and host cost side by side, no scalar") has no code. Grep of `harness/**/*.py` for host, scalar, cost: `resources` is a presence-only field (`registration.py` L14) and no gate refuses a scalar.
   - So four rules are untested (5, 6, 8, 12) and eight are taken.
   - Point 4's "TAKEN" is in G8 and G9.sham with hard-coded margins (`torture.py` L18 `MARGIN = 0.1`; `audits.py` L111 `margin=0.25`). B's own use, observer equivalence with a registered margin (B-rep L119-122), is "specified and not built" (D3 L175-176).
   - Fix: "four (5, 6, 8, 12)"; say that item 4's margin is applied to baselines and shams, not to observers.

9. **D2 L110-113.** "The package extends it to claims. Neither makes it a condition on every gate".
   - C applies the broken-case half at most layers: C02 L28-35 "Inject: RNG advance ...", L41-46 "Reject: ...", L50-57 fixtures, L81 "Catch ...", L85 "Inject defects ...". C06 L16: "Add at least five deliberate mutants".
   - D1 L402-404 itself says "C injects faults at every layer".
   - Fix: "The package injects faults at most layers and asks reviewers for mutants; it does not make a gate with no rejected case UNQUALIFIED, and asks nothing of the write-up."

10. **D2 L28-29 (change 3) and D1 L412.** "Attainability is computed, not declared, and refuses a run on day 1", listed as a difference from the package.
    - C never says declared. C01 L282: "verdict attainability/power is checked pre-run". C05 L15 puts "thin runner/refusal gates/receipts" in days 1-15. Only the preflight is in days 16-30 (C05 L30).
    - Fix: "C checks attainability pre-run but schedules the preflight for days 16-30 and does not say how it is computed."

11. **D2 L288-289.** "O's eight coordinates, as the package orders them (physics, search, world, development, boundary, resources, measurement, exposure)".
    - O's eight are physics, boundary, world, developmental history, selection pressure, search, measurement, resources (O03 L25-36: "P: selection/evolution/lifetime pressure"). "Exposure" is not among them.
    - C01 L63 drops P and adds exposure. That is not a reordering.
    - Fix: "the package's eight (O's, with selection pressure replaced by exposure)".

12. **D1 L338, section 7 row 5.** "NEUTRALITY as a facet: C's name; A's question and panel".
    - The question is O's. O03 L158: "No interface should be called substrate-neutral until it has operated correctly on at least two materially different physical realizations."
    - A-R1 L132-133 credits O for it: "v0.1 rightly withholds the word substrate-neutral ...".
    - Fix: "O's rule; A's panel and registered answers; C's name".

13. **D1 L241-243 and L261-263.** "My run 2 is one member of that family" (B's cargo-laundering compiler), then "the cargo compiler is a negative for [reuse]".
    - B puts a task library and the laundering compiler in different classes. B-rep L204: "Split task-library R8-T, learned updater-library/compiler R8-U, and disguised answer-exporter attack". B-rep L461: "Two cases must not be conflated".
    - B does not call the exporter negative for reuse. B-rep L463-464: "a counterfeit of improved learner construction, even if its reuse is economically valuable".
    - The NEGATIVE-for-reuse answer is this author's registration; C gives no answers.
    - Fix: "run 2 is B's R8-T, not its cargo compiler; it reproduces four of the six lines"; mark the cargo compiler's reuse answer as the author's.

14. **D1 L374-375, section 8.** "(C flags such rulers; it plants none)".
    - C's charter requires the attack. C06 L17: "Try to make a physics-specific ruler masquerade as shared."
    - Fix: add "its charter asks reviewers to try the masquerade; its panel holds no standing one".

15. **D1 L92-95 and L275.** A's "repair of that fault" is given as "retention in bits against an exact bound; nested key worlds".
    - A's own repair list (A-R1 L981-1011) has six items. Bits are one of them. The others include fixing the five choices, "QUALIFY BEFORE USE ... a designed positive for the third class and the kit as negatives", and V, U, S as a registered mapping.
    - A-R1 L1053-1054 says of the bits run: "It shows nothing about depth."
    - The "two sides" contrast rests on this narrowing.
    - Fix: list A's repair as A states it.

**MINOR**

16. **D1 L297 and L109-110.** "As each source states them" and "45 tunnel core, 45 organisms". A states "about 65% instrument ... about 25% candidate architectures" (A-R1 L140-145). The 65 never appears in D1. Fix: "regrouped into C's buckets; A's own split is 65/25/5/5".
17. **D1 L186-187.** "B asks for a 2x2 ... at once." B schedules "one I/E cell" in days 31-55 (B-rep L624). That is about D2's own timing (L475-476). Fix: "early".
18. **D1 L377-378.** "Eight of nine reversal conditions (C keeps neutrality at day 45)". C also keeps the substance of A's reversal 6 (C01 L30-32, L258: "Reserve 'recursive' until the ruler has a genuine positive and defeats the counterfeit kit"). Fix: "seven of nine".
19. **D1 L352-354.**
    - "kit of nine: A (seven members)". One of the seven is O's own R8: O04 L188 "fixed update rule + growing library".
    - "B (amortization horizon)". It is also in A (A-R2 L271-272, L417-418) and O (O03 L278 "amortization").
20. **D1 L343-344, row 8.** The contract is credited to "B (3.1 ...); A (perturbations, inheritance dial)". C01 L116-123 is A-R2 L381-397 almost item for item: adapters, inheritance dial, WAIT/DISTRACT/QUENCH/NOISE, capture, cost, shams, tracer. This under-credits A.
21. **D1 L64-66 and D2 L64-65.** "thirteen steps on three stores". In O, U and V are processes (O03 L285-288: "U: process that constructs/changes S"). A-CF L509-510 says so itself.
22. **D1 L118-119, L128; RM L37-38.** A is said to agree on "thin federation / no universal runtime" and "frozen comparators". A's text has neither: A-R1 L113-114 says "shared worlds, shared rulers", and A's W1 asks for exact class values (L625-634). D1 L510-511 gives the shape as "from B, O, C" with no A.
23. **Smaller wording against C in D1 sections 8 and 9.**
    - D1 L427: "NO THIRD OUTCOME". C has four verdicts (C02 L114-117). Say "no INDETERMINATE".
    - D1 L418-419: "asked of nested improvement only". C02 L94 has the general fixture "impossible/non-failing control".
    - D1 L406-407: "sound cases in one place only". C asks for positives in H1, H2 and H7 (C02 L20, L24, L77). Say "for a gate, as opposed to a ruler".
    - D1 L383-384: "world as the unit". C freezes a "sample unit" (C05 L42) and rejects "dependent trials analyzed as IID" (C02 L46).
24. **D2 L583 and L597-599.** "Statuses are the package's", but R7 is shown CATALOGUED with "(I said retire, B said defer)". The package says RETIRE (C03 L37) and is not mentioned. R3 is NEXT in C (C03 L21) and FIXTURE here.
25. **D1 L512-514 ("then new") and D2 L24-26.** The second author's attack is already in C06 L16 and in A-R2 L504-505: "The acceptance test should be run by someone who did not write the tunnel." Add C to the "from" column.
26. **D1 L230-231 and D2 L609-611.** "Six entries trace to my design". O also lists R0 as "All three Phase 3 designs" (O04 L13) and R9 as "Fable/Astra local substrate families" (O04 L200).
27. **D3 L462-463.** "each by someone who has not seen the ruler". B says "Hold out attack constructors, not only random seeds" (B-rep L604-605). The gloss is the author's.
28. **D2 L110.** "O has this rule for organisms". O's rule is for rulers (O03 L67-68: "Ruler qualification requires reachable positive and negative outputs").
29. **D1 L107-108.** B's reversals are given as "one per candidate and one per interval". This omits the six in B's final answer (B-rep L712-718).
30. **D1 L366-367.** "Three statuses" is listed as C's own. B-rep L191-192 already has "a hypothesis ledger" and fixture-only status (L201).

Outside my scope, one line: D1 L152-153 says the strong ruler "stays unqualified" while D1 L270-271 and the registry give FAIL at all three settings. The five-verdict vocabulary keeps those apart.

## Unverifiable from the allowed files

- The contents of C's archive (D1 L36-38). Only the author's saved note describes it.
- "R4 traces to [B's] own design". It rests on O04 L17 only; B does not say it and no design directory was opened.

## Checked and found accurate

- Every double-quoted string in D1, D2 and D3 attributed to B, C or O is verbatim (line wraps aside). Examples: B-rep L41-42, L77-79, L100-101, L121-122, L204, L248, L330, L352, L389-390, L413, L423, L448-449, L453-454, L485, L492, L496-497, L518-520, L609-610, L651, L689-690; C01 L18, L32, L57, L120, L150/L154, L252, L256, L288; C02 L5, L107, L119; C03 L43; C05 L30, L61; C06 L11; O03 L341; O04 L231.
- Saved copies of C match their manifest hashes; the 04:19 modification time on C02 is not a content change.
- The section 1 rows for evidence, verdict, first fault, library learner, next build, R7, boundary and plan match the sources (B-rep L5, L24-25, L60, L83-86, L199-200, L203, L395-398, L620-626; A-R1 L13, L444, L705, L1179).
- "85 defects" is 38+21+26 (A-R1 L43-44). "72 checks" matches the saved checker output. "nine; seven carry a number" holds. Power 0.865 is at A-R2 L498-501.
- Allocation numbers: A 45/20/10/15/5/5 (A-R1 L1212-1217); B 30/12/14/6/8/20/10 (B-rep L630-639); C 35/30/20/10/5 (C05 L5-9). Each column sums to 100; D2's own split sums to 100.
- Run 2 figures (313.5, 20.5, 316.0, 12.0, 16.0, 22.0, 323.5) equal the medians recomputed from `RECEIPT_gauntlet2.json`.
- B's six lines of evidence are B's, in B's order, paraphrased (B-rep L433-440). Four of the six have run-2 numbers.
- Section 7 rows 1, 2, 3, 6, 7, 9, 10, 11, 12, 13, 15, 16 and the second-build row are correct. C's section numbers are right.
- Counts: nine frozen choices (C01 L242-250), nine kit members (C01 L230-238), eleven acceptance conditions (C01 L276-286), eight runtime items (C01 L116-123), eighteen fixtures in C's order (C02 L91-108), ten attacks and nine returns (C06 L16-37), eight builds and two runs before Gate 15 (C05 L15-24).
- Section 8 items that C really lacks (grep of the five files): equivalence margins, update-law freeze, mediation clamp, a rule against a scalar, the table of old engines, experiments as alternative/arms/readout/decision, the scale check, a cost test for the tunnel, operator attention.
- D2 section 9's execution-class rows match B-rep L114-117. B's seven facets are at L129-131. The H-layer column in D3 section 4 matches C02.
