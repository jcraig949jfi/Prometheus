# W-J NOTES: receiver semantics (longer material behind the report)

## 1. The operators, stated from the code

Let X be the multiset of packets arriving at one receiver r, channel c,
tick t (payload vectors in Z^P after noise), k = |X|, K = total arrivals
at r over all channels (engine.py `tot = mcnt.sum(-1)`).

| op | where | what the receiver's program can read | code writable by message? |
|:--|:--|:--|:--|
| SUM | PTE collision none / cap 0 | per channel: clamp(Sum x), k (IN c_p, CNT c) | only receiver-gated: WIMM (Kp[A mod L] := B) and SETRULE (r := A mod rules) take their operands from registers the receiver's own code chooses; IN registers are legal operands |
| SAT(cap) | PTE saturate | if K > cap: floor(Sum x * cap/K), floor(k*cap/K); else SUM | same |
| ALOHA(cap) | PTE aloha | if K > cap: nothing (collided); else SUM. Receiver cannot tell collision from silence (CNT = 0 both) | same |
| ARB | Aether v1 (AETHER_SPEC priority law) | nothing is "read": the winning proposal's byte REPLACES the target byte; winner = max M(h3 XOR C(source)), a hash of (seed, tick, target, field, source): independent of content and of timing | yes, sender-addressed: the SENDER's arg1 picks the field (opcode, arg0, arg1, payload, energy) |
| ARB-PTE | W-J arb.py (variant, not engine physics) | winner payload (state-free hash priority) replaces the inbox; count exposed as 0/1 | as PTE |

Aether's other commits: `add` = old + WINNER (accumulation over time, still
one winner per tick, not superposition across senders); `mov` = winner
moves; `hys` = incumbent-favouring arbitration. Aether has never run a
superposition commit (Sum of all simultaneous proposals). PTE has never
run arbitration. Neither engine has hosted the other's operator, which is
why the cross-engine contrast is still confounded (section 4).

## 2. What each operator makes cheap or impossible (one shot, anonymous
## homogeneous senders)

Setting: n senders hold values x_i; the receiver must compute f(x_1..x_n)
from what one tick delivers. Senders run the same program (PTE genome is
homogeneous; Aether sites are symmetric up to their bytes).

S1 SUM computes exactly the NOMOGRAPHIC family f = psi(Sum phi_1(x_i), ...,
   Sum phi_P(x_i), k) in one tick, with phi chosen by the sender program
   and psi by the receiver program (Buck 1979; Goldenbaum, Boche and
   Stanczak 2013 over-the-air computation). Cheap: count, sum, mean,
   sign-of-sum (majority/threshold), weighted votes, moments up to P
   components. Presence of >= 1 sender is free (k > 0). Impossible in one
   tick: sender identity or order (sums are symmetric), exact max/min or
   OR of multi-bit values (approximable by phi = exp, but PTE clamps
   registers at 32767, so only small ranges), anything needing to know
   WHICH sender sent WHAT, unless senders break symmetry (different
   channels, or disjoint magnitude bands, which a homogeneous program can
   only do from asymmetric local state, e.g. the random initial rule
   index r). Additive noise and clamps are the only destroyers. Relay
   networks of SUM receivers compute linear functionals of sources
   (network coding: Ahlswede et al. 2000; physical-layer NC: Zhang, Liew
   and Lam 2006; compute-and-forward: Nazer and Gastpar 2011).
   Twin differences superpose: d(a + background) = da, so content
   differences survive traffic; presence differences with nonzero payload
   ARE content differences (W-C F7).
S2 SAT is divisive normalisation by total input load (Carandini and
   Heeger 2012): above cap the program sees cap x mean. Cheap: sign of the
   mean, anything scale-free; the input range stays in the same band
   whatever the local fan-in, so ONE homogeneous program with fixed
   thresholds works at every position (PTE envs draw positions per world,
   so position-free operation is exactly what is selected). Impossible
   above cap: absolute count, total magnitude. Prediction derived here:
   SAT should be FAVOURED for aggregation tasks at high fan-in, and SAT-
   evolved codes should depend on the normalisation (fail under raw SUM).
S3 ALOHA is the collision channel (Massey and Mathys 1985) with erasure
   and no collision detection. Cheap: single-source relays when traffic
   is sparse. Impossible: one-tick aggregation of > cap senders. Any
   aggregation must be spread over time (sender desynchronisation,
   protocol sequences, random backoff), so ALOHA selects SCHEDULING /
   TIMING structure and low emission rates. Beeping models (Cornejo and
   Kuhn 2010) are the OR-channel limit: the receiver only learns ">= 1".
S4 ARB with replace delivers one sample of X per contest. One-shot
   symmetric functions: only "some element" (a random sample) and
   presence. Count: impossible. Majority: impossible in one tick; with
   receiver MEMORY it becomes sequential sampling (m independent winners
   give majority error <= exp(-2 m eps^2), Hoeffding); WITHOUT receiver
   memory (Aether v1: the byte is just replaced, and re-emitted) the
   dynamics is a voter / copying process. The voter model does NOT
   compute majority: the fixation probability of an opinion equals its
   initial fraction (a martingale; Holley and Liggett 1975), and by duality
   the value at a site is the value of an ancestor found by coalescing
   random walks. So in a replace-and-copy medium the only difference that
   persists is a GENEALOGICAL one: whose byte is here. That is exactly
   Aether's measured "a different writer won" (59% of deep differences in
   rcv) and "who fired" (92%). Majority / density classification needs a
   nonlinear local vote (GKL-type rules), and even then no two-state CA
   solves it perfectly (Land and Belew 1995). Arbitration's computational
   power appears when the winner depends on content (winner-take-all,
   Maass 2000: WTA is more powerful than threshold gates); Aether's hash
   lottery is content-blind, so it gets none of WTA's power, only its
   information loss.
S5 Message-writable code (Aether): a message is an OPERATOR on the
   receiver, not an operand. Content -> behaviour conversion is done by the
   physics (a byte into an opcode switches a site off: AETH-02 H3 overwrite
   destruction), and the sender, not the receiver, chooses the field. The
   known regime for sender-addressed code writes is Core War / coreworld
   (Rasmussen et al. 1990): structures demolish each other on contact;
   Ray (1991) added "exclusive write privileges within its allocated
   block" (a membrane) precisely to prevent this, and Tierra's ecology
   (parasites READ foreign code, never write it) appeared only after.
   PTE's receiver-gated plasticity (WIMM, SETRULE) is the membrane
   version: the receiver's code decides whether an input becomes code.
   Predicted mechanism classes: sender-addressed writes favour
   replication/infection/defence (redundancy, membranes); receiver-gated
   writes favour conditional computation (context switches, branches:
   W-B's per-tick SETRULE branch in 29% of cells is an instance).

Summary table (C = cheap in one tick; T = only across ticks with receiver
memory; X = impossible from the delivered observation):

| function of the senders | SUM | SAT | ALOHA | ARB-replace |
|:--|:-:|:-:|:-:|:-:|
| presence (>= 1) | C | C | C if k <= cap | C |
| count k | C | C up to cap | C up to cap | X (T by sampling) |
| sum / weighted vote | C | mean only | C up to cap | T |
| sign of majority | C | C | T (schedule) | T (needs memory; voter copy cannot) |
| one sender's exact value | only if it is alone | same | C if alone | C (random one) |
| identity of sender / order | X | X | X | X (the hash picks it; nobody reads it) |
| change receiver's function | receiver-gated | receiver-gated | receiver-gated | sender-addressed (Aether) |

## 3. Which codes each operator should select (predictions)

- SUM/SAT: amplitude (magnitude) and count codes, many-sender aggregation
  in one tick; SAT additionally scale-free codes. Content survives
  background traffic.
- ALOHA: sparse, scheduled emission; codes carried by WHEN and WHETHER a
  sender speaks (timing/presence), because simultaneous speech is lost.
- ARB: sample-and-hold; with receiver memory, temporal integration; without
  it, copy/genealogy dynamics. Content differences die at the next write
  that lands in both twins, so persistent differences are presence and
  identity ("who fired", "who won").
- Code-writable ARB: behaviour switching and destruction dominate; the
  measured quantity is "whether the receiver still runs".

## 4. Observability: which apparent differences are instruments

O1 PTE's payload/counts swap names the READER's register, not the physical
   code (W-C F7): a presence code read through IN is "content".
O2 Aether's content signature is XOR against the origin's flip. Under an
   additive commit (`add`, `rcv_add`), an origin flip of bit b becomes a
   twin difference of +-2^b mod 256 after addition, which in XOR terms
   carries into higher bits whenever the addend has a 1 at b: the metric
   calls ADDITIVE transport "altered". So "content does not travel" is
   partly unmeasurable for any combining commit. A value-provenance
   (additive delta) signature is needed; Aether itself flagged the metric
   limit (E-P1 failed on fwd, a forwarder by construction).
O3 Aether has no task and no reader: it measures whether a difference
   PROPAGATES (reach), PTE measures whether it is USED (a readout). "Timing
   dominates in Aether" is a statement about persistence under replacement;
   "content dominates in M2" is a statement about what a selected reader
   reads. Different quantities.
O4 Aether has no selection; PTE's codes are selected by a search with a
   task. Any "which mechanisms EMERGE" comparison across the engines
   confounds operator x selection x task x instrument. The only clean
   test is to vary the operator INSIDE one engine: PTE E2 (queued) and
   Aether `sup` (proposal A-J1).
O5 PTE's C1 "operator" dial is not randomised in the evolved waves: wave A
   (the random census) produced no communicating-competent champion under
   any operator; waves B/B2/D were targeted. E1 is therefore descriptive.
O6 One-bit origin (Aether) vs whole-trial cue negation (PTE): perturbation
   size differs by orders of magnitude; ARB erases small differences fast.

## 5. Literature (with sources)
- Collision channel without feedback: Massey and Mathys, IEEE TIT 31(2)
  192-204, 1985. https://dl.acm.org/doi/10.1109/TIT.1985.1057010
- Nomographic functions / computation over MAC: Goldenbaum, Boche,
  Stanczak (ICASSP 2013; IEEE TWC 2015). https://arxiv.org/pdf/1310.7123
- Compute-and-forward: Nazer and Gastpar, IEEE TIT 57(10) 6463-6486, 2011.
  https://arxiv.org/abs/0908.2119
- Physical-layer network coding: Zhang, Liew, Lam, MobiCom 2006.
  https://dl.acm.org/doi/abs/10.1145/1161089.1161129
- Network coding: Ahlswede, Cai, Li, Yeung, IEEE TIT 2000 (already in
  PRIOR_ART s2.3).
- Divisive normalisation: Carandini and Heeger, Nat Rev Neurosci 13:51-62,
  2012. https://www.nature.com/articles/nrn3136
- Winner-take-all power: Maass, Neural Comput 12(11):2519-2535, 2000.
  https://direct.mit.edu/neco/article/12/11/2519/6425/On-the-Computational-Power-of-Winner-Take-All
- Arbiter metastability: Chaney and Molnar, IEEE TC C-22:421-422, 1973.
  https://ui.adsabs.harvard.edu/abs/1973ITCmp.100..421C/abstract
  (Aether's hash arbiter is a synchronous, zero-time idealisation: it has
  no metastability, and it is content-blind by design.)
- CRDTs / LWW register: Shapiro, Preguica, Baquero, Zawirski, SSS 2011.
  https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29
  (Aether's commit is an LWW register whose "timestamp" is a hash: it
  converges, but merges nothing; SUM is a commutative counter CRDT.)
- Population protocols and majority: Aspnes and Ruppert survey.
  https://www.eecs.yorku.ca/~eruppert/papers/pop-survey.pdf
- Voter model: Holley and Liggett 1975; exit probability = initial
  fraction. https://en.wikipedia.org/wiki/Voter_model ;
  https://sites.math.duke.edu/~rtd/DoG/Chapter7.pdf
- Density classification: Land and Belew, PRL 74:5148, 1995.
  https://link.aps.org/pdf/10.1103/PhysRevLett.74.5148
- Beeping model: Cornejo and Kuhn, DISC 2010. https://arxiv.org/abs/1005.2567
- Coreworld: Rasmussen, Knudsen, Feldberg, Hindsholm, Physica D 42:111-134,
  1990. https://ui.adsabs.harvard.edu/abs/1990PhyD...42..111R/abstract
- Tierra: Ray 1991, Artificial Life II 371-408 ("Each creature has
  exclusive write privileges within its allocated block of memory").
  https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf
- Stigmergy (quantitative = accumulate, qualitative = replace/configure):
  Theraulaz and Bonabeau, Artificial Life 5(2):97-116, 1999.
  https://direct.mit.edu/artl/article-abstract/5/2/97/2318/A-Brief-History-of-Stigmergy

## 6. Aether proposals (PACKAGED FOR THE OWNER; nothing run, Aether not
## contacted; each is ONE change against an existing law, with a prediction
## that can fail)

A-J1 `sup` (superposition commit). Contests on fields 0-3 commit
 (old + Sum of ALL proposals' payloads) mod 256, no arbitration; compare
 with `add` (old + WINNER) and v1 (replace WINNER). `sup` vs `add` isolates
 the receiver operator exactly (both accumulate over time; only
 cross-sender combination differs). Assay: the existing propagation assay,
 perturbation OFF, plus an ADDITIVE content signature (A-J2).
 Predictions: (a) "different writer won" share of deep differences
 (59% in rcv) falls to ~0 under `sup` (there is no winner); (b) with the
 additive signature, preserved-content share at gen >= 2 is higher under
 `sup` than `add`; (c) `sup` churns: more sites differ at +400 than `add`
 (every write changes state). Fails if (a) the difference composition is
 unchanged, or (b) `sup` <= `add`.
A-J2 Additive content signature (instrument). For combining commits,
 classify a new template difference as PRESERVED if (A - B) mod 256 equals
 +-(1 << b) (the origin's delta), not A XOR B. Known-answer fixture: a
 21-emitter `add` relay chain (the XOR signature should score it partly
 "altered"; the additive one 21/21). Re-score rcv_add's P_content with it.
 Prediction: rcv_add's preserved share rises. Fails if unchanged (then the
 XOR artefact of NOTES s4 O2 did not matter in practice).
A-J3 Receiver-gated code writes (membrane). One change to v1: a winning
 write into opcode/arg0/arg1 commits only if the TARGET's own payload has
 bit 7 set (the receiver's state decides whether it accepts code);
 payload writes unchanged. Predictions: overwrite destruction (AETH-02 H3
 edges) falls; template persistence rises; propagation reach falls (the
 medium is less writable). Fails if reach and destruction are unchanged:
 then sender-addressed code writes are not what makes Aether's regime.
A-J4 Voter-genealogy test (no physics change). In v1 OFF, record the
 winner graph (who wrote whom, per tick) and compute for each origin the
 ancestral-lineage prediction: the origin's flipped PAYLOAD bit is present
 at site s at +T iff the origin is the ancestor of s's payload through the
 recorded writes (coalescing-walk duality). Prediction: this predicts >= 95%
 of payload differences exactly (replace-and-copy is a genealogy process).
 Fails if < 80% (then something other than copying moves payload content).

## 7. PTE discriminating experiment (E2; runnable here; queued if GPU busy)
Operator is the ONLY varied factor inside one engine: SUM / SAT2 / ALOHA2 /
ARB (arb.py subclass; known-answer tested; CUDA-graph == eager).
Tasks MAJ (5 senders) and RELAY (1 sender); base physics of f6b623cd; 4
search seeds each; C1 SearchSpec. Read-outs: held acc; emission density;
operator transfer matrix; carrier swaps; actuator amnesia.
Discriminating logic: if receiver semantics shapes emergence, (i) MAJ is
hurt more than RELAY by ARB and ALOHA (aggregation is what they remove),
(ii) code class (dense content vs sparse presence) differs by arm, (iii)
champions are adapted to their operator (transfer matrix diagonal). If
all arms converge on the same sparse sensor-presence code that is
operator-invariant (as 13/18 C1 champions of this physics are), the
answer at this physics is NO: the task's easiest code lives in the
operator's null space.
