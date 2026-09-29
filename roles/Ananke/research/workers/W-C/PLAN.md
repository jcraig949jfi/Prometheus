# W-C PLAN: PTE vs Aether, where does information ride and why?

Written 2026-09-27 BEFORE any PTE experiment below was run. Thresholds are
fixed here and are not changed after results. Namespace 0x5E6. CPU runs use
torch.set_num_threads(2). GPU is leased by W-B at plan time, so everything
here is sized for CPU; the evolution arm (X4) goes to QUEUE.md.

## Reading done before this plan (evidence, not results of this plan)

Aether (origin/main, read only): PHYSICS_DESIGN_02/03, RCV_REINTERPRETATION,
AETHER_ENGINE_CARD. Key facts that shape the plan:
- `rcv`: a written site fires once, emitting ITS OWN payload. The content
  channel of the relay is closed by the law's definition; only "whether it
  fired" can differ. 92-96% of secondary differences are the received flag
  and energy, 8% template bytes.
- `fwd` (relay forwards the received byte) FAILED as a content control in the
  rich soup: preserved content at gen >= 5 in 3.1% of origins; where both
  twins wrote, the value mostly differed because a DIFFERENT WRITER won the
  contest. Aether commit = hash-arbitrated winner REPLACES the target byte.
- `rcv_add` (accumulate instead of replace): P_content 0.188, but 76% of its
  content differences are "a write happened in one world only".
PTE: engine.py delivery SUMS payloads (Acc_sum) and counts (Acc_cnt), both
readable by the program (IN*, CNT*). All physics randomness is a counter hash
of (world seed, stream, tick, site): never of state. Caps (aloha/saturate)
depend on counts only. M2 decompiled: EMIT constant, PAY1 := IN0_0 (i.e. M2
is structurally a `fwd` law with the timing channel closed).

Working hypothesis H0 (the "artefact" reading): each engine's instrument found
information in the only dimension its mechanism left free. Aether-rcv fixes
content, PTE-M2 fixes firing. H1 (the "deeper distinction" reading): the
receiver's COMBINATION OPERATOR decides where differences can live:
replacement-with-arbitration (Aether) erases content differences and turns
them into writer-identity/timing differences; superposition (PTE) keeps a
twin difference additively through background traffic, so content survives,
and presence differences arise ONLY where the law makes EMIT/CHAN/routing
depend on input. H0 and H1 are compatible; the experiments try to break each.

## X1. Twin-difference decomposition (Aether-matched instrument on PTE)

Single-cue twins exactly as spikes/s_f.py (world 2p+1 = world 2p with ONLY
trial k=5's cue negated; same seeds, same positions). From trial-5 cue onset
to its readout tick, count per tick:
- channel entries (slot, recipient, channel) with Mcnt different = PRESENCE
  (count/timing/destination: who sent what where, when);
- entries with equal Mcnt but different Msum = CONTENT-ONLY;
- sites whose emit decision differs = FIRE (Aether's "who fired");
- sites that emit in both twins with different payload = PAYLOAD-ONLY.
Report presence share = PRESENCE/(PRESENCE+CONTENT-ONLY) and fire share =
FIRE/(FIRE+PAYLOAD-ONLY). Specimens: M2 4ab2ba01, the 12 C1 D-wave cells,
and two plants (X3).
Predictions:
 X1-P1 M2: presence share <= 0.10 and fire share <= 0.10.
 X1-P2 Every evolved specimen whose S-CT verdict was payload FLIP (channel
       content carriers: M2, RELAY 31cd/62a7/c16d, MAJ 0a23/f6b6) has
       presence share < 0.5. Failing on any of them = the swap and the
       difference census disagree about the carrier class.
 X1-P3 (H1 prediction, the one most likely to fail) presence differences
       exist in a specimen only if its fire share > 0 or its routing (w)
       differs between twins; i.e. PRESENCE > 0 implies FIRE > 0 or
       w-difference > 0, in 13/13 specimens (physics alone never converts
       content into presence). This is a consequence of engine.py; a
       violation means a physics path I missed.

## X2. Reach audit of the counts swap (a guard that may be unable to fire)

For the same 13 specimens under MIRROR pairs (as S-CT, ns 0x5E6), at each
S-CT swap tick record the share of pairs whose Mcnt differs at all and the
normalised L1 difference sum|dMcnt|/sum(Mcnt).
Prediction X2-P1: in >= 8/13 specimens fewer than 5% of pairs differ in Mcnt.
Decision rule (fixed now): where < 5% of pairs differ, the S-CT "counts
NO-EFFECT" is re-labelled NOT_VERIFIED (the swap was near-identity), and the
engine card's "never counts" claim is restricted to the specimens where the
swap had reach.

## X3. Positive controls: can PTE host an Aether-like presence code, and
## does the lens classify it?

Plant P-FIRE (mine, written in this directory; physics c1b_da_physics, env
RELAY d=1 delta=4 cue_len=2 iti=50 as C1b's F_DA; latency 4 == delta):
sensor EMIT := 256 iff SENSE > 128, PAY0 constant 256; every site
S0 := +256 if CNT0 > 0 this tick else -256. Variant P-FIRE-SUM: identical
except the reader uses IN0_0 > 0 instead of CNT0 > 0.
Swaps between mirror partners after tick ro-1 (packets in flight to the
readout), and X1 decomposition.
Predictions:
 X3-P1 both plants normal acc >= 0.95 (else plant bug; fix and log, no claim).
 X3-P2 X1 on both: fire share = 1.0 and presence share = 1.0.
 X3-P3 P-FIRE: counts swap FLIP, payload swap NO-EFFECT.
 X3-P4 P-FIRE-SUM: payload swap FLIP and counts swap NO-EFFECT, although its
       code is pure presence. If X3-P4 holds, the swap's "content" verdict is
       a statement about which register the reader reads, not about the
       carrier's physical dimension: under superposition a presence event
       with nonzero payload IS a content difference. That is the definitional
       confound between the two engines' vocabularies.
Also the route_relay plant (C1b fixture, destination code on plastic routing)
through X1 only: prediction presence share >= 0.9, fire share <= 0.1
(identity/destination, not firing).

## X4. Which physics selects presence vs content? (evolution; GPU -> QUEUE)

Arms on HOLD (M2's physics and env) with the C1 SearchSpec, 3 search seeds
per arm: A0 as M2 (no economy); A1 economy on with emission cost such that a
site can afford at most ~1 emission per 4 ticks (e_income=1, c_emit=4 per
copy, e_max=64). Measure held acc, X1 fire/presence shares, S-CT swaps.
Prediction X4-P1 (from energy-efficient/event coding): among competent A1
champions (held lo99 >= 0.60) median fire share >= 0.5, while A0 median fire
share <= 0.1. Failure mode anticipated: A1 champions fire in both twins
periodically with sign in the payload ("sparse content"). Either outcome is
informative. Not run unless the GPU frees or a CPU run fits the budget; a
reduced CPU version, if run, is labelled REDUCED and cannot confirm X4-P1.

## Aether-side experiments: PROPOSALS ONLY (never run here)
Written into REPORT.md, each with a prediction that can fail.

## Stop rule
~4 h total. Every attempt goes in LOG.md, including bugs.
