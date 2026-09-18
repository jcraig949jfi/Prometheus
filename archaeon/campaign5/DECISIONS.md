# Campaign 5 -- local campaign decisions (operator offline ~10 h; "make your own calls")

Format: D5-### | when (UTC) | decision | evidence | alternative rejected |
revisit-if. Each decision states SCIENTIFIC DISCRETION or DETERMINISTIC.
Vocabulary in prose follows archaeon/campaign4/DISPOSITION_C4-REH-1.md s6.
The directive is verbatim at roles/Archaeon/prompts/2026-09-18_campaign5/.

D5-001 | 2026-09-18 10:05 | EXECUTION PATH AND IDENTITY: the campaign harness
path (campaign-3 Experiment parametrized: archaeon/campaign5/c5base.py),
local evaluation, every world / experiment / observation written to the
engine under a NEW client cmp5-archaeon (self-registered by the Engine
wrapper on first use; credential written beside c5base.py, gitignored, never
moved), campaign seed 20260922, ledger prefix L5. NOT Vivarium's
wse_evaluate_v1: it is a working day away (#426) and wraps the OLD evaluator,
which Phase B cannot use at all. Recorded as the directive requires; no
scientific reason to wait was invented. | Directive HARD RULES; Vivarium
#426; D4-001. | Alternative: reuse cmp4-archaeon (rows distinguishable by
seed only) -- rejected: one identity per campaign is the C1-C4 convention. |
Revisit when the kind exists and Phase A is over. DETERMINISTIC.

D5-002 | 2026-09-18 10:05 | THREE QUESTIONS PUT TO THE OPERATOR IN CHAT before
they went offline, each with the default that applies on silence: (1) LANE --
Archaeon authors the Phase-B interpreter, generator and grammar variant under
archaeon/campaign5/ as a campaign-scoped representation, Proteus's frozen VM
untouched, handed to Proteus for adoption after (default yes); (2) FAIL
semantics -- the first fault kills the whole evaluation (reward 0 on every
episode), the maximal HARD (default); (3) STOP authority -- if Phase A returns
OLD_SUBSTRATE_EXHAUSTED and C5-03 returns REPRESENTATION_FAILURE, the
campaign ends there with a report (default). Any answer received is appended
here beside the default it replaces. | Operator preface: "I'll answer
questions now before you start". | -- | Revisit on the operator's word.
SCIENTIFIC DISCRETION (defaults chosen by the lead).

D5-003 | 2026-09-18 10:05 | C5-01 RESOLUTION: 6 walkers per competent parent (C4-05
had 4), depth 64, archives 0/16/32/48/64; 282 walkers per depth gives a
Wilson half-width of about .02 at rates near .05, the smallest effect the
branches use (.02). Walkers 1-4 reproduce C4-05's walks byte-for-byte for the
first 16 steps (same seeds) and that is checked. PRESERVE rule: continued-
gradient branch AND yield per evaluation at depth 64 >= 2 x a random single
edit's (.0012/evaluation). | C5-01/DESIGN.md. | Alternative: 4 walkers
(half-width .03, cannot resolve a 2-point difference). | Revisit never in C5.
SCIENTIFIC thresholds, DETERMINISTIC application.
