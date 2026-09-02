# Diversity demonstration — PREREGISTRATION (amendments A4, A5, A7, A8). Frozen before any run.

**What this is.** An instrument qualification. It asks whether the two signatures can tell
organisms apart at all, and it preserves the genotype-to-phenotype map for later detectors. It
does not ask whether the organisms are good, interesting, capable, or diverse in any sense a
human would care about, and no number below is a target.

**Population.** Generation 0: 2,000 organisms from the default Foundry manifest with seed =
the first 16 hex digits of the external addendum hash (a public value Proteus did not choose).
Generation 1: one child per generation-0 organism, one operator each, mutation seed = parent
index, splice mate = the next organism in generation-0 order. Total 4,000. All pass through
Foundry-local qualification first; deaths are ledgered, not dropped.

**Probe ensemble.** The frozen ensemble in `proteus/foundry/probes.py` (`DEFAULT_ENSEMBLE`):
four probes derived from the addendum hash, 1..3 input and output channels, 3..6 ticks, 0..3
uniform 32-bit values per channel per tick, budget cap 256 ops per tick. Its identity hash is
recorded in `CONFIG_IDENTITY.json` before the run.

**Signatures.**
- `transcript_class`: sha256 of the externally visible transcript (outputs per channel per
  tick, and the tick status). The relation is `probe_transcript_equivalence`. Nothing else.
- `knockout_vector`: for each of the nine opcode classes, `-` if absent from the genome, `1` if
  rewriting the class to NOP changes the transcript, `0` if it does not.

**Alphabet, floor, ceiling, stated before measurement.**
- Transcript classes: floor 1 (every organism identical on the probes), ceiling 4,000.
  Entropy floor 0 bits, ceiling log2(4000) = 11.97 bits.
- Knockout vectors: floor 1, ceiling min(3^9, 4000) = 4,000 patterns; entropy ceiling 11.97 bits.
- The `silent` class (no output on any probe, whatever the status sequence) is reported by
  size because it is the class most likely to dominate a uniform-random population. Its size is
  a fact about uniform initialisation, not a defect.

**Instrument qualification criterion, the only pass/fail here.** The instrument is qualified if
transcript classes > 1 AND knockout vectors > 1 — that is, each signature can distinguish at
least two organisms. Anything above that is reported, not judged. There is no diversity target
and, per A8, nothing in the configuration is changed after the numbers are seen.

**Degeneracy map (A7), preserved per transcript class:** class id; number of distinct genomes;
lineage ids; number of member pairs that are parent-child versus unrelated lineages; the
distribution of knockout vectors within the class. Written as rows, never summarised away.

**Also reported, ungated:** the number of generation-1 children whose transcript class differs
from their parent's (a one-mutation transcript-change rate), broken down by operator; the
per-class size distribution; the fraction of organisms with budget-exhausted ticks.

**Not used.** `roles/Diomedes/coordinate_census.py` is not run and not reported (A5).

Configuration identity (`CONFIG_IDENTITY.json`) is written before the run and the runner refuses
to run if it already exists with a different content. A second run under a changed configuration
is a new file, a new identity, and a new demonstration.
