# FAILURE 15 -- status: NOVEL_FAILURE_SUPPORTED relative to the frozen NS-01 archive (not new to science; see end)

Name: RELATIONAL ENCODING DEFEATS FIXED-CAPACITY STATE DECODERS (information-presence false negative).

What happens. A mechanism holds the cue only as a RELATION among state coordinates that are each uniform at all times
(B08 "proactive secret sharing": 32 share pairs, cue = (B - A) mod 4, every step re-randomises both shares with a common
shift). Its own readout computes the invariant (histogram of B - A) and the cue is decodable at excess 1.00 for every k.
A generic decoder of the DECLARED full state -- the instrument family the archive uses to say "the information is / is
not in the state" (C3 P1 decodability; NS-01 full[k], which drives the DEGENERATE and M-UNREACHABLE rules) -- reads
.27-.33 (random features), .02-.05 (linear), .35-.46 (one-hot + random features).

Minimal witness: prometheus/cosmos/ns01/f15.py RelationalWitness (W-REL), written by Cosmos from the causal account, not
from B08's code; reproduces the signature (readout 1.00; full .28-.30, linear .02-.06, one-hot .43-.46).

Causal account + intervention (prereg PREREG_F15_RELATIONAL.md, c14ab905a; run 08:33Z, supervise DONE):
GAUGE (common random shift of both shares at t = 1) leaves the readout at 1.00; DESYNC (shift B only) drops it to ~0.
So the cue is causally carried by the relation, inside the declared state (also: transplant moves it, own8 ~ 0).

Why the archive does not explain it (as tested): not M-HIDDEN (transplant: donor 1.00, own ~0); not M-UNREACHABLE (the
inverse: readout > state decoder); not M-LINBLIND (readout is linearly decodable; the blindness is on the STATE side);
not E12/P8 representation dependence (per-coordinate one-hot re-encoding does not restore it -- contrast B01, which IS
representation-dependent: one-hot restores 1.00); not a decoder-class artefact (linear fails too -- contrast B05, whose
total-momentum readout is linear in the state and a linear state decoder recovers it).

Why it is only a CANDIDATE (found by Cosmos after the preregistered test, descriptive): a wider generic decoder
(random features 4096 instead of 512, n_train 4000) reaches .96 on W-REL with 32 pairs, and with 1 or 4 pairs even
width 512 decodes perfectly. The false negative is therefore a CAPACITY x RELATIONAL-DIMENSION effect, i.e. close to
the archive's known decoder-class dependence (XorCue / E08 shared-failure matrix), moved to the state side and made
quantitative. Directive s6 item 4 is only partly met.

Consequence if it holds: "not decodable from full_state" is evidence of absence only up to the decoder's capacity
relative to the dimensionality of relational codes; any P1-type gate (C3 certificate premise "the generic probe sees
everything", calibrated on non-relational planted systems) has an uncalibrated false-negative region. Not shown to
affect any C3/C4 family (their states are not relational); flagged, not claimed.

Provisional archive entry for NS-02: M-RELATIONAL, rule: rf - full >= .20 at some k AND full_lin and full_onehot also
fail; witness W-REL; NS-02 must test the capacity scaling (preregistered) before it is promoted or merged into decoder-
class dependence.

## Falsification attempt (prereg PREREG_F15_CAPACITY.md, bb8624d1d; run 08:36Z, supervise DONE) -- SURVIVED
Required generic-decoder width for excess >= .90 (W-REL, k 4, one-hot + random features, n_train 4000):
M 1, 2, 4: 128 | M 8: 512 | M 16: 1024 | M 32: 4096 | M 64: > 4096 (.76 at 4096).
Slope of log2 w* on log2 M (M >= 4): 1.6 (rule: <= 1.0 would MERGE). Sample-size control n_train 16000 at w 512:
M 16 .83, M 32 .55, M 64 .31 (no rescue). VERDICT by rule: KEEP_DISTINCT ("relational dilution").
Status raised from CANDIDATE to SUPPORTED (relative to the archive): reproducible (fresh seed, 4 disguises), minimal
witness written from the account, causal intervention (gauge / desync), representation-change test (one-hot), and a
preregistered merge test it survived.

## Honest scope
This is a known fact of learning theory, not a discovery: random-feature (kernel) decoders need capacity that grows with
the number of interacting coordinate subsets a target depends on (parity-like targets; expected slope ~2 for pairwise
relations, observed 1.6 on a coarse grid). What is new is its place in THIS program: the archive's information-presence
instruments (C3 P1, NS-01 full[k]) are fixed-capacity generic decoders calibrated only on non-relational planted
systems, so their "no information" verdicts have an uncalibrated false-negative region that grows super-linearly with
relational code dimension. Limits: one witness family (Z4 shares), one decoder family, k = 4, widths in factors of 2.
