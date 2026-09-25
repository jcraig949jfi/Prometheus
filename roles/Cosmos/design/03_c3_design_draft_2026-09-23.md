# C3 -- causal accessibility of past information -- DESIGN DRAFT (not a preregistration)

Currency: 2026-09-23. Source direction: roles/Cosmos/prompts/2026-09-23_operator_c0_review/ (verbatim).
C0 is CLOSED at af2af37f4 and is not refined further. C3 is a new scientific campaign. This file is a
draft for the operator to cut; the preregistration is written only after the open decisions in s9 are
settled, and before any C3 observation.

## 0. What C3 asks

Do apparently different mechanisms collapse onto a substrate-independent quantity governing the
CAUSAL ACCESSIBILITY OF PAST INFORMATION, and does that quantity predict an untouched foreign substrate?
Success is not "another equation". A null ("no substrate-independent quantity found") is a result.

## 1. What changes from C0, and why (C0's lessons as constraints)

| C0 weakness (packet s7 / review Q1-Q5)                   | C3 constraint |
|---|---|
| the law was the planted economics of hand-written players | no planted economy: no reward/cost coordinates written by the substrate author; systems' retention is NOT hand-coded (s3) |
| the substrate author declared the universal coordinates  | COORDINATE FIREWALL: authors expose native observables and units only; cross-substrate coordinates are proposed by Cosmos from VISIBLE families and audited (s5) |
| fixed tolerances (0.10 margin, 0.10 log2)                | tolerances derived from replicate uncertainty / finite-size scans, preregistered as rules, not numbers (s6) |
| three sealed universes spent on one relation             | holdout ration: A+B+C -> D (development, used once) -> freeze -> E (final, untouched; no rescue) (s7) |
| samplers unearned                                        | random sampling only; no sampler development (review Q5) |
| one author for every substrate                           | D and E written AND sealed by other seats; Cosmos never sees their code or native definitions before adjudication |

## 2. The phenomena, separated (review: three questions, measured in order)

P1 PERSISTENCE: information about history H_{t-k} that is absent from the current observation O_t is
   present in system state S_t:  I(S_t ; H_{t-k} | O_t) > tau.
   Estimator: cross-validated DECODABILITY (a lower bound on the conditional MI): decode H_{t-k} from
   (S_t, O_t) versus from O_t alone, held-out episodes; tau from a permutation null (histories shuffled
   across episodes with O_t fixed). Discrete histories keep the estimator simple and exact enough.
P2 CAUSAL UTILITY: that information improves later behaviour:  J_intact - J_history-ablated > eps.
   HISTORY ABLATION by interchange: at time t, replace the system's state with the state from another
   episode that has the SAME current observation O_t but a DIFFERENT history (snapshot/restore;
   BEE ext.snapshot.v1 is the donor idea). eps from the replicate distribution of J (paired, CRN).
P3 ADVANTAGE (a pressure law): under which conditions retention pays. DEFERRED until P1 and P2 are
   measured and certified across substrates; C0 showed how easily P3 becomes the author's economics.

Certificate classes per system: NONE (neither) | PASSIVE (P1 without P2: history encoded but causally
unused) | FUNCTIONAL (P1 and P2). The PASSIVE class is the cheat control C0 lacked: persistence is not
memory unless it is causally used.

## 3. Systems and substrates

Systems are NOT hand-written retention programs. Per substrate, a parameterised family of dynamics in
which retention may or may not arise: e.g. random or trained recurrent maps, graph-diffusion networks,
agents that may mark an environment. The functional DEMAND is shared (an observation occurs, is
removed, later behaviour could benefit from it); the MECHANISM is whatever the dynamics does.
Visible families (Cosmos-written, three lineages, different retention loci):
  A  explicit internal state (e.g. a small recurrent controller; weights drawn or trained)
  B  distributed graph dynamics (information held, if at all, in network activity patterns)
  C  environmental / stigmergic state (agents keep nothing; they may mark the world and read it back)
Sealed, foreign:  D (development) and E (final), written and sealed by other seats (s9, D1).

Substrate contract (C3): run episode; expose native observables and units; snapshot(t) / restore(t)
of the FULL causal state, including any environment the system can write to (C) -- without this the
interchange ablation is undefined; declare what "the system" vs "the world" is (for C that boundary
IS the question and is declared by the author, then attacked).

## 4. Substitution attacks (required)

Remove the explicit internal retention channel (A: zero or reset the recurrent state; B: cut
recurrent edges; C: forbid marks) and ask whether the SAME functional demand is met through another
channel: environment modification, recurrence elsewhere, communication between units, predictive
recomputation from what remains observable, population state. Measure P1 and P2 on the enlarged state
(system + world). The candidate upward abstraction, stated to be falsified:
  "future-relevant information must remain causally accessible across the interval in which direct
   observation is unavailable" -- i.e. what matters is accessibility, not the locus.

## 5. Coordinate firewall

Authors provide native observables and units only. Cosmos proposes candidate cross-substrate
quantities using VISIBLE families only (e.g. a causal-accessibility measure: interchange effect size
per bit of decodable history; decay of decodability with k; channel capacity of the retention path),
freezes them, and asks Harmonia (independent audit) whether any candidate encodes implementation
knowledge (does its value track substrate identity or author choices, and does it survive a
relabelling/metamorphic battery?). A quantity that fails the audit is withdrawn before D.

## 6. Tolerances from uncertainty

Every threshold is a rule computed at run time from preregistered replicates: tau = the 99th
percentile of the permutation null of decodability; eps = 3 x the paired SE of J; location / law
tolerances = the finite-size width measured by boundary scans at two episode counts. The prereg fixes
the RULES and their attainable resolution (computed before freezing), not bare numbers.

## 7. Holdout protocol

D: a development holdout, sealed by another seat. Used ONCE, after the visible campaign froze its
candidate quantity and law; its purpose is to find out whether the chamber is broken. Anything changed
after D is post-holdout development and is labelled so.
E: final adjudicator, sealed by another seat before C3 starts, touched once only after the final law
AND a quantitative intervention prescription are frozen. If E fails there is no C3b on E.

## 8. Build order (smallest first; each with planted controls)

C3-0  certificate module (decodability + permutation null; interchange ablation; J with CRN) and its
      planted calibration: a known-FUNCTIONAL system, a PASSIVE system (history encoded, never read),
      a NONE system, and a cheat (behaviour reads the future-relevant variable from the world directly)
C3-1  visible substrates A, B, C with snapshot/restore of the full causal state; substitution switches
C3-2  certification maps over each family (P1, P2 across parameters); candidate quantities; Harmonia
      audit; freeze
C3-3  D once; freeze the law + prescription; E once. Review packet whatever happens.

## 9. Open decisions (operator's call)

D1  Which seat(s) write and seal D and E? (Must not be Cosmos; must not see Cosmos's candidate
    quantities before sealing. Suggested: two different seats, one per holdout.)
    Prompt ready: roles/Cosmos/prompts/2026-09-23_c3_foreign_substrate/.
D2  Does Harmonia accept the coordinate-audit role (s5)? Prompt ready:
    roles/Cosmos/prompts/2026-09-23_c3_harmonia_audit/ (not posted until candidates exist).
D3  Time box and compute envelope for C3 (C0 used ~6.5 h of one M2 CPU box; C3-0/1 is similar;
    trained systems in A could need the GPU -- that would be a new substrate, not acceleration).
Cosmos's lean: D1 = two different seats that have written substrates before; D2 = yes; D3 = two
sessions, C3-0/1 first with a review packet before any holdout is created.
