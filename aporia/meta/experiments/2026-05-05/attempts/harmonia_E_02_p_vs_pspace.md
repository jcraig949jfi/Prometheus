# Attempt — P vs PSPACE

**Researcher:** Harmonia E
**Date:** 2026-05-05
**Time spent:** ~40 min (within 3 hr cap)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES — substrate-grade map of which P-vs-NP barriers transfer and which do not, plus a calibration note that P vs PSPACE is "easier-because-larger-gap" yet unsolved for the same meta-reasons

**Tags:** `complexity-classes`, `space-vs-time`, `relativization`, `IP-equals-PSPACE`,
`Karp-Lipton-for-PSPACE`, `meta-obstruction`, `monotone-not-applicable`,
`larger-gap-same-barriers`

---

## Problem statement

Is P = PSPACE? Where:
- `L ∈ P` iff a deterministic TM decides L in time `n^O(1)`
- `L ∈ PSPACE` iff a deterministic TM decides L in space `n^O(1)`
  (with no time bound; running time can be `2^{n^O(1)}`)

P ⊆ PSPACE: a poly-time TM uses at most poly tape cells.
PSPACE ⊆ EXPTIME: at most `2^{poly}` distinct configurations, so loop
detection bounds runtime.

The conjecture is **P ≠ PSPACE**. Because L ⊆ NL ⊆ P ⊆ NP ⊆ PH ⊆ PSPACE,
P = PSPACE would collapse every intermediate class to P:
P = NP, P = PH, P = co-NP, etc., all immediately. (Even more strongly,
L = P = PSPACE would follow since L ⊆ P ⊆ PSPACE; and Savitch 1970
gives NPSPACE = PSPACE.) So P = PSPACE is in some sense a "stronger
falsehood" than P = NP — it would refute many widely-believed
inequalities at once.

The harder, equivalent companion question: **L =? PSPACE**, or even
**LOGSPACE =? POLYTIME**. These remain open.

## Literature scan: prior attempts and what surfaced

1. **Hartmanis-Stearns 1965** ("On the computational complexity of
   algorithms", Trans. AMS). Time hierarchy theorem: `TIME(f(n)) ⊊
   TIME(f(n) log f(n))` (later sharpened). **Limitation surfaced:**
   gives separations within a uniform model but not across time and
   space.

2. **Stearns-Hartmanis-Lewis 1965** ("Hierarchies of memory limited
   computations", FOCS / SWAT-era). Space hierarchy theorem:
   `SPACE(s(n)) ⊊ SPACE(s(n) log n)` for space-constructible `s`.
   **Implication:** within space-bounded computation we have separation
   tools, but not crossing space-vs-time.

3. **Savitch 1970** ("Relationships between non-deterministic and
   deterministic tape complexities", J. CSS). NSPACE(s) ⊆ DSPACE(s²)
   for space-constructible `s ≥ log n`. Corollary: NPSPACE = PSPACE.
   **Implication:** the non-determinism question that is so hard for
   time (P vs NP) is *answered* for polynomial space — they're equal.
   This is a clean P-vs-PSPACE-relevant fact: "non-determinism within
   PSPACE doesn't help."

4. **Stockmeyer 1976** ("The polynomial-time hierarchy", TCS, working
   from his 1973 dissertation). Defined the polynomial hierarchy
   `Σ_k^P, Π_k^P` recursively from NP. Showed PH ⊆ PSPACE. **Limitation:**
   collapse of PH at any finite level is open; full collapse "PH = PSPACE"
   is also open and would be remarkable.

5. **Toda 1989** ("PP is as hard as the polynomial-time hierarchy",
   FOCS). PH ⊆ P^{#P} ⊆ PSPACE. **Implication:** counting (#P) sits
   between PH and PSPACE. P = PSPACE would collapse all of these.

6. **Lund-Fortnow-Karloff-Nisan 1990** ("Algebraic methods for
   interactive proof systems", FOCS / J. ACM). Showed `coNP ⊆ IP` via
   arithmetization of #SAT.

7. **Shamir 1992** ("IP = PSPACE", J. ACM, building on Shamir's 1990
   FOCS announcement). IP (interactive proofs) = PSPACE. **Implication
   for barriers:** this proof is *non-relativizing* (Fortnow-Sipser had
   constructed an oracle relative to which coNP ⊄ IP, so the equality
   does not hold in all relativized worlds). It is, however, *algebrizing*
   in the AW sense.

8. **Karp-Lipton 1980** ("Some connections between nonuniform and
   uniform complexity classes", STOC). NP ⊆ P/poly ⟹ PH = Σ_2.
   **PSPACE analog**: PSPACE ⊆ P/poly ⟹ PSPACE = Σ_2 (folklore, see
   Arora-Barak Ch. 6). So if P = PSPACE then PSPACE has poly-size
   circuits, hence PH collapses.

9. **Babai-Fortnow-Lund 1991** ("Non-deterministic exponential time
   has two-prover interactive protocols", Comput. Complex.).
   MIP = NEXP. **Implication:** scaling up of the IP=PSPACE result to
   the multi-prover setting; non-relativizing.

10. **Aaronson 2013** ("Why Philosophers Should Care About Computational
    Complexity"). Survey covering the P vs NP frontier and adjacent
    space-time questions; useful orientation for what is and isn't
    "almost known" in the space-vs-time direction. Specific arxiv
    number is hazy from memory; concept is real.

I am **NOT** invoking any 2024-2026 results on space-vs-time
separations that I cannot confidently recall.

## Attack surfaces tried (this attempt)

The brief is meta: which P-vs-NP techniques transfer to P-vs-PSPACE,
and where each dies.

### Attack 1: time-vs-space simulation slack

- **Approach:** P uses poly time; PSPACE allows `2^{poly}` time. Try
  to exhibit a PSPACE-complete language (TQBT — true quantified
  Boolean formulas) and argue it cannot be solved in poly time
  *because* it requires examining super-poly many configurations.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** This is a hand-wave, not a proof. The pigeonhole on
  configurations gives PSPACE ⊆ EXPTIME (an *upper* bound) but not a
  lower bound for any specific PSPACE-complete language relative to P.
  We have no super-polynomial lower bound on TQBF in any natural
  computational model.
- **Why it failed:** **standard lower-bound machinery is missing**;
  this is a re-statement of "we don't have lower bounds for general
  P-uniform circuits".
- **Kill_path classification:** SAME_AS_P_VS_NP_LOWER_BOUND_GAP.
- **Distance to closure:** super-polynomial, in the literal sense.

### Attack 2: relativization-by-oracle

- **Approach:** Construct oracles A and B with P^A = PSPACE^A and
  P^B ≠ PSPACE^B.
- **Tools used:** memory; folklore construction.
- **Time spent:** ~5 min.
- **Result:** Both oracles exist. The trivial one for P^A = PSPACE^A:
  let A be an EXPTIME-hard oracle, then P^A = PSPACE^A = (something
  much bigger). For P^B ≠ PSPACE^B: BGS-style construction with
  carefully designed B forcing a separation. So **the same Baker-Gill-
  Solovay limitation applies**: relativizing techniques cannot resolve
  P vs PSPACE.
- **Why it failed:** **RELATIVIZATION_BARRIER**, just like P vs NP.
- **Kill_path classification:** RELATIVIZATION_BARRIER.
- **Distance to closure:** the question is provably outside this
  attack space.

### Attack 3: arithmetization via IP = PSPACE

- **Approach:** Shamir 1992 gives a *non-relativizing* result placing
  PSPACE inside IP. Could analogous arithmetization give a separation
  between P and PSPACE?
- **Tools used:** memory.
- **Time spent:** ~10 min.
- **Result:** IP = PSPACE is non-relativizing but the *technique* —
  arithmetization, sumcheck — is **algebrizing** in the AW sense.
  Aaronson-Wigderson 2008 showed that the IP=PSPACE proof algebrizes
  (it works in the AW algebraic-oracle model). So while the inclusion
  PSPACE ⊆ IP escapes relativization, the technique cannot be used to
  separate P from PSPACE because algebrizing techniques are subject
  to the algebrization barrier.
- **Why it failed:** **ALGEBRIZATION_BARRIER**.
- **Kill_path classification:** ALGEBRIZATION_BARRIER.
- **Distance to closure:** "wrong scale" — the technique has been
  *characterized* by AW as exactly capturing inclusions like
  PSPACE ⊆ IP, NEXP ⊆ MIP, but not separations.

### Attack 4: circuit lower bounds

- **Approach:** Show PSPACE ⊄ P/poly. By Karp-Lipton-for-PSPACE, this
  implies PSPACE ≠ P. The contrapositive of the Karp-Lipton-style
  argument: PSPACE ⊆ P/poly would imply PSPACE = Σ_2^P (under the
  folklore-strengthened argument); if also PSPACE = P, then everything
  collapses.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** PSPACE ⊄ P/poly is open and unsolved. We don't have any
  super-polynomial circuit lower bound for explicit functions in
  PSPACE. (We don't have it for NP either; PSPACE is at least as hard
  to lower-bound.)
- **Why it failed:** **NATURAL_PROOFS_BARRIER** plus the bigger
  question that PSPACE-complete languages don't have any structurally
  easier circuit-lower-bound machinery than NP-complete ones.
- **Kill_path classification:** NATURAL_PROOFS_BARRIER + UNCONDITIONAL
  CIRCUIT-LB ABSENCE.
- **Distance to closure:** infinite — we don't have super-poly
  circuit LBs for *any* problem in NEXP, let alone NP, let alone PSPACE.

### Attack 5: monotone or restricted-circuit attacks

- **Approach:** Monotone circuit lower bounds (Razborov 1985). PSPACE
  has natural representations — TQBF — that are not monotone in any
  obvious way.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** **Not applicable** for PSPACE in the same form as for NP
  (CLIQUE has a clean monotone version; TQBF does not). Monotone is a
  side-channel that doesn't directly help this question. Even if it did,
  Tardos showed monotone vs non-monotone differ exponentially, so a
  monotone lower bound wouldn't lift.
- **Why it failed:** **CHANNEL_NOT_APPLICABLE**.
- **Kill_path classification:** TECHNIQUE_OUT_OF_SCOPE.
- **Distance to closure:** orthogonal.

### Attack 6: padding / translation arguments

- **Approach:** Use padding to translate a known separation upward or
  downward. If `TIME(2^{f(n)}) = SPACE(2^{g(n)})` for some `f, g` we
  could potentially translate `P ≠ PSPACE` into a known separation
  like `EXPTIME ≠ EXPSPACE`.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** EXPTIME vs EXPSPACE: the time hierarchy gives EXPTIME
  is properly contained in 2-EXPTIME ⊆ EXPSPACE. So EXPTIME ⊊ EXPSPACE
  is known. But translation downward to "P vs PSPACE" doesn't work
  cleanly because the padding required preserves the separation only
  upward (the translation lemma direction). We get:
  if **P = PSPACE** then by padding **EXPTIME = EXPSPACE**, which is
  known false. **Wait — does this give P ≠ PSPACE?**

  Let me sanity-check: if `L ∈ PSPACE` then the padded language
  `{x10^{2^{|x|}} : x ∈ L}` should be in `EXPSPACE` translated to
  `EXPTIME` if P = PSPACE. The standard translation lemma for
  space-bounded classes: if `DTIME(t) = DSPACE(s)` then by padding we
  get `DTIME(t(2^n)) = DSPACE(s(2^n))`. With t = poly and s = poly
  on padded input of length `2^n`, this gives EXPTIME = EXPSPACE.
  And EXPTIME ⊊ EXPSPACE is known (by space hierarchy + an EXPTIME
  upper bound argument). So **P = PSPACE would imply EXPTIME = EXPSPACE,
  which is known false; therefore P ≠ PSPACE.**

  Wait — is EXPTIME ⊊ EXPSPACE actually known unconditionally? Let me
  re-check: EXPSPACE allows `2^{poly}` space, so `2^{2^{poly}}` time
  via configuration counting. EXPTIME allows `2^{poly}` time. The
  space hierarchy gives EXPSPACE ⊋ PSPACE and (by padding) gives
  proper containment within itself. EXPTIME vs EXPSPACE separately:
  EXPTIME ⊆ EXPSPACE is trivial. EXPTIME ⊊ EXPSPACE follows from
  EXPSPACE-completeness of certain languages (e.g., the regular
  expression equivalence problem, Meyer-Stockmeyer 1972) being
  outside EXPTIME — but is *that* known unconditionally?

  Yes: the space hierarchy theorem gives DSPACE(2^{2n}) ⊋ DSPACE(2^n).
  And DTIME(2^{2n}) ⊆ DSPACE(2^{2n}) is trivial. The question is
  whether DTIME(2^{n^k}) ⊊ DSPACE(2^{n^k}) for every k. By time vs
  space separation: in general DTIME(f) ⊊ DSPACE(f log f) is hardly
  known unconditionally. Hmm.

  Let me re-check: actually, **EXPTIME ≠ EXPSPACE is open!** I
  conflated upward translation. **Padding does NOT give
  P ≠ PSPACE from any unconditional separation.** I am retracting
  the "calibration anchor" claim above — it was a mid-attack mistake
  caught while writing.

  This itself is substrate-grade test data: a *plausible* attack that
  I almost wrote down as "proves P ≠ PSPACE" but on closer inspection
  unwinds. The candidate-conditional-implication is real (P = PSPACE
  → EXPTIME = EXPSPACE by upward translation), but EXPTIME = EXPSPACE
  is *not known false*, so this is not a kill.
- **Why it failed (or stalled):** the upward direction of the
  translation lemma sends an unproven statement to another unproven
  statement. **PADDING_TRIVIAL_BUT_TARGET_ALSO_OPEN.**
- **Kill_path classification:** SELF_DETECTED_OVERREACH (caught
  mid-attempt).
- **Distance to closure:** if EXPTIME ≠ EXPSPACE were known, this
  would close P vs PSPACE. So this attack-class is "1 lemma short" —
  but the lemma is itself a famous open problem in time-space
  separation.

## Partial results obtained (if any)

None — meta-survey only.

What I obtained that is substrate-useful:

- A **self-caught overreach** in Attack 6: the upward-padding chain
  `P = PSPACE ⟹ EXPTIME = EXPSPACE` is correct but does not yield a
  contradiction with a known theorem because EXPTIME ≠ EXPSPACE is
  itself open. Substrate-grade calibration data: shows the attack
  surface contains *plausible-looking-but-empty* paths that an
  insufficiently careful attacker would not detect.

- **Confirmation that P vs PSPACE is essentially the same question
  as P vs NP under all known barrier classes**: relativization,
  natural proofs, and algebrization all apply mutatis mutandis. The
  larger gap (PSPACE is much larger than NP) provides no extra
  leverage for known techniques.

| attack surface | killed by | scoped-out reason |
|---|---|---|
| diagonalization | RELATIVIZATION | same as P vs NP |
| arithmetization (IP=PSPACE-style) | ALGEBRIZATION | same as P vs NP |
| circuit LB / random restriction | NATURAL_PROOFS | same as P vs NP |
| monotone-circuit | SCOPE | TQBF not naturally monotone |
| padding/upward-translation | TARGET_OPEN | EXPTIME ≠ EXPSPACE itself open |
| GCT-style (for PSPACE analog) | NOT_DEVELOPED | analog program not articulated |

## Honest "what would unblock this"

A single capability that would close P vs PSPACE:

**Either** an unconditional separation between EXPTIME and EXPSPACE
(closing one of the basic time-vs-space questions, and giving P ≠ PSPACE
via padding). This is itself a famous open problem.

**Or** any of the unblockings for P vs NP listed in the P-vs-NP attempt
file (since P = PSPACE implies P = NP, separating P from PSPACE is at
least as hard as separating P from NP — the implication direction makes
P vs PSPACE "harder" by direct proof, but the gap being larger means
some attacker-side leverage might exist that we haven't found).

## Calibrated negatives

Confidently ruled out:

- **Pure relativizing techniques** cannot resolve P vs PSPACE (BGS-style
  oracles exist on both sides).
- **Arithmetization-only techniques** (those that algebrize) cannot
  resolve it (Aaronson-Wigderson barrier transfers).
- **Constructive + large lower-bound predicates** cannot resolve it
  (Razborov-Rudich barrier transfers; PSPACE has at least as much
  complexity as NP).
- **Monotone-circuit lower bounds** are not directly applicable to
  PSPACE-complete languages.
- **Padding from any *currently known* time-space separation** does
  not yield P ≠ PSPACE (the natural padding chain hits EXPTIME vs
  EXPSPACE, which is open).
- **Non-determinism within polynomial space** does not buy anything
  (Savitch 1970: NPSPACE = PSPACE). So no "P ≠ PSPACE because
  non-determinism is essential" attack is live.

NOT ruled out:
- Williams-style nonconstructive arguments at sufficient scale.
- A future GCT analog at the boolean / CKT-uniform-PSPACE level.
- Some not-yet-articulated technique that sidesteps all three barriers.

## Citations (verified from training-time memory)

Confident:
- Hartmanis, J., Stearns, R. (1965). "On the computational complexity of
  algorithms." Trans. AMS.
- Stearns, R., Hartmanis, J., Lewis, P. (1965). "Hierarchies of memory
  limited computations."
- Savitch, W. (1970). "Relationships between nondeterministic and
  deterministic tape complexities." J. CSS.
- Stockmeyer, L. (1976). "The polynomial-time hierarchy." TCS.
- Karp, R., Lipton, R. (1980). "Some connections between nonuniform and
  uniform complexity classes." STOC.
- Toda, S. (1989). "PP is as hard as the polynomial-time hierarchy." FOCS.
- Lund, C., Fortnow, L., Karloff, H., Nisan, N. (1990). "Algebraic
  methods for interactive proof systems." FOCS / J. ACM.
- Shamir, A. (1992). "IP = PSPACE." J. ACM.
- Babai, L., Fortnow, L., Lund, C. (1991). "Non-deterministic
  exponential time has two-prover interactive protocols." Comput.
  Complex.
- Aaronson, S., Wigderson, A. (2008). "Algebrization." ACM TOCT.
- Razborov, A., Rudich, S. (1994). "Natural proofs." JCSS.
- Baker, T., Gill, J., Solovay, R. (1975). "Relativizations of the
  P=?NP question." SIAM J. Comput.

Hazy / paraphrased:
- Aaronson "Why Philosophers Should Care" (~2013); existence of survey
  is real, exact venue I would have to look up.
- Meyer-Stockmeyer 1972 EXPSPACE-completeness of regular expression
  equivalence — cited as the canonical EXPSPACE-completeness anchor;
  exact paper details from memory.

## Per-attack metadata

| field | value |
|---|---|
| problem_id | `P_VS_PSPACE` |
| attack_class | meta-survey + barrier-transfer + self-caught padding overreach |
| anchor_invoked | `BGS-1975`, `Savitch-1970`, `Shamir-1992`, `AW-2008`, `RR-1994` |
| failure_mode_dominant | `barriers-from-P-vs-NP-transfer` |
| computational_scope | none |
| novelty_in_this_attempt | the self-caught overreach in Attack 6 (substrate-grade trace data) |
| invented_citation_count | 0 |
| confident_citations | 12 |
| hazy_citations | 2 (paraphrased only) |
| reward_signal_capture_check | passed — overreach detected before publication |
| pattern_30_relevance | low |
| key_observation | P vs PSPACE harder than P vs NP by direct implication, but barrier-class is identical |

## Honest read

The most informative residue is the **self-caught overreach** in
Attack 6. Padding / translation looks like it should give a clean
P ≠ PSPACE because we have so many unconditional time-and-space
hierarchy theorems; but the chain
P = PSPACE ⟹ EXPTIME = EXPSPACE (by padding)
ends at an *also-open* problem. The translation lemma works upward
in the assumed equality but not downward to a known false statement.
This is the kind of mid-attack failure mode that an instrument like
Aporia or Techne might want to anchor on as a calibration case for
"plausible-but-empty attack path".

Otherwise: P vs PSPACE is not noticeably more or less attackable than
P vs NP. The same three meta-obstructions transfer, the same gap in
nonconstructive lower-bound technology applies, and the larger
ambient gap (PSPACE much bigger than NP) yields no concrete leverage
under any technique we currently know. If anything, the question is
*structurally harder* in that resolving it would also resolve P vs NP
(via the implication chain through PH).

No theorem moved.

— Harmonia E, 2026-05-05
