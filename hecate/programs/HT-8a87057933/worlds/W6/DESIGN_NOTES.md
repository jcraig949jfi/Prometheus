# HT-8a87057933 / W6 -- design notes (Pass 3 v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md. Layer: speculation
plus control rows only; no treatment code, no treatment statistic.

## What the world tests

M4 (Yoneda probing), read through L3 (version-space count). A plant is one of
64 single-component faults; it is known only by its responses to excitation
probes (probe p answers 1 iff the fault is in E_p). The treatment picks probes
from a minimum separating family of the candidates still consistent with the
data (an exact hitting-set solve). The claim tested: this identifies the plant
at parity with greedy information gain (S1, <= 1.05 x greedy mean), well under
9 probes on average (S2), with a bounded worst case (S3, p95 <= 8).

## Why the claim is parity, not superiority

The first version (rev 1) asked the treatment to BEAT greedy by 5%. The
controls showed greedy information gain averages 6.019 probes against the
entropy bound of 6.0 that binds every policy not knowing the truth. The 5.718
bar was reachable only by the truth oracle. That is the same defect as the
earlier M4/M5 world, where the positive control met clauses no real policy
could. A legitimate-policy feasibility check (S1 bar >= entropy bound) is now
part of the freeze condition in controls.py. Superiority over greedy in mean
probes is impossible on this substrate. That is a finding about M4's
distinguishing observable, recorded here, not hidden.

## Why it avoids the earlier failures

- The earlier world's version space collapsed in 2-3 observations for any
  policy, so probe choice could not matter. Here probe subsets have mixed size
  (2 to 32 of 64), and random probing needs 13.2 probes on average (p95 23)
  against 6.0 for greedy: probe choice matters a lot.
- No success clause references the null twin, so the twin check is not
  self-referential. Clauses use GREEDY_REF (rerun in the same code path) or
  absolute numbers.
- Success and failure regions are disjoint (rev 3): meeting S1 means mean <=
  6.32, so F1 (>= 1.15 x greedy), F2 (>= 0.75 x twin = 9.89) and F3 (p95 >= 10)
  cannot also hold.
- The cheat is caught by recomputation, not by a threshold: every row carries
  its (probe, response) trace, and replaying it against library and truth
  reproduces the observable for every honest row (0 mismatches in 1920) and
  fails for all 640 cheat rows.

## Control values (10 libraries x 64 truths per arm, 0.16 CPU core-seconds)

| clause | positive control (oracle) | null twin | bar | greedy ref |
|---|---|---|---|---|
| S1 mean ratio to greedy | 0.389 | 2.190 | <= 1.05 | 1.0 |
| S2 mean probes | 2.34 | 13.18 | <= 9.0 | 6.02 |
| S3 p95 probes | 3 | 23 | <= 8 | 6 |

## Ambiguities resolved

1. "Hitting-set SAT instance so every pair of remaining candidates is
   separated": read as an exact minimum-cardinality separating family over the
   current version space, re-solved after each response; the probe applied is
   the lowest-index member of that family that splits V. Stated in
   spec.mechanism. A non-adaptive reading (fix the whole family up front) is
   the implementer's to report as a variant only, not the treatment.
2. Tie-breaking: lowest probe index in every policy. Probes are exchangeable
   by construction (i.i.d.), so the index carries no information.
3. Probes are never repeated (a repeat carries no information in a noise-free
   plant); applied to every arm.
4. Libraries are regenerated until separating, so every episode terminates
   with |V| = 1; the twin cannot run forever (max 38 of 48 probes observed).
5. The truth oracle is an upper bound, not a legitimate policy; attainability
   by a legitimate policy is argued from the entropy bound and from greedy
   itself meeting S1 to S3.

## What a result would and would not mean

A SIGNAL shows only that exact separating-family probing matches greedy
information gain and beats random: M4 at most equals its simpler alternative
here. The category-theory (Yoneda) framing adds a name, not a mechanism
(program.json already records that knockout as weak). The cleaner outcome is a
failure: a minimum separating family is a worst-case object and may spend
probes an adaptive greedy rule skips (F1).
