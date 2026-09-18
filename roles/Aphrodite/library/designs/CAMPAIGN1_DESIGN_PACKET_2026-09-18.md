# Campaign 1 design packet (DRAFT for the operator; TIER 3; execution NOT authorised)

SUPERSEDED 2026-09-18 by CAMPAIGN1_DESIGN_PACKET_v2_2026-09-18.md (after the
operator's directive on 0B, Campaign 0C and the benchmark harness). Kept as written.

Currency: 2026-09-18. Requested by the operator's Campaign 0 disposition
("Next deliverable: Campaign 1 design packet with substrate choice, real
compute budget, lineage economics, frozen delta, and explicit statement
of which claims remain powered if fewer than 64 independent lineages are
affordable"). Inputs: Campaign 0 (PASS, tier 2), Campaign 0B (FAIL on
power under jackpot structure, calibration intact, tier 2),
RSI_PROGRAM_v2 (tier 3). Every number from C0/C0B is tier 2: a property
of the assay under a model the seat wrote. Items marked OPERATOR are
decisions this packet cannot make.

## 1. The question and the resolution floor, stated up front

Campaign 1 asks whether an evolved improvement operator transfers to
fresh agents on sealed task families at matched compute. The assay's
floor is ~4.7 points of held-out tasks solved at L = 64 (~7.1 at 32,
~9.6 at 16). Campaign 1 will therefore report one of:
  TRANSFER DETECTED (above the floor), EQUIVALENT (no transfer larger
  than delta, if powered), or BELOW RESOLUTION (no detection, and
  equivalence not established) -- and never collapse the third into
"no RSI". This wording is part of the preregistration.

## 2. OPERATOR decision 1: the estimand (new, forced by Campaign 0B)

  E-mean   "the typical evolved improver transfers" -- what the qualified
           assay measures. Under jackpot structure (10% of lineages
           carrying the gain) it finds real transfer only 25% of the time
           at L = 64.
  E-exist  "evolution produces transferable improvers in at least some
           lineages" -- needs a SCREEN-AND-CONFIRM stage (top-k lineages
           re-tested on fresh sealed tasks), NOT yet qualified; qualifying
           it is a Campaign 0C step (CPU, same worlds + P1-P3) before any
           GPU.
Seat's lean: preregister BOTH, E-mean primary (qualified), E-exist
secondary once 0C qualifies it. Hyperagents' positive transfer is an
E-exist-style result (5 runs, best agent per run), which is one reason
the two literatures may disagree.

## 3. OPERATOR decision 2: delta (the equivalence margin)

Define it first in task units: "X points of held-out tasks solved at
fixed compute is the smallest difference worth calling meaningful".
What each choice buys (C0B delta table, tier 2):
  delta 2 pts: equivalence shown in the null 0 / 1 / 41% (L 16/32/64);
               specialisation recoverable 3 / 7 / 39%.
  delta 3 pts: 6 / 45.5 / 87%; specialisation 5 / 46 / 92%.
  delta 5 pts: 63.5 / 94 / 99%; specialisation 49 / 96 / 100%; but
               4-5-point real effects are classed TRIVIAL (MDE at L 64
               becomes 7.1 points).
Seat's lean: 3 points, IF L = 64 is affordable; if only 32, 5 points
with the explicit statement that effects under 5 points are declared
not meaningful. The seat does not set it.

## 4. OPERATOR decision 3: substrate and host

Options (none measured on our hardware; all labels ASSUMED):
  S-a  one small open model (1.5-8B, 4-bit) on the M1 and M2 RTX 5060s
       via a batched server; cheapest; the substrate-transfer arm needs a
       second model family of similar size.
  S-b  the same on RunPod (larger batch throughput, dollar cost).
  S-c  a hosted API model (no GPU; token cost; metering by the provider's
       counts plus our proxy).
The assay needs: an external meter below the improver (tokens in/out per
call, per resource handle), sealed task generators, and 64 independent
lineages. Seat's lean: S-a for Campaign 1, because Prometheus owns the
metering end to end; first measure throughput on M1/M2 (a benchmark, not
an experiment -- needs the operator's go since it is a model-host
deployment).

## 5. Lineage economics (PARAMETRIC; ASSUMED throughputs; 8 generations)

Total tokens = L x (8 x E x T + 1,760 x T), E = task evaluations per
lineage per generation during evolution, T = tokens per task evaluation;
2-GPU-days at an aggregate 500 or 2,000 tokens/s per GPU:

    T (tok/task)  E/gen   L=16          L=32          L=64
    2,000         200     1.2 / 0.3     2.5 / 0.6     5.0 / 1.2
    2,000         1,000   3.6 / 0.9     7.2 / 1.8     14.5 / 3.6
    10,000        200     6.2 / 1.6     12.4 / 3.1    24.9 / 6.2
    10,000        1,000   18.1 / 4.5    36.1 / 9.0    72.3 / 18.1
    30,000        200     18.7 / 4.7    37.3 / 9.3    74.7 / 18.7
    30,000        1,000   54.2 / 13.6   108.4 / 27.1  216.9 / 54.2
(each cell: 2-GPU-days at 500 / 2,000 tokens/s/GPU). Screen-and-confirm
(E-exist) adds a second evaluation of the top k lineages: small next to
evolution. Reading: L = 64 is affordable on two local GPUs ONLY with
short procedural tasks (~2k tokens) and a lean evolution budget; long
agentic tasks at L = 64 need RunPod or months.

## 6. What stays powered below 64 lineages (explicit, from C0/C0B, tier 2)

  L = 32: TRANSFER (0.985; 0.885-0.965 under heavy tails / sign-changing
          families), MEMORY (0.99), TRANSFERRED MODULE (0.975), WORKER
          (0.985), nulls calibrated; MDE ~7.1 points.
          NOT powered: COMPUTE-cheat contrast (0.84; the meter still flags
          overspend directly), SPECIALIZATION (0.505), MIXED causes (0.69),
          EQUIVALENCE at delta 3 (45%). A 32-lineage Campaign 1 makes no
          claim about specialisation or mixed causal structure (operator's
          qualification) and reports null results as BELOW RESOLUTION.
  L = 16: only WORKER transfer and null calibration are reliable; TRANSFER
          0.795; MDE ~9.6 points. Not recommended.
  Any L:  jackpot-structured transfer is NOT powered under E-mean (0.26
          at L = 64).

## 7. What Campaign 1 reports (operator's fourth qualification)

No exact flag-set classification. Each causal contrast (D_VAULT, D_DEV,
D_MEM, D_WORK, D_COMP, ASRUN, module necessity/sufficiency) is reported
with its estimate, 95% and 90% intervals, Holm-adjusted p, TOST p and
Lakens verdict, lineage-level rows attached; plus the frontier across
three budgets; plus the lineage-value distribution (so jackpot structure
is visible, not averaged away).

## 8. Before any GPU: remaining gates

1. OPERATOR: estimand (s2), delta (s3), substrate/host (s4), L and
   budget (s5-s6).
2. Campaign 0C (CPU, tier 2): qualify screen-and-confirm if E-exist is
   adopted.
3. Throughput benchmark on the chosen host (needs the operator's go).
4. APHRODITE-31: whether Aphrodite may ask Archaeon (sealed generators),
   Harmonia (meter), Vivarium (sandbox) for their parts.
5. The Campaign 1 preregistration itself, with all of the above frozen.
Campaign 1 execution remains NOT AUTHORISED.
