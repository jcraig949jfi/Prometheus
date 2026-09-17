# Campaign 3 -- local campaign decisions (no operator, no HITL)

Format: D3-### | when (UTC) | decision | evidence | alternative rejected |
revisit-if. Each decision states SCIENTIFIC DISCRETION or DETERMINISTIC
(and where the machinery went).

D3-001 | 2026-09-17 06:40 | Campaign 3 uses campaign seed 20260920 and engine
client cmp3-archaeon; the campaign-2 runner, prereg, accounting and harness
base are PARAMETRIZED per campaign (root, seed, client, ledger prefix) rather
than copied. | One shared machine; three campaigns of rows must stay
distinguishable (run identity carries the campaign seed). | Alternative: copy
campaign2/ to campaign3/ (two machines to fix). | Revisit never.
DETERMINISTIC (runner.Campaign).

D3-002 | 2026-09-17 06:40 | Three levels of reach on every row: FLOOR (best
training reward < 0.45), SHELF (0.45 <= best < 0.90), SUMMIT (best >= 0.90),
with first_shelf_gen and first_summit_gen; the 0.5 foothold stays as the
campaign-1/2 criterion for continuity; the SUMMIT threshold 0.90 is the
preregistered full-solve criterion for K=2 cells (E=16 x 2 asks = 1/32
resolution; 0.90 = at most 3 of 32 asks missed). | Campaign-2 L2-025/L2-039:
every K=2 foothold sat at 0.50-0.56; 0/24 full solves. | Alternative: SUMMIT =
1.0 (one unlucky episode would deny it; the evaluator's resolution is 1/32).
| Revisit if C3-SFE-01 shows a second shelf between 0.6 and 0.9. SCIENTIFIC
thresholds, DETERMINISTIC application (reachability.level).

D3-003 | 2026-09-17 06:40 | Stopped-on-solve runs are BASELINE rows with
stopped_on_solve=true and G = generations run; lookup(G) pools every row that
INFORMS budget G monotonically: a row run for >= G generations, or a stopped
row that reached before G. | Campaign-2 L2-026: ~17 valid W0 solves were
'treated'. | Alternative: keep them treated (loses the cheapest reachability
evidence the campaign has). | Revisit never. DETERMINISTIC (reachability).

D3-004 | 2026-09-17 06:40 | The corridor table is an INSTRUMENT: rows are
(source cell, source maturity, target cell, direct-reuse competence,
initialization reach at a declared dose, budget, foundry); mature sources
only; no row is a transfer claim. | Directive section 10. | Alternative: fold
it into reachability (it keys on pairs, not cells). | Revisit never.
DETERMINISTIC (corridor.py).

D3-005 | 2026-09-17 06:40 | Injection dose is explicit (common_fill dose /
inject n) and an OFFSPRING CAP limits the share of children per generation
whose primary parent carries an import origin; realized origin shares are in
every trace row already. | Campaign-2 L2-037/L2-048 takeover. | Alternative:
a fitness handicap (changes the economics the experiment is supposed to
measure). | Revisit if C3-SFE-10 shows the cap itself distorts selection.
DETERMINISTIC (evolve.Evolution.offspring_cap).

D3-006 | 2026-09-17 06:55 | SUMMIT requires the HELD-OUT competence >= 0.90 (48 episodes), not a
single generation's training best: the table held one W2_K2 row with training best
0.9375 at generation 54 and held-out 0.53 (C2-SFE-03 seed 9, the same run as
C2-SFE-10 random seed 9 under CRN), a lucky 16-episode battery. A training-only
summit is recorded as summit_candidate_gen; first_summit_gen is set only when the
held-out confirms it. C3-SFE-01 confirms candidates with a held-out probe at the
candidate generation. | reachability rows W2_K2 seed 9. | Alternative: k
consecutive training generations >= 0.9 (still a training battery). | Revisit if a
held-out probe at the candidate generation proves too costly. DETERMINISTIC.

D3-013 | 2026-09-17 07:55 | C3-SFE-08 (wall-clock producer-consumer under a
FULL-solve criterion) is REPLACED before execution: C3-SFE-01 found no
full-solve regime on W2_K2 through G300 (0/24), so the experiment's outcome
variable does not exist. The replacement is chosen after C3-SFE-02's anatomy
from the directive's preferred direction A (shelf/summit): a selective pressure
that distinguishes partial from complete behaviour without naming the
mechanism, or a valley-crossing measurement, whichever the anatomy makes
sharper. | C3-SFE-01 rows. | Alternative: run C3-SFE-08 on time-to-shelf (a
campaign-2 measurement repeated). | Revisit never. SCIENTIFIC.
