# REVIEW 2 -- adversarial review of REVIEW_2_CLAIMS.md (R2-1 .. R2-5)

Reviewer: independent, no prior context. Checkout: ~/Prometheus-worktrees/rev2 @ 49abd0da4.
Everything below was re-executed on the committed data (th013_out.json, th013_analysis.json, th015_out.json) with the frozen VM
(archaeon/z80atlas/vm.py). I did NOT re-run the 70-minute replay. Scripts are in ~/wk/rev2/out/ (h.py, r5.py, r5min.py,
r5zero.py, gate.py, ko.py). The key snippets are copied into this file.

Shared helper (~/wk/rev2/out/h.py):

```python
import json, sys, random
sys.path.insert(0, '/home/jcraig/Prometheus-worktrees/rev2')
from archaeon.z80atlas import vm
from archaeon.lineage import core as LC
from archaeon.attribution.probes.th013_block13 import ALLOWED, G
from archaeon.attribution.probes import th015_archaeon as P
D = '/home/jcraig/Prometheus-worktrees/rev2/ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/'
d = json.load(open(D+'th013_out.json'))
F = bytes.fromhex(d['founder']['tape'])
def trace(t, x, pc0=0, nbr=LC.ZERO):
    return vm.execute(t, nbr, (x,), LC.STEP_CAP, True, -1.0, pc0)
```

## What I checked first, and what held up

- Material ids are NOT assigned by byte matching. `core.attribute` (archaeon/lineage/core.py:192-222) passes ids along the
  taint-VM data flow: ('E',p) -> executor.orig[p]. Every copy-noise change gets a fresh MUT id (core.py:199-200), and so does every
  background mutation (core.py:155-159, only where `new[p] != g[i][p]`). So "founder material at a displaced locus" means the byte
  was physically copied from the founder's locus q. The offsets are not an artefact of the attribution method.
- Aligned byte state agrees exactly with the material labels. For every capable member's full-scan machinery, I aligned each member
  by its modal founder offset and compared its bytes with the founder's. The founder-id fraction and the aligned-byte-identity
  fraction are identical: 0.85/0.85 (14,300), 0.63/0.63 (15,000), 0.55/0.55 (16,000), 0.57/0.57 (17,500), 0.41/0.41 (19,000),
  0.33/0.33 (19,900). There are no back-mutations and no silent relabelling. The decline of founder material is a real change in
  sequence, not a bookkeeping effect.
- Sampling is not biased by lineage structure. N = 128 and the lineage holds 124-128 cells from 14,400 on. "First 12 by cell
  index" is therefore cells 0..11, which is effectively arbitrary. The sample is 12 of about 125 cells, though. Every per-snapshot
  fraction carries a binomial SE of about +/-0.1-0.14. Snapshots are also autocorrelated: cells 0..11 are resampled every 100
  epochs.

---------------------------------------------------------------------------------------------------------------------------------

## R2-1. "0.0 founder material" is REFUTED

**Plain restatement.** The deep-block note said that, in the dominant block-13 lineage, no founder DNA remained at the founder's own
positions. It inferred that identity by descent had turned over completely. R2-1 says that inference is false: founder-derived
bytes are present at shifted positions (about 58% of the genome at 14,200, and all of the essential loci at 14,300). They then
decline to about 3 of 32 bytes.

**Hidden assumption.** "Founder material" is identity by descent from ONE ancestral genome, and positions are compared without
alignment. In standard terms this is a positional-homology error: the deep-block metric compared unaligned sequences after an
indel-like shift. "Refuted" is aimed at the wrong target.

**Attack 1: the number that was actually measured is reproduced, not refuted.**
- The deep block measured on 2026-09-27 at epoch 14,800 (block13_probe_out.json: glin 1071, founder 448863, 127 members, all 32
  positions 0.0).
- TH-013 is the same glin and the same founder. Its same-position metric at 14,800 is also 0.0 (th013_analysis.json rows,
  `founder_material_same_pos` = 0.0 from 14,200 on).
- What is refuted is the INTERPRETATION ("identity by descent turns over completely"), not the measurement.
- R2-1's own wording ("the ... claim (same-position metric) is REFUTED") says the opposite of this.

**Attack 2: the claim quotes the wrong epochs.** The deep-block claim was about epoch 14,800. R2-1 answers it with 14,200 (58%)
and 14,300 (100%), before the claim's own epoch. At 14,800 the replay gives:
- founder material anywhere on the tape: 0.32 (12 sampled members);
- founder share of the essential loci: 0.667, from ONE member (th013_analysis.json, 14,800 row).
Those figures still refute "0.0 / complete turnover", but they are the ones that should be quoted.

**Attack 3: "100% of the machinery at 14,300" is a 2-member number.**
- Across all 11 capable sampled members at 14,300, using full-scan knockout per member, founder material makes up 0.85 of the
  essential loci (88 loci total), not 1.00.
- The 2-member estimate is the first 2 cells.

**Attack 4: "machinery" depends on the knockout value, so every "share of machinery" number is conditional on it.**
- M is defined by knocking each locus out to 0x00 (th015_archaeon.py:47). In this VM, 0x00 is NOP, and so is any byte with
  (b & 31) in {0, 30}.
- Knocking out to 0x00 therefore cannot detect an essential NOP. Late tapes contain long runs of 0x00.
- With random-value knockout (a locus counts as essential if >= 8 of 16 random replacements abolish births), the essential sets are
  larger. Snippet ko.py:
  * 15,100: 11 -> 17 loci; 4 of the missed loci are NOP-valued.
  * 16,100: 11 -> 17.
  * 17,900: 6 -> 10.
  * 18,900: 8 -> 11.
- At 17,900 the founder share of the essential loci is 3/6 = 0.50 under 0x00 knockout, but 3/10 = 0.30 under random knockout.
- TH-013's "machinery shrinks ... to 5-7 loci" is partly produced by this knockout choice.

```python
# ko.py
from h import *
t=json.load(open(D+'th015_out.json')); rng=random.Random(3)
for r in t['rows'][::4]:
    T=bytes.fromhex(r['tape']); M=r['M']; Mr=[]
    for p in range(G):
        kill=0
        for _ in range(16):
            t2=bytearray(T); t2[p]=rng.randrange(256); kill+= not P.run(bytes(t2))[0]
        if kill>=8: Mr.append(p)
    print(r['epoch'],'M(0x00)',M,'M(random)',Mr,'NOP-valued missed',[p for p in Mr if p not in M and T[p]&31 in (0,30)])
# 15100 M(0x00) [6,11,13,14,15,16,17,18,26,28,31]  M(random) [2,3,4,5,6,7,10,11,13,...,31]  missed [2,4,5,10]
# 17900 M(0x00) [0,6,15,16,17,18]                  M(random) [0,3,6,10,13,14,15,16,17,18]
```

**Re-derived:**
- founder material anywhere on the tape: 0.5755 at 14,200, and 36/384 = 3/32 per member at 17,500-19,900;
- machinery share (2 members): 1.0 / 1.0 at 14,300, and 0.333 / 0.30 at 19,900.
All match the file.

**Verdict: STANDS WITH CORRECTION.** The correct statement is: "At 14,800, the epoch the deep block measured, the same-position
0.0 is reproduced. It is an unaligned comparison and does not measure turnover. With alignment, 0.32 of the genome, and about 0.6
of the essential loci, are still founder-derived. Essential-locus shares depend on knockout by 0x00 (NOP) and are upper bounds on
the founder share of the essential set."

---------------------------------------------------------------------------------------------------------------------------------

## R2-2. The machinery relocated "as a unit" by offset copying; both position-fixed material and position-fixed state are wrong units

**Plain restatement.** The copies carry shifted versions of the founder genome: extra leading bytes are added and the tail is
truncated. So the functional region sits at different absolute addresses in descendants. Any comparison at fixed addresses
therefore reads 0, whether it compares descent labels or byte values.

**Attack 1: the unit that moved is the whole retained founder segment, not the machinery.**
- Every member has exactly ONE offset for all its founder bytes, cargo included. Per-member offset histograms:
  * 14,100: {-3:25}, {-7:21}, {-4:23}, ...
  * 15,500: all {-9:7}.
- The mechanism is visible in the tapes. Descendants carry a growing run of constant 0x00 at the front: 14,300 members start
  "0000000000002700000000 2835581410fd...".
- The founder's copy loop writes zeros ahead of the copied segment and drops tail bytes. Since 0x00 is NOP, the program still runs
  from pc 0 down a NOP run.
- In standard terms: a terminal insertion plus a terminal deletion, i.e. a frame shift of the entire genome. "Relocated as a unit"
  suggests the functional module moved selectively. It did not. The whole genome moved, and the module came along with it.

**Attack 2: "-5, then -8/-9, then -11" is not the trajectory of one unit.**
- 14,100-14,300 hold standing variation: 12 members carry 8 (14,100), 11 (14,200) and 4 (14,300) distinct offsets, ranging
  from 0 to -15.
- The modal values quoted are summaries of a diversifying population, not steps of one lineage.
- Only the later history is a sequence: -9 fixed by 15,500 (12/12), then a -11 variant swept (10/12 at 16,000, 12/12 at
  16,500).
- Without per-member genealogy, the claim cannot show that the -11 at 16,000 descends from the -9 clade rather than from the -11
  class present at 14,200-14,300.

**Attack 3: "fixed-position STATE is also the wrong unit" is a non-sequitur.**
- The wrong thing is the FRAME (no alignment), not state versus material.
- Once aligned, byte state tracks descent perfectly here (0.85/0.85 ... 0.33/0.33, above).
- The IBD-vs-IBS contrast in the TH-013 diagram therefore adds nothing. Alignment is enough; this is standard sequence-homology
  practice, not a new finding about units.

**Re-derived:** modal offsets per snapshot (from the file) -5 (14,100), -8 (14,200), -9 (14,300 ... 15,500), -11 (16,000 ...).
Aligned byte-state at the founder's fixed loci {3-7,12} is 0.00 from 14,200.

**Verdict: STANDS WITH CORRECTION.** The correct statement is: "The whole founder-derived segment shifted by a terminal NOP
insertion and tail deletion. Early descendants carried many different shifts, and later a -9 class and then a -11 class swept.
Position without alignment is the wrong frame. With alignment, material and state agree."

---------------------------------------------------------------------------------------------------------------------------------

## R2-3. Capability changed class on conserved founder material and then held

**Plain restatement.** The founding genome could not make an exact copy of itself in isolation. Within about 2 generations,
descendants that were still almost entirely founder-derived could copy themselves exactly on some inputs. By about 14,400-14,600
they could do so on all inputs. Exact self-copy then stayed common while founder material eroded.

**Hidden assumption.** "Capability class" is the ruler's category: exact on 0, on 1..255, or on all 256 inputs
(copier_census.py:82-88). A category boundary is treated as a change in capability.

**Attack 1 (decisive): NEAR_COPIER -> EXACT_GATED is a fixed point of the founder's own copying, reached in one copy, with no
change to any executed byte.**
- On inputs 127, 130, 134, 142, 158 and 190, the founder writes 00 00 followed by F[2:]. Loci 0-1 come out as 0x00 and loci 2-31
  are copied exactly.
- That child copies itself exactly. The founder's single defect (writing zeros at loci 0-1) is invisible once loci 0-1 already are
  zero.
- The founder's recorded first birth (input 142, SELF_COPY, epoch 13,955) produces exactly this child.
- The "improvement" is the loss of two founder bytes (0x22, 0x59) that were never part of the founder's essential set
  {3,4,5,6,7,12}.
- Two controls rule out other explanations. With two random bytes at loci 0-1, 5 of 5 trials give NEAR_COPIER or WRITER. A pure
  one-byte shift gives NEAR_COPIER.

```python
from h import *
from archaeon.envgate import ruler as R
c = bytes(2) + F[2:]
assert trace(F,142)['nbr_window'] == c           # the founder's first-birth product
assert trace(c,142)['nbr_window'] == c           # ...copies itself exactly
print(R.measure(F)['class'], R.measure(c)['class'], P.machinery(F)[0], P.machinery(c)[0])
# NEAR_COPIER EXACT_GATED [3,4,5,6,7,12] [2,3,4,5,6,7,12]
```

Calling this "the capability IMPROVED ... first on founder material" (TH013_RESULT H1) overstates it. The copying procedure is
unchanged. What changed is the ruler's whole-genome identity test, which now passes because the genome became the fixed point of
an imperfect copying map. In standard terms, the founder was not the replicator. Its first-generation product was.

**Attack 2: "EXACT_UNGATED by 14,600 ... then held" is contradicted by the recorded members.** Exact-input counts over all 256
inputs, recomputed per member with gate.py:
- 14,000: 7/256. 14,100-14,200: 4/256. 14,300: 3, 8, 32, 64 or 65/256.
- 14,400: 12/12 members at 256/256. The switch happens here, not at 14,600.
- It does not hold:
  * 15,300: members at 32/64, 228/256 (x5) and 2/256;
  * 16,700: 3 members at 226/249;
  * 17,300: 2 members at 8 exact and only 20 birth inputs out of 256;
  * 17,900: 6 of 12 EXACT_GATED.
- The ruler column of th013_analysis.json shows EXACT_GATED members in 12 snapshots after 14,500, peaking at 7/12 (15,300) and
  6/12 (17,900).
- Strongly gated genotypes keep arising. The claim should say "most sampled members are ungated", not "held".

```python
# gate.py (excerpt)
for m in snap['members']:
    T=bytes.fromhex(m['tape']); ne=nb=0
    for x in range(256):
        r=trace(T,x)
        if sum(r['nbr_mask'])/G>=0.9: nb+=1; ne+= r['nbr_window']==T
# 17300: 256/256 256/256 0/0 8/20 8/20 256/256 ...
```

**Attack 3: the GATED/UNGATED boundary is 255 vs 256 exact inputs.**
- At 14,400, zeroing the only founder-derived byte at locus 0 (0x75, IN D, material F@20) takes a member from 256 to 245 of 256
  inputs, with exact copying intact.
- So the "class change" is partly a one-input threshold.

**Attack 4: the endpoint is cherry-picked.** "1.00 at the end" is the last snapshot. 19,000 is 0.67 and 19,700 is 0.75.

**Re-derived:** median 0.8333, minimum 0.50 (14,900), last 1.00 over 60 rows. These match. TH-013 H5 also says "from 14,300 on,
members copy exactly in isolation at 0.75-1.00". That is false: 12 of the 57 snapshots from 14,300 on are below 0.75 (14,800
0.58, 14,900 0.50, 17,100 0.50, ...).

**Verdict: FAILS as stated.**
- The first class change is not a capability change built on conserved material. It is the first-generation product being the
  fixed point of the founder's imperfect copying, reached by deleting two non-essential founder bytes.
- The "then held" part is contradicted by recurring gated members.
- The only surviving part is: exact isolated self-copy stayed at >= 0.5 of sampled members (median 0.83) while founder material
  fell.

---------------------------------------------------------------------------------------------------------------------------------

## R2-4. Hypothesis verdicts 1-5

1. **"Partly supported".** Acceptable as "exact copying persisted while founder material fell from 0.85 to 0.33 of essential loci".
   The "IMPROVED" framing inherits the R2-3 failure.
2. **"Not supported" (replacements are inherited mutations, not rebuilt).**
   - Re-derived: 345 mutation + 3 computed = 348 non-founder loci at 19,700; SELF_COPY 646,622/655,307 = 0.9868.
   - However, th013_out.json stores only the KIND of each non-founder id, not the id. So inheritance of a SPECIFIC mutation (the
     same id shared across members) cannot be checked from the committed data.
   - "Inherited, not rebuilt" rests on the engine's copy semantics plus the 98.7% self-copy share. That is reasonable, but it is
     not a measurement on these members.
   - Verdict: STANDS WITH CORRECTION ("consistent with", not "shown").
3. **"Not supported at lineage level".**
   - The author concedes it is untested per member.
   - My gate.py shows that per-snapshot genotypes move between 0/0 (INERT: up to 6 of 12 at 14,800-14,900), gated and ungated
     inside the same lineage. So loss and regain of the ability is common at the genotype level.
   - A lineage-level "not supported" is true only in the trivial sense that the lineage never went extinct.
   - Verdict: UNTESTABLE AS STATED with the committed data.
4. **"Supported: the ruler tracks the wrong material unit".** Supported only as "the ruler compares unaligned positions". The
   material-vs-state part is wrong (see R2-2 Attack 3).
5. **"Origin scaffolded (host execution), maintenance not".**
   - The lineage's first birth is SELF_COPY on input 142 at epoch 13,955 (th013_out.json `founder`). It produces an exact gated
     self-copier (R2-3 Attack 1), before the host began at 14,001.
   - Whether host execution was NECESSARY for establishment was never tested (no replay with the host removed). The evidence is
     that the ancestry passed through hosted births under the parent-chain label (ENVGATE01_REVIEW:237-245).
   - "Scaffolded" should read "the origin passed through host execution; necessity untested".
   - "Maintenance not" also overstates isolated copying (see R2-3 re-derivation: 0.50-0.67 in 12 snapshots).

**Verdict: STANDS WITH CORRECTIONS** for items 1, 2 and 4. Item 3 is UNTESTABLE AS STATED. Item 5 is STANDS WITH CORRECTION
(necessity untested; a self-copying exact descendant existed before the host).

---------------------------------------------------------------------------------------------------------------------------------

## R2-5 (TH-015). The smallest transferable object is the executed program plus its data loci (~half the tape)

**Plain restatement.** Genome transplant into random-byte genomes: which subset of a member's bytes, written into an otherwise
random 32-byte genome, still gives a genome that can reproduce?
- The set of addresses the member executes, plus its single-knockout-essential loci: 89%.
- The essential loci alone: 3%.
- Everything except the essential loci: 0.1%.
- Random genomes: 0/400.

**Hidden assumptions.**
- "Capable" and "copy" mean "writes >= 90% of the neighbour window" (th015_archaeon.py:29), NOT self-copy.
- "Random background" is uniform bytes.

**Re-derived:** EXECUTED_ONLY mean 0.889 with an independent seed (file: 0.891), MACHINERY_ONLY 0.028 and MATERIAL_ONLY 0.001 (from
the file), chance 0/400.

**Attacks the claim SURVIVED** (reported because they were real attempts):
- Size-matched control, which the probe lacks. The RANDOM_SAME_SIZE control is matched to |M|, not |X|. I grafted |X| random loci
  of the same member (r5.py):
  * mean 0.057;
  * M plus random loci up to |X|: 0.188;
  * the first |X| loci: 0.117.
  So X is specifically informative, not just "most of the tape".
- Greedy minimisation of X, dropping a locus only if the graft rate stays >= 0.8 under two seeds (r5min.py, 8 tapes). X is
  1-minimal in 7 of 7 tapes where X passes (one locus removable at 15,600). The word "smallest" survives, locally.
- Zero (NOP) background: M on an all-zero background reproduces for only 1/3 of tapes. So the necessary/sufficient gap is not an
  artefact of the random background.
- Random-value knockout M (larger, see R2-1 Attack 4): graft rates 0.05 / 0.275 / 0.0 / 0.125. The necessity-vs-sufficiency gap
  survives.

**Attacks that land:**
- "~half the tape" understates it.
  * Mean |X| = 21.2 of 32 (66%).
  * For every tape up to 16,600, |X| = 24-30 loci (75-94%). At 14,700-15,600, EXECUTED_ONLY transplants 27-30 of 32 bytes.
  * Remove the 0x00 bytes from X (1.7 loci per tape on average) and the rate falls from 0.889 to 0.627 (r5zero.py). A large part of
    the "program" is NOP padding, which is needed only because the background is random.
- "0.85 exact" in the TH015_RESULT table does not follow from th015_out.json: the mean EXECUTED_ONLY exact is 0.829. Likewise
  MACHINERY_ONLY exact is 0.002, not "~0.003".
- "Input gating was lost by epoch 14,500: all 22 later tapes copy on 254-255 of 255 inputs."
  * The 22 are a stride sample of distinct capable tapes. "Copy" there counts births, not self-copies. The 18,400 tape counts as
    copying on 255 inputs yet has NO exact self-copy on any input (th015_out.json row 18,400: INPUT_SCAFFOLD.exact = False).
  * In the lineage as recorded, gating recurs: 17,300 two members birth on only 20 of 256 inputs; 15,300 one member on 64. See
    R2-3 Attack 2.
  * FAILS as a lineage statement.
- "BLOCK_128 ... the likely reason [the arm] did not stop this lineage" (TH015_RESULT Reading 3). The founder already reproduces
  on 15 ALLOWED inputs, and its first birth was on input 142. Input 128 was never necessary, so losing the gate is not needed to
  explain escaping the block.
- "Dependence on the fixed start pc grows over time."
  * The first tape (14,000) has CONTROL_STATE 0.000 and the second (14,200) 0.325. Robustness to a random start pc is highest in
    the middle (0.75-0.88 at 14,500-15,900) and low at both ends.
  * The data show a rise then a fall, not monotone growth.
- MATERIAL_ONLY 0.001 is true by construction. M is the set where any single knockout abolishes births, so re-randomising all of M
  is expected to abolish them. It does not test "material".

**Verdict: STANDS WITH CORRECTION.** Core: on uniform-random backgrounds, the executed-address set plus the essential loci is
locally minimal and transplants at 0.89, far above a size-matched random subset (0.06). Corrections:
- the set is 50-94% of the genome (mean 66%), not ~half;
- the exact rate is 0.83;
- "input gating lost" FAILS for the lineage (it holds only for the sampled tapes, and is measured by births not copies);
- the BLOCK_128 explanation is unsupported;
- start-pc dependence does not rise monotonically.

---------------------------------------------------------------------------------------------------------------------------------

## Summary of verdicts

| claim | verdict |
|---|---|
| R2-1 | STANDS WITH CORRECTION. The 0.0 is reproduced at its own epoch (14,800); only the "complete turnover" reading is refuted. Quote 0.32 / 0.67 at 14,800, 0.85 (not 1.00) for all members at 14,300; 0x00 knockout undercounts machinery. |
| R2-2 | STANDS WITH CORRECTION. The whole founder segment shifted (terminal NOP insertion and tail loss), not the machinery "as a unit". Early offsets are standing variation, not a trajectory. Aligned state equals material, so "state is the wrong unit" is false. |
| R2-3 | FAILS. NEAR->EXACT is a one-copy fixed point of the founder's copying map (lose loci 0-1 to 0x00), with no executed byte changed. Gating recurs after 14,500 (8/20 inputs at 17,300; 6/12 gated at 17,900). |
| R2-4 | 1, 2, 4 STAND WITH CORRECTION; 3 UNTESTABLE AS STATED; 5 STANDS WITH CORRECTION (host necessity never tested; a self-copying exact child existed first). |
| R2-5 | STANDS WITH CORRECTION. The 0.89 is real and survives a size-matched control and minimisation. "~half" is 66% (up to 94%); exact is 0.83 not 0.85; "input gate lost by 14,500" FAILS for the lineage; the BLOCK_128 explanation is unsupported. |

## Strongest objection (two sentences)

The headline "capability changed class on conserved founder material" (R2-3, H1) is a ruler artefact: the founder's own first birth
(input 142, epoch 13,955) writes `00 00 + F[2:]`, a fixed point of the founder's imperfect copying that copies itself exactly, so
the NEAR->EXACT step deletes two non-essential bytes and changes no executed instruction. The later "EXACT_GATED -> EXACT_UNGATED,
then held" is a 255-vs-256-input threshold that recorded members repeatedly cross back over (strongly gated genotypes at 15,300,
16,700, 17,300 and 17,900), so "input gating lost by 14,500" is true only of TH-015's 22 stride-sampled tapes.
