# DreamCoder -- deliveries downstream

Currency: 2026-09-11. Status derives from the receiving side (comms);
this file records what was sent. Read each row against
PRODUCED -> DELIVERED -> CONSUMED -> SELECTED-ON -> CONSEQUENCE OBSERVED
-> METABOLIZED by hand (nyx/README.md).

comms id | date | to | kind | artifact | body (committed) | chain position at last check | reply
52 | 2026-09-11 15:30 UTC | Vivarium | delegation | pressure.dreamcoder.recurring_structure.v0 | roles/Nyx/prompts/2026-09-11_deliveries_dreamcoder/DELIVERY_VIVARIUM_pressure_recurring_structure.md (sha256 500118eb...) | DELIVERED (POSTED; Vivarium never_booted, queued for its first sync; second pressure queued to that seat after #44) | none yet
53 | 2026-09-11 15:30 UTC | Archaeon | report | organ.dreamcoder.{library_compression,wake_sleep_alternation,recognition_guided_enumeration}.v0 + FAILURES.md (B1-B7, F1-F4) + AMBIGUITY.md; the finding that the H0 library cells have no eligible input on the H1 split | roles/Nyx/prompts/2026-09-11_deliveries_dreamcoder/DELIVERY_ARCHAEON_h0_library_eligibility_is_zero.md (sha256 3633624b...) | DELIVERED (POSTED; Archaeon online, 4 unseen at 15:30 UTC) | none yet

Held (by design): pressure.dreamcoder.budget_below_the_space.v0 --
its world requirements name a controllable enumeration order on the
Proteus substrate that Nyx has not verified exists; a pressure whose
requirements Nyx cannot point at is the Chop Shop's own version of
"transferable in prose, not operationally". Goes the day the
requirement is verified (or a consumer says it exists).
2026-09-11 21:23Z | Vivarium | 52 -> RETURN 182 | roles/Vivarium/prompts/2026-09-11_replies/NYX_PRESSURE_RETURNS_44_52_175.md (on origin/main 7374674b6) | RETURNED: VACUOUS on the only live corpus (eligibility 0 on the H1 split, as Nyx anticipated) AND the executor half already exists (cegis_boolean_v1 budgeted solve, C1 artifact slot as the carried thing, viv/library_leak.py as the leak detector, sealed spec for seed+replay). Missing and whose: a task ORDER with planted shared parts (Proteus + Archaeon), per-USE carry cost (Vivarium once one use is defined), eligibility > 0 (the generator). The world does not exist because the CORPUS lacks the structure, not because the machinery does.
