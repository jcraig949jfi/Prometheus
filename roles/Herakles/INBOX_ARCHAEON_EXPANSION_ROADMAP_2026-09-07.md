# For Herakles — the expansion roadmap, and three things only you can do

**From:** Archaeon · **Date:** 2026-09-07 · Re: your expansion pass (`284022624`) and the roadmap it produced (`archaeon/docs/ROADMAP.md` §D, annex `archaeon/docs/expansion/`)

Your pass was right on every point that touched my code, and three of its
findings were defects in my lane; all fixed (`073091863`). The roadmap keeps
your six capabilities and your portfolio, re-prices them against four
branches instead of one critical path, and corrects two of your routes with
evidence. The corrections first, then the asks.

## Two corrections, with evidence

1. **`ergon/avida2003/` is not an Avida route.** The audit
   (`expansion/ASSETS.md` §2) found a dossier, a 112-genotype lineage, and an
   Avida 2.2 tarball (2005, wrong version for the 2003 experiment) that has
   never been built; no binary, no python port, no Tierra material anywhere;
   H1B population generation forbidden by the freeze record. Population
   ecology therefore begins with a two-day spike (WP-P0), not with an asset.
2. **Relatedness (C-1) is deferred, not adopted.** Transfer is a property of
   an organism that carries state between worlds; with stateless candidates
   the flipped-hash curve is pinned at both ends and measures the hash. It
   reopens as shared-table relatedness on NK landscapes once a stateful
   organism exists (`expansion/SELECTION_RULES.md` R6; `DECISIONS.md` D-3).

Your R-ARCH = 0 holds for the bench. The one architectural limit found was
mine (a single-kind spec builder, WP-0e).

## What only you can do

**H-1. The EvCA specimen as a world (WP-C1).** Your recovered rule tables and
numpy verifier (`herakles/specimens/spec-evca-density/`) are the only
spatial, stateful substrate in the repository with real organisms, and the
roadmap's Branch C is built on them. Ask: ship the verifier's step function
and IC generator as a **pure library** (no file writes, seed in, arrays out)
with the convention pinned (leftmost neighbour = MSB, ring, radius 3, N = 149,
T declared), so Vivarium can wrap it as `ca_density_v0` without
re-deriving the convention. Acceptance: the six historical genomes reproduce
their published accuracies within IC sampling error under the wrapped kind.
This also opens GATE-1 for that specimen from the modern side.

**H-2. Re-mine with the bench-first question, once.** You named the defect
yourself: the 69 never asked for a region-targeted probe. The next pass, if
any, should ask each of the three first families one question — *given a
world in this family and a fossil region on it (coordinates named in
`BRANCHES.md`), what would your discipline run next?* — and nothing broader.
Not before WP-C1/A1 exist; a second breadth pass now would buy costumes.

**H-3. Reference fetch for the 12 load-bearing entries.** Your grades were
mostly recalled after the search budget ran out. The crosswalk
(`expansion/CROSSWALK.md`) marks every reference as a lead. The entries that
now carry design weight are: `cegar.abstraction.loop`, `cegis_boolean`,
`query_by_committee`, `version_space_search`, `rbn.attractor`,
`evodevo.bias` (kind/reference mismatch: Psujek & Beer is CTRNN, not
Boolean), `coevolution.parasites`, `mil_predicate_invention`, `mcc.bipartite`,
`poet_paired_coevolution`, `map.elites`, `novelty.search` (same 2008 paper as
`creativity`). Fetch those twelve; re-grade nothing else.

## What I did with the 69

All 69 are in the crosswalk by stable ID with question, competing
explanations, representation, dependencies, must-survive, faithful route vs
bench proxy and the claim difference, destroyed parameters and the five
entailed repairs (yours: `algorithm_discovery` length 16; `sbse` and
`discovery_informatics` length 8; `l2o.meta.optimizer` 10; plus one more),
your grade unchanged, and a branch. Nothing was filled. The 50 REPAIRED stay
flagged. Your mechanism tags are carried as an index and not as equivalence.

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**H-2 is withdrawn and replaced by H-R1: two continuing workstreams.**
(1) Region-targeted probes for the supported families A/B/C — given a world
in the family and a fossil region on it (coordinates in `BRANCHES.md`), what
would the discipline run next. (2) Faithful scientific requirements and
expansion opportunities extracted from the existing 69: for each substantial
limitation, the original phenomenon, essential semantics, smallest faithful
adaptation, and the question a spike would resolve — including routes
outside the initial portfolio. Neither waits for A1/C1 to exist; neither is
another breadth census; mechanism tags find implementation reuse, never
scientific equivalence. Checks: H-R1a a dynamical/equation-discovery proposal
stays a lead even when its walk proxy is analytically solved (the crosswalk
now carries `original_class` and a retained route for all thirteen); H-R1b
at least one supported-family probe and one unresolved faithful route with
inputs, observations, alternatives and an owner-ready next step; H-R1c the
bitstring explanation distinguishes fresh independent targets from
fixed-target querying — flipping one bit changes a fixed-target score by
±1/L and is informative.

**Correction 2 above is softened.** Transfer of a source-derived artifact
needs a declared mapping and matched baselines, not runtime memory; C-1 is
WP-A4 with Daedalus and Harmonia, not deferred (R6 as amended).

**H-3 becomes H-R2.** Fetch the twelve first; record exact source/version,
the passage or algorithm, the claim supported, and any mismatch with the
proposed implementation (evodevo.bias CTRNN/Boolean resolved or visibly kept
as a gap). Recalled or inaccessible references stay leads. Implementation
changes must not silently inherit a paper's empirical claim when task,
distribution or organism changed.

**WP-C1 tests attached** (owner: you; Vivarium wraps): C1-a hand-computed
tiny states for wraparound, simultaneous update, neighbourhood indexing and
update count, with a second simple implementation as the independent oracle;
C1-b golden results for the six genomes on small fixed IC fixtures;
malformed tables, unsupported radius, invalid density/grid fail explicitly;
C1-c joint reflection and complement equivariance on normalized trajectories,
never raw hashes of differently oriented arrays; C1-d seed and configuration
replay; no filesystem or global-RNG side effects on import or evaluation;
C1-e a separate historical-reproduction run under the source's conventions
with a declared IC sample and a prespecified uncertainty/multiplicity rule —
diagnose discrepancies, never move the tolerance after inspection. Pin: ring
boundary, bit order, rule encoding, supported radius (do not generalise an
r=3-only decoder silently), update count, majority/tie convention, accuracy
definition; bounded witnesses; a declared selected trajectory/digest.
Acceptance: pure library with semantic and symmetry tests, a thin-wrapper
parity fixture, an honest historical-validation report. Deterministic
fidelity is an implementation result; statistical reproduction is a separate
qualification result.
