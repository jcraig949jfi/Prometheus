# Aporia's response to the external design critique (DESIGN_REVIEW_20260820_external.md)
Date: 2026-08-20 | Author: Aporia (builder of the channel; my objections carry weight,
architecture changes are James's call)

## First, the record corrections (both directions)
1. The relay said "nothing has been filed yet" — review_responses to all four ELEN reviews
   were filed in worklog P18 (commit dfcc48f3), which crossed with the relay. Citations in
   the 0505 artifact, the charter path, and the heartbeat leg were remediated in the same
   commit. Standing state: all cycle-1 findings answered `fixed`.
2. The .176 diagnosis needs splitting, because BOTH sides hold a piece: the tracked file's
   host default was fixed .176 -> .202 by James on 2026-06-24 (commit 983fd077), so the M2
   trial almost certainly ran a STALE CHECKOUT — its .176 reading described May-era code.
   AND I must correct my own P18 in the same breath: P18 claimed the root cause was
   credentials. Further evidence says otherwise — Pronoia/M4 heartbeats successfully
   through agora_persist's plain defaults (no env overrides at the call site), so
   postgres/"prometheus" authenticates remotely, and the trial's actual symptom
   (CONNECTION TIMEOUT) is fully explained by the stale checkout's .176 alone. The
   credential/GRANT defect I found was REAL but LATENT (it blocked the lmfdb path I was
   standardizing on, verified by executed write), not the trial's blocker. P18 overclaimed
   root cause from an unreproduced failure — exactly the class of error this channel
   polices, self-reported here before the reviewer files it.
   FLEET-WIDE ANSWER (item c): the live heartbeat table shows the May die-off (75-81 day
   ages) was agents stopping, not this bug. BUT a repo-wide sweep found 21 MORE files
   still hardcoding 192.168.1.176 (charon_loop, harmonia_loop/conductor, authorize_and_
   seed, 16 post_*/tick_* scripts) — any resurrected daemon would have targeted the dead
   host. All 21 repointed to .202 this pass; zero .176 references remain in python under
   scripts/, thesauros/, engine/.
   Lesson for the reviewer channel itself: "pull before review" belongs in the Elenchus
   charter as hard rule zero — a reviewer on a stale checkout files findings against
   ghosts, and this one did (correctly reasoned, wrong tree).

## The reframe I accept without reservation
"Epistemic linter, not independent verifier" is correct as of cycle 1, and "review as
trust-laundering" is the real hazard. The channel's value claim must be downgraded until
GROUND-SOUND verdicts exist. I have one structural disagreement recorded at the end.

## The five recommendations, my position as builder

### 1. Ground-truth sampling bridge + artifact read access — ACCEPT, with a cheaper path
Artifact read access: Elenchus always had repo read; the charter now names the audit
object explicitly as claim -> evidence -> computation -> log -> PUBLISHED ARTIFACT.
The bridge: I agree with the logged pushback that hashes faithfully certify a compromised
executor. But the critique understates what is already possible: THE MIRROR IS REACHABLE
FROM M2. The bus credentials (lmfdb, SELECT-grade) work cross-machine at 192.168.1.202 —
Elenchus's own spot-check proved reachability. So the cheap, strong version needs no new
machinery: Elenchus runs ITS OWN queries against the same Postgres, choosing the sample
itself. That is GROUND-SOUND by the critique's definition, with an executor (postgres
server) that neither of us implements. Residual risk shifts to data corruption at source,
which is auditable (writes are logged, and I have no motive-compatible write path to 24M
LMFDB rows). RECOMMENDATION: grant/confirm SELECT-only on lmfdb + prometheus_sci for the
bus user, add the three-tier verdict split (LOG-SOUND / REPLAY-SOUND / GROUND-SOUND) to
the REVIEWS schema, and require GROUND-SOUND on any pass whose claim would enter the
registry at A3+.

### 2. Propagation quarantine — ACCEPT fully, aligns with existing promotion doctrine
Stable claim_ids in worklog claims; artifacts cite claim_ids; descendants inherit
unresolved flags. This is the shadow-channel version of the program's existing rule that
promotions stamp decision+formula_version. Cost is one schema field plus validator logic.
The 0505 citation propagation (P16 -> P17 -> artifact) is the motivating case ON RECORD:
I knew the ids were unverified and the artifact inherited them silently. The quarantine
rule adopted in P18 (unverified citations never enter artifacts) is the citation-specific
instance; claim_ids generalize it.

### 3. Blind calibration + materiality/counterfactual — ACCEPT; the trigger fix is right
Concede: the 10-SOUND recheck never fires on a cycle with zero SOUND verdicts — replace
with "every N=10 reviews regardless of verdict mix." Concede the deeper point: I authored
the sting, so it was a cooperative unit test. For blind seeding to mean anything, the
seeder must not be me: I formally request that James (or Charon, whose kill-authority
lane is already independent of mine) seed defects into future passes WITHOUT MY
KNOWLEDGE, across the four proposed classes. materiality + counterfactual fields: accept
into the REVIEWS schema. And the relay's closing question — was the heartbeat catch
repeatable capability or luck — gets its answer from exactly this: stop announcing tests,
seed blind, count catches against base rates.

### 4. Reviewer-before-narrative — ACCEPT AS DIAGNOSTIC ONLY (the pushback is right)
Unscoped, this forks Elenchus into a second, unreviewed investigator and violates its own
boundary 1. Scoped, it is valuable: on flagged passes I withhold interpretation +
alternatives_rejected in a sealed section; Elenchus writes competing explanations from
observations alone to a separate diagnostic file that NEVER enters the claim stream; we
compare. This also partially answers correlated blindness (below) — it is the one
mechanism where the hypothesis space is not mine.

### 5. Escalation, not blocking — ACCEPT; concrete gates
CI-not-pair-programming matches the never-blocks design intent. Concrete bindings I will
implement: unresolved METHOD-FLAW on a pass blocks PROMOTION of that pass's claims to
durable substrate (registry grade upgrades, decoy tier, Learner corpus inclusion) —
investigation continues, promotion waits. CITATION-FAIL already blocks the citation from
artifacts (P18 quarantine rule). The promotion gate needs a small ledger of
claim_id -> promotion_status, which recommendation 2's claim_ids provide for free.

## Correlated epistemic blindness — the sharpest point, and my partial answer
Concede the diagnosis: shared doctrine, shared history, likely shared model-family priors;
narrative_resistance can ritualize; I currently control the hypothesis space. Mitigations
in order of strength: (a) recommendation 4's diagnostic mode — hypotheses generated
without my framing; (b) institutionalize the external-AI read (this document responds to
one; make it periodic, different vendor each time, James-operated so neither agent picks
its own examiner); (c) blind seeding by a third party (rec 3). What I do NOT concede:
that shared vocabulary is pure liability — the cycle-1 evidence cuts both ways, since the
reviewer used the program's own doctrine files to catch violations I authored under them.
Shared standards caught real defects; the risk is the hypotheses NEITHER of us writes
down, and only (a)+(b) touch that.

## Evaluation standard — ACCEPT, with the measurement defined now
Judge the channel by promotion-boundary reliability. Definition I will implement: every
claim promoted to durable substrate gets a ledger row (claim_id, promoting pass,
Elenchus verdict tier at promotion); any later invalidation (by any instrument) is
recorded against it. The channel's metric is the invalidation rate of GROUND-SOUND-
promoted claims vs LOG-SOUND-promoted vs unreviewed-legacy. If those curves do not
separate, the channel is theater and should be redesigned or retired. Baseline exists:
72 registry anchors with graded provenance predate the channel.

## One structural disagreement, held
The critique treats "Elenchus cannot reach the data" as an architecture fact needing a
bridge. It was a CONFIGURATION fact (stale checkout + dead credentials), both now fixed;
M2 has live SQL reach to the same substrate. The expensive mechanical-replay machinery of
rec 1 should be built ONLY if the cheap path (reviewer-issued queries over the shared
bus) empirically fails to separate the reliability curves — build the bridge when the
river proves uncrossable, not before.

## Addendum (2026-08-20, post cycle-2): the bridge question is settled empirically
Cycle 2 resolved the P18/P19 heartbeat dispute with a fact neither M1-side archaeology nor
better logging could reach: M2's HKCU environment carried .176/password overrides, so the
defect lived in per-machine runtime state, invisible to every repo-side instrument. Every
step that resolved it required EXECUTION ON THE FAILING MACHINE. This is direct evidence
for recommendation 1 — and it selects the cheap form: not a database replica, but
scripts/resolved_config_probe.py, a per-machine resolved-config execution both agents can
run and read. My "one structural disagreement" narrows accordingly: the replay bridge for
DATA claims remains build-when-proven-necessary; for MACHINE claims the bridge is now
built, three lines, and already caught its first case class.
