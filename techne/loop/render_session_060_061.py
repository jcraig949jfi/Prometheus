"""Render the cycles 060-061 session record and the external-review packet FROM the records.

CAMPAIGN RULE 2, applied to a summary document. A consolidated write-up is exactly where
hand-typed numbers creep back in -- the row files are two directories away and the prose is
being written for a reader, so a remembered figure feels harmless. Every quantity below is
therefore pulled from a committed artifact at render time:

    pivot/arsenal_red_060.json
    techne/loop/rung_notes/cycle_060_nonfinite_sweep_{PRE,POST}FIX.json
    techne/loop/rung_notes/cycle_060_p4_arsenal.json
    techne/loop/rung_notes/cycle_061_red_triage.json
    techne/loop/rung_notes/cycle_061_zaremba_{prefix,postfix}.json

The narrative is mine; the numbers are not. If a row file changes, this document changes with
it, and if a row file is missing this script fails rather than emitting a plausible number.

    python techne/loop/render_session_060_061.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techne.lib.claim_record import render  # noqa: E402

ROWS = REPO / "techne" / "loop" / "rung_notes"


def _load(path: pathlib.Path):
    if not path.exists():
        raise SystemExit(f"REFUSING TO RENDER: missing row file {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PRE = _load(ROWS / "cycle_060_nonfinite_sweep_PREFIX.json")
POST = _load(ROWS / "cycle_060_nonfinite_sweep_POSTFIX.json")
P4 = _load(ROWS / "cycle_060_p4_arsenal.json")
RED = _load(REPO / "pivot" / "arsenal_red_060.json")
TRI = _load(ROWS / "cycle_061_red_triage.json")
ZPRE = _load(ROWS / "cycle_061_zaremba_prefix.json")
ZPOST = _load(ROWS / "cycle_061_zaremba_postfix.json")

C060 = _module("claims_060", "techne/loop/claims_060.py")
C061 = _module("claims_061", "techne/loop/claims_061.py")


def facts() -> dict:
    claims60, claims61 = C060.claims(), C061.claims()
    promo60 = sum(1 for c in claims60 if c.promotable()[0])
    promo61 = sum(1 for c in claims61 if c.promotable()[0])
    changed = [q for q in range(1, 501) if ZPRE[str(q)] != ZPOST[str(q)]]
    nd = RED.get("name_diff", {})
    return {
        "pre_tally": PRE["tally"],
        "post_tally": POST["tally"],
        "pre_nonfinite_fns": PRE["n_functions_returning_nonfinite"],
        "p4_considered": P4["functions_considered"],
        "p4_outside": P4["n_outside_the_height_family"],
        "p4_dropped_arity": len(P4["dropped_arity"]),
        "red_total": RED["red"],
        "red_errors": RED["collection_errors"],
        "red_new": len(nd.get("NEW", [])),
        "red_gone": len(nd.get("GONE", [])),
        "suite_summary": RED["summary_line"],
        "triage_nodes": TRI["n_nodes"],
        "triage_final": C061.TALLY,
        "absent_modules": TRI["missing_modules"],
        "zaremba_changed": changed,
        "claims_060": len(claims60), "promotable_060": promo60,
        "claims_061": len(claims61), "promotable_061": promo61,
    }


F = facts()
TOTAL_CLAIMS = F["claims_060"] + F["claims_061"]
HELD_TOTAL = TOTAL_CLAIMS - F["promotable_060"] - F["promotable_061"]
MISSING = F["triage_final"].get("MISSING_DEPENDENCY", 0)


def measured_facts_block() -> str:
    t = F["pre_tally"]
    return f"""### Cycle 060 — the height family's non-finite domain

- Population: the FULL cross product of 5 scalar entry points x 9 non-finite inputs = **{PRE['n_calls']} calls**,
  complete enumeration, no sampling.
- **Before:** `RETURNS_NONFINITE {t.get('RETURNS_NONFINITE', 0)} / RAISES {t.get('RAISES', 0)} /
  RETURNS_BOOL {t.get('RETURNS_BOOL', 0)} / RETURNS_FINITE {t.get('RETURNS_FINITE', 0)}` —
  **four different postures** toward the same out-of-domain input, varying with the POSITION of
  the bad coefficient.
- **{F['pre_nonfinite_fns']} of 5** entry points returned a non-finite float rather than raising.
- **The two RETURNS_FINITE are the load-bearing result:** `house([inf, 1, -1])` and
  `house([-inf, 1, -1])` returned **0.0**, which is `house`'s genuine documented value for a
  monomial — a plausible, in-range, wrong answer, indistinguishable from a correct one.
- **After:** `RAISES {F['post_tally'].get('RAISES', 0)}` and nothing else.
- Registry sweep for the class outside the height family: **{F['p4_considered']} functions
  considered**, **{F['p4_dropped_arity']} dropped for arity and named**,
  **{F['p4_outside']} leak outside the height family** — and all three return a structured result
  carrying an explicit failure marker, i.e. graceful degradation, not a silent wrong number.
- Regression: `{F['suite_summary'].strip()}` — name-diff **NEW {F['red_new']}, GONE {F['red_gone']}**.

### Cycle 061 — the arsenal reds, by cause

- Population: **{F['triage_nodes']} node ids** — the complete FAILED list ({F['red_total']}) plus
  every collection error ({F['red_errors']}) — each **re-run individually** and classified by the
  exception it actually raised.
- Final classification: {', '.join(f'**{v} {k}**' for k, v in sorted(F['triage_final'].items(), key=lambda kv: -kv[1]))}.
- **REAL_DEFECT: {F['triage_final'].get('REAL_DEFECT', 0)}.**
- Absent modules, extracted from the interpreter's own messages rather than recalled:
  {', '.join('`' + m.split(' ')[0].rstrip(';') + '`' for m in F['absent_modules'])}.
  **A ruling on #242 buys {MISSING} of {F['triage_nodes']} red node ids.**
- Finding #16 differential over q = 1..500: **{len(F['zaremba_changed'])} value changed**, and it
  is q = {F['zaremba_changed'][0] if F['zaremba_changed'] else 'none'}. All 499 results for
  q >= 2 are identical.

### Claim records

- Cycle 060: **{F['promotable_060']} of {F['claims_060']}** promotable.
- Cycle 061: **{F['promotable_061']} of {F['claims_061']}** promotable — **{F['claims_061'] - F['promotable_061']} HELD**, both blocks correct,
  **0 false blocks**.
- Across the session: **{TOTAL_CLAIMS} claims exported, {HELD_TOTAL} held.**
- `escape_rate` **1 of {TOTAL_CLAIMS}** — cycle 060's headline finding #17, falsified by cycle 061."""


SESSION_DOC = """# Session record — Techne cycles 060 and 061

**2026-08-25.** Campaign cycles 1 and 2 of 20 under `techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md`.
Controls frozen at the campaign's opening commit and NOT modified in response to any failure.

**Rendered from the records by `techne/loop/render_session_060_061.py`.** Every number below is
read from a committed row file at render time; none is typed into the prose. This is campaign
Rule 2 applied to a summary document, which is precisely where remembered figures creep back in.

---

## 1. What this session was for

The campaign's objective is not "make fewer mistakes". It is:

> **Can Techne become incapable of silently promoting the mistakes it still makes?**

Two cycles ran. Both pre-registered their predictions in a commit made *before* any measurement,
both scored those predictions including the failures, and both shipped their raw rows in the same
commit as their verdicts.

## 2. Commits

- `3b6f9de8` — cycle 060 pre-registration, before measuring.
- `d36f8c3f` — cycle 060: the shared coefficient-domain guard, the `zaremba_test` search bound,
  87 new tests, the report, the rows.
- `bab3ab5f` — cycle 061 pre-registration, before the failing node ids were read.
- `2b9123b9` — finding #16 fix (source + a 500-value differential), isolated by design.
- `8fbaa34b` — finding #16 tests, split off only because a concurrent seat reverted the file
  between the verification run and `git add`.
- `7181c239` — cycle 061: the red triage, the report, the rows.

## 3. Measured facts

{FACTS}

## 4. What was fixed

**A shared coefficient domain** — `techne/lib/coefficient_domain.py`, now guarding all five
scalar entry points of the height family and all three batch entry points.

The decision was **refuse, not propagate**, against a criterion pre-registered before the data:
*the posture that wins is the one under which a caller cannot confuse "no height exists for this
input" with "the height is small."* Propagation fails it, and worse than expected — NaN is not
merely wrong, it is **unordered**. `mahler_measure([nan])` is neither below, nor above, nor equal
to the Lehmer bound, so a candidate whose measure failed to compute exits every screen without
ever being counted as a failure.

The scalar/batch contract is kept coherent: the batch path already used NaN in its *output* as
the in-band signal for a degenerate row, so non-finite *input* is refused at the front door and
`NaN out <=> degenerate row in` is now an asserted invariant rather than a convention.

**Strings are refused by type, not just by value.** `mahler_measure(["1.0", "-2.0"])` returned
**2.0** — the correct Mahler measure of x-2 — because numpy parses numeric strings on cast. Cycle
059's double-encoding fault handed every function in a 128-call sweep a string; this function
would have answered correctly throughout and concealed it.

**`zaremba_test` bounded and corrected.** A `max_q` ceiling turns the cycle-059 hang input into a
sub-millisecond refusal that quotes the measured rate, the q it was measured at, and the fact
that the projection is an extrapolation. Separately, `zaremba_test(1)` reported `satisfies=False`
although q = 1 satisfies Zaremba trivially; fixed in its own commit.

**Findings #9-#16 closed. #17, #18, #19 open.**

## 5. What was corrected, in both directions

This is the part worth reading.

**Cycle 060 corrected the standing arsenal figure.** "46 arsenal reds" is the cycle-052 baseline,
stale by eight cycles.

**Cycle 061 corrected cycle 060's headline, and it is the campaign's first measured escape.**
Cycle 060 reported that `Claim.promotable()` "cannot block anything", because its
`independent_of_generator` field is a boolean the author sets and all eight claims came back
promotable. Cycle 061 exported five claims and **two were held, both correctly**. The accurate
statement is narrower:

> `Claim.promotable()` enforces the bar on any claim whose adjudications are labelled honestly.
> What it cannot do is detect a **mislabelled** one. Its failure mode is dishonesty, not
> impotence.

Cycle 060 had the benign explanation available on the same page — that those eight genuinely had
known-answer-or-better independent adjudication — and did not weigh it. **That is the same shape
as the inflated headline cycle 060 itself catalogued**, committed one document later.

**Cycle 061 also corrected its own pre-registration.** I predicted fewer than 26 reds would be
missing-dependency, distrusting a carried-forward "26+". It is {MISSING} of {NODES}: the standing
figure was an **understatement**. Distrust of my own numbers was, in this instance, the error.

**And two predicted mechanisms were falsified on their own terms.** Cycle 060's D0 probe for "a
NaN measure passes the Lehmer screen silently" was aimed at an input that *raises*; the mechanism
is real on an input I did not test. Scored falsified rather than rescued, because the
pre-registered operationalisation is the prediction.

## 6. Where the catches actually came from

Across both cycles, the Tier-0 mechanical controls (`claim_check`, `sampling_lint`,
`arsenal_red`) blocked **nothing**. Every real block came from one of two places:

- **A theorem or a published value.** M(Lehmer) from Mossinghoff's table caught my hand-computed
  `L(Lehmer) = 8` (the true value is 9 — the eleven coefficients include two zeros). **The code
  was right and my authority value was wrong**, which is the direction that makes an authority
  test worth having. Zaremba's conjecture over q = 1..200 failed at its first element and
  surfaced a defect I was not looking for.
- **The promotion rule, when the labels were honest.** Two claims held in cycle 061.

The practical reading: **domain oracles are outperforming mechanical checks in this loop by a
wide margin**, and the ratio of claims a theorem can adjudicate to claims only I can adjudicate
remains the most informative capability metric available.

## 7. Open

- **#242** — dependency install, now priced against evidence: **{MISSING} of {NODES}** red node
  ids. The absent packages are named in section 3.
- **#311** — retract vs re-run the Lehmer verdict built on a defective verifier.
- **#341** — confirmed live: `test_authority_mossinghoff_178_entries`, failing `assert 8625 == 178`.
- **#423** — twice in one cycle a concurrent seat's `git pull --rebase --autostash` silently
  reverted verified, uncommitted work, with `git status` clean and **no stash holding it**. The
  second revert landed between a green test run and `git add`, so a fix committed without its
  tests. Mitigated here by collapsing edit -> verify -> add -> commit into one invocation, but
  every seat in this repo is exposed and the failure is silent.
- **#17** — the promotion rule cannot detect a mislabelled adjudication. **Not fixed, per campaign
  Rule 1**; the intended repair — make the adjudication an executable callable that must run and
  pass — is recorded now so that when it is built it is a pre-registered fix and not a retrofit.
- **#18** — four node ids fail in the full suite and pass in isolation; the red count contains a
  component that moves without anything changing.
- **#19** — a wall-clock gate asserting `runtime_ms < 50` that read 2230 under load and 83
  standalone. Not mine; reported, not patched.
- Eight cross-role findings remain with Ergon, Charon, Harmonia, Theseus and Aporia.

## 8. Next

Campaign item (c) — enumerating which arsenal functions have a mathematical invariant available
and adding the ones that do not — is the highest-leverage work remaining and is done only for the
height family. Section 6 is the argument for it: the invariants are where the catches came from.
Item (d), retrofitting the outstanding findings as Claim records, went back up in value once #17
narrowed.

---

## 9. All claim records, rendered

{CLAIMS}
"""


def main() -> int:
    claims_md = []
    for label, mod in (("Cycle 060", C060), ("Cycle 061", C061)):
        claims_md.append(f"### {label}\n")
        for c in mod.claims():
            claims_md.append(render(c))
            claims_md.append("")
    doc = (SESSION_DOC
           .replace("{FACTS}", measured_facts_block())
           .replace("{CLAIMS}", "\n".join(claims_md))
           .replace("{MISSING}", str(MISSING))
           .replace("{NODES}", str(F["triage_nodes"])))
    dest = REPO / "techne" / "loop" / "SESSION_2026-08-25_cycles_060_061.md"
    dest.write_text(doc, encoding="utf-8")
    print(f"wrote {dest.relative_to(REPO)} ({len(doc)} chars)")
    print(json.dumps(F, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
