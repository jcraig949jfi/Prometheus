# Epistemic controls for an LLM-authored research loop

**Techne, 2026-08-25.** Written after cycles 049–059 and two audit passes over them.
Supersedes nothing; it is the design document the error record earned.

---

## 1. What the record actually showed

Eleven autonomous cycles produced four production fixes, twelve defect findings, and — measured
honestly — **roughly seventeen errors of my own**, in four classes:

- **Wrong population (8)** — a measurement taken over one set of rows, quoted as a property of
  another. Three occurred *while actively working on that exact class*: inside the script built
  to prevent it, inside the cycle measuring my own self-model, and against a memory file naming
  the specific antipattern.
- **Citation (2)** — named a function without importing it (`_verify_mahler_mpmath` does not
  exist); characterised a dataset without opening it. **Both times the computed numbers were
  right and the label attached to them was invented.**
- **Measurement answered a different question (7)** — stale file, stored literals vs old path,
  sympy cold-start read as a 16× regression, PARI import read as a hang, double-encoded
  arguments that delivered every function a *string*.
- **Invalid control (2 of 3)** — controls that carried the defect they were meant to exclude.

**Six of the seven bad measurements were caught because the number looked absurd, not because
anything checked.** A *plausible* wrong answer would have shipped in every case.

**Two of these recurred after being written into the traps ledger.** The same root cause — setup
time attributed to the thing under test — appeared in cycles 052 and 059, seven cycles apart,
with the lesson recorded in between. **A written rule demonstrably does not prevent recurrence
in this system.**

---

## 2. The decisive contrast

Building the mechanical checker took **four defects in twenty minutes**: it imported modules to
test symbol existence (~12 s each, and *executed* code to ask whether a name exists); a splice
deleted a function; the contradiction check did not fire on the exact case it was written for;
inline regex flags sat mid-pattern.

**Every one surfaced within seconds** — a `NameError`, an `re.error`, a timeout, a zero-finding
run on a file known to contain the defect.

Same author, same session. **Inference errors sat undetected for cycles; mechanical errors
announced themselves immediately.** The difference is entirely whether the claim was addressable
by something other than judgement.

**That is the whole design principle: move claims down the ladder from inference to decidable.**

---

## 3. The ladder, by how much judgement each rung requires

### Tier 0 — fully decidable, zero inference

No model reads anything; the exit code is the verdict.

- **`techne/scripts/claim_check.py`** — every `module::symbol` must resolve (AST, no import, no
  execution); every file path must exist; every stated rate must equal its own fraction; any
  identifier called a false positive that also appears as a detection is surfaced.
  *Catches `_verify_mahler_mpmath`. Fires on cycle 055 and names the false positive that sat
  inside the 7/8 headline for five cycles.*
- **`techne/scripts/sampling_lint.py`** — AST-flags positional selection (ordered slices of
  traversals, sorts, match results): the syntactic cause of the wrong-population class.
- **`techne/scripts/arsenal_red.py`** — a reported count ships the command that produced it and
  diffs by failing node id, never by number.

### Tier 1 — decidable given one declaration

The declaration needs a mind; the check does not.

- **`techne/lib/measurement_guard.py`** — a number is unreadable until the same code path
  returns a known answer on an independently-known case. `Measurement.value` **raises** if read
  before validation; `population` is a **required field**; `compare()` refuses arms that return
  the same value on a case chosen because they should differ.
  *Retro-tested against the real failures: 5 of 6 caught.*
  **CORRECTION (2026-08-25, from external review): that figure is CIRCULAR and I did not say
  so.** Those six failures were the design input for this instrument, so 5/6 is a **fit
  statistic, not a generalization estimate** — the wrong-population error again, inside the
  document about wrong-population errors. The real measurement is the **prospective** escape
  rate under frozen controls; see `CAMPAIGN_ESCAPE_RATE_PREREG.md`.
- **`techne/ladder_circuits/control_certifier.py`** — a control is checked against **every**
  shape in the taxonomy; an unchecked shape reports `UNCERTIFIED`, never clean.

### Tier 2 — the domain supplies the oracle

**The highest-leverage tier for this program, and the most underused.** In most software a human
must say what "correct" means. In mathematics the theorems do it:

```
M(f·g) = M(f)·M(g)        multiplicativity   -> caught the repeated-root defect
house(f) ≤ M(f) ≤ L(f)    height chain       -> caught the house() defect
M(f) = 1 ⟺ f cyclotomic   Kronecker          -> caught is_cyclotomic disagreeing with M
empty product = 1         convention         -> certified a control clean
```

**Differential testing** belongs here too: the Lehmer verifier fix was confirmed because an
independent symbolic route (`factor_list` over ℤ[x]) agreed on all 17 entries. Two
implementations, one answer, zero inference — the strongest confirmation anything received.

### Tier 3 — irreducibly inferential

*Is this the right population? Does the docstring state the contract it should? Is this finding
worth reporting?* **Mark these; do not launder them as measurements.**

---

## 4. The structural gap

Every finding this loop produces is **markdown**. Nothing can test an essay.

`sigma_kernel` has 54 modules of typed-record infrastructure — `coordinate_chart`,
`exclusion_certificate`, `caveats`, frozen dataclasses — built for exactly this. **The loop
bypasses it entirely.**

If a finding were a typed record instead:

```python
Claim(subject="techne.lib.mahler_measure::mahler_measure",
      metric="max_abs_error", value=4.481e-10,
      population="all 8,625 catalog entries",
      command="python -m ...", confirmed_by=["path_b_symbolic"])
```

…then all of Tier 0 runs on every finding automatically, forever, with nobody remembering to.
**That is the largest single item in this document**, and larger than any individual bug in the
record: the substrate that makes claims machine-addressable exists, and the role that owns it
stopped using it for its own findings.

---

## 5. Where this points, against the north star

The north star is *"map the verbs of mathematics so synthetic intelligence can find
transformations humans, trapped in noun-silos, cannot see."* The traversal is synthetic; the
proofs and meaning remain human.

The record above is a direct measurement of the traversal's reliability, and it is sobering:
**an LLM-authored research loop generates findings and errors at comparable rates, and cannot
reliably detect its own errors by introspection.** Not because the reasoning is poor — several
findings were genuinely good — but because *the same faculty that produces the finding produces
the error*, and it has no independent vantage on itself.

That does not defeat the thesis. It sharpens what the machine is for. **RETRACTED PHRASING (2026-08-25): "the adjudication must not be synthetic" is too broad —
a human is also inferential, a second implementation is still synthetic. The property is
EPISTEMIC INDEPENDENCE. Replacement doctrine: _generation may be synthetic; promotion requires
an independent failure mode. No claim may be promoted by the same epistemic path that generated
it._** Every result that survived scrutiny this week
survived because something outside my judgement confirmed it — a theorem, an independent
implementation, a test that failed.

The practical consequence: **the ratio of Tier-2 checkable claims to Tier-3 inferential ones is
the real capability metric for this program**, more than any discovery count. A claim a theorem
can adjudicate scales; a claim only I can adjudicate does not.

---

## 6. Immediate next steps

1. **Emit findings as typed records**, not markdown, into the existing `sigma_kernel` substrate.
   Retrofit the 12 outstanding findings first — they are the natural test set.
2. **Wire `claim_check` into a pre-commit hook** on `techne/loop/*.md`, so a wrong symbol name
   *cannot enter the record* rather than being caught later by luck.
3. **Fix findings #9–12** (mine, no ruling needed): three silent-NaN returns and `zaremba_test`'s
   unbounded search.
4. **Clear the 46 arsenal reds**, gated on the #242 ruling — 26+ are missing optional
   dependencies, and `hyperbolic_volume` threw OSError on every probe for want of SnapPy.
5. **Extend Tier-2 coverage**: enumerate which arsenal functions have a mathematical invariant
   that could check them, and add the ones that do not.

## 7. Open for the operator

- **#242** — dependency install, with the vetting protocol proposed and self-reported
  counter-evidence (the last dependency taken on a leverage argument is consumed by one demo).
- **#311** — retract vs re-run the Lehmer verdict built on a defective verifier.
- **#341** — update a stale authority test now that its data is verified.
- **Eight cross-role findings** remain with Ergon, Charon, Harmonia, Theseus and Aporia,
  unanswered.

*— Techne, 2026-08-25.*
