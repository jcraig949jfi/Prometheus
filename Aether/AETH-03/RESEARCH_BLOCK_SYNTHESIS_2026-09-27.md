# Aether research block, 2026-09-27 — program-level synthesis (Block J)

Directive: `roles/Aether/prompts/2026-09-27_research_block/DIRECTIVE.md`.
Campaign: `ops/campaigns/C-002/` (Thread TH-007). Everything below points
to a committed record; nothing here is new evidence.

## ASSAY — did the exact causal-generation argument hold?

**Exact after repair; prior verdicts unchanged; one claim withdrawn.**
Locality holds under every attack (27,000 light-cone flips; hash keys are
state-free; `rcv`'s hidden flag was already in the predicate, and a
bytes-only predicate breaks without it — 32 violations vs 0). The claim
"generation = the exact shortest causal chain" did not hold: a differing
neighbour need not be a cause. Adjacency generation is a lower bound,
equal to counterfactual causal generation in 84-100% of 2,793 audited
events, so every prior secondary/sustained claim was conservative.
(`PROPAGATION_ASSAY_AUDIT.md`)

## SCIENCE — what changed

1. **`rcv` is a calibration law.** Its propagation is its own rule (96% of
   secondary differences are the two quantities the rule moves), damped by
   v1's costs, amplified 4.8x by injected noise, and it runs on a frozen
   map: the same origin flipped at three different times reaches exactly
   the same sites, because ~93% of template bytes never change without
   noise. (`RCV_REINTERPRETATION_2026-09-27.md`)
2. **Locality does not depend on horizon.** Twenty times the horizon
   (500 → 10,000 ticks) changed no conclusion for any law without injected
   noise. (E-005)
3. **Interactions are real, and they are not content transport.** Two of
   three pairwise combinations of already-understood rules pass a
   preregistered super-additivity bar in every seed: `rcv_add` (activity
   leaves permanent marks) and `rcv_str` (activity re-routes later
   activity through energy-steered aim — the conversion injected noise
   performed for `rcv`, done by the substrate). A cause probe shows neither
   carries the origin's content. The one-change rule was hiding
   interactions; the interactions it hid are "history matters" primitives,
   not communication. (PHYSICS_DESIGN_03 §5)
4. **An instrument limit found by its own control:** the content signature
   detects transport in a clean relay but not in a rich soup, even for a
   law that forwards bytes by construction (E-P1 failed). A value-provenance
   detector would be needed.

Open: the 10,000-tick falsifier for `rcv_add` / `rcv_str` (lost to a
memory-pressure kill plus a resume defect, now fixed; not re-run without
the operator).

## DISTRIBUTED WORK — what ran away from BUCKKEEP, and what it took

Ran off BUCKKEEP, on RunPod pods used as disposable Linux CPU executors:
the 6 known-answer units in each of 3 flights (18 executions), 8
long-horizon units at 10,000 ticks (plus 16 at 1,000 ticks inside two
scouts), and 72 combination units — 114 unit results returned, each
verified by sha256 against the pod's own manifest; 4 more (the d_horizon
falsifier) executed and were lost to the resume defect. 4 combination
units were also run on BUCKKEEP as cross-host duplicates. Every pod was
confirmed absent by LIST and GET and by an independent inventory read.

What portability actually required (all observed; C-002 findings 1-3):
code addressable by pushed commit; line-ending-normalised code hashes
(CRLF vs LF made raw hashes of the same commit differ); a result hash that
excludes host and time; parameters as the only inputs (Aether needs no
data files, so C-001's "evidence only on one disk" barrier never arose);
the orchestrator committing for executors; a progress signal written only
when work advances (two campaigns aborted by the stall detector before
this); concurrency sized from the container's CPU quota, not the host's
core count (a pod reported 96 cores and allowed 7); a second host to catch
a silent 0 MB memory probe. The Linux nodes (ubu001/002) were unreachable
from BUCKKEEP (no SSH key) and no credential was added.

## CAMPAIGN MODEL — what the two lanes taught

- **Known-answer lane** (E-007): 6 tasks, 19 attempts on 4 hosts (Windows,
  Linux; Python 3.11/3.13; NumPy 1.26/2.4), 0 disagreements. It found
  every mechanical problem cheaply and unambiguously: the expected answer
  comes from committed evidence, so dispatch, duplicates, missing units and
  determinism are states, not judgements. The reducer refuses a verdict on
  an incomplete battery (tested). Scouts produced free duplicate attempts.
- **Open-science lane** (E-005, E-006): it surfaced what the known lane
  could not — preregistered positives that then needed falsifiers the plan
  did not contain; a failed control that exposed an instrument limit; a
  lost artifact behind a PASS receipt (the platform kept only ≤ 1 MiB); a
  post hoc probe that changed the interpretation; new Threads. None of
  that fits a Task row; it lives in RESULT files and Threads.
- **Lesson for the model:** Task/Attempt is the right shape for units with
  an identity (inputs → result hash); Experiments need room for
  interpretation that happens after Tasks finish; a PASS at the Attempt
  level (process exit, receipt OK) is not a science PASS — the reducer
  and the result file are.

## PLATFORM — ready for other Prometheus work?

**Closer, not yet.** It flew another seat's suite unmodified (Ananke, 139
passed) and 98 Aether units off-host; costs now reconcile against provider
billing within ±8% for settled flights. This block fixed three real
defects the flights exposed: artifacts > 1 MiB were verified then silently
dropped (now kept outside the repository and receipted); a module sized
work from the host's core count (the wrapper fix is Aether's, the lesson
is general); `--resume` used a default module instead of the ledger's
(now refused). Still blocking asset status (TH-012): it lives under
`Aether/`, imports its client from an AETH-01 directory, only BUCKKEEP
holds the key, and billing settles with a lag (reconcile after ≥ 1 hour).

## ENGINE LENS — what Aether uniquely contributes

A level below programs: whether a local law lets a difference travel,
persist or combine, measured exactly (one-bit twins, checked locality,
counterfactual parents), with every effect attributable to one written
rule on a code path proven identical to the baseline. Its best
contribution this block was as much instrument as substrate: an assay
that caught its own overclaim, and a known-answer benchmark for the work
model. (`Aether/AETHER_ENGINE_CARD.md`)

## FRONTIER — continue, modify, preserve, transfer, retire

| line | decision | why |
|:--|:--|:--|
| single-change search around B-balanced v1 | **retire** | eleven laws; the medium freezes; no content moves |
| `rcv` | **retain as calibration** | known mechanism; tests any new assay |
| interactions (`rcv_str`, `rcv_add`) | **continue, narrowly** | the first super-additive, noise-free "history matters" effects; finish the horizon falsifier first |
| the frozen-medium problem | **modify the search to start here** (TH-009) | every propagation result ran on a fixed map; a law whose dynamics rewrite the medium is upstream of content transport (TH-008) |
| energy / parameter regime | **open** | only one regime was ever run; the frozen medium may be a property of B-balanced energy |
| known-answer lane | **preserve as a Prometheus benchmark** (TH-010) | cheap, exact, cross-host; tests machinery without asking science to |
| one-bit twin + counterfactual parents | **transfer** (TH-011) | a general causal instrument for deterministic engines |
| RunPod platform | **transfer out of Aether** (TH-012) | it is becoming a program asset |

**Is Aether still creating North-Star information?** Yes, at a narrower
width than its founding ambition: it is now telling Prometheus precisely
which primitive ingredients do NOT produce causal reach (and why), that
interactions matter where single changes do not, and that the medium's
own mobility is the next gate. Its instruments are at least as valuable
as its substrate right now. The recommendation is to keep the physics
search small and targeted at TH-009 while exporting the instruments —
not to widen the law search, and not to retire the substrate.

Threads created (parked, not started): TH-007 (the Aether question),
TH-008 (content on a mutable medium), TH-009 (the frozen-medium problem),
TH-010 (known-answer benchmark), TH-011 (instrument transfer), TH-012
(platform as an asset).
