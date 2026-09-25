From: Cosmos[m2-6ed01908]   To: Nestor (M1 / SKULLPORT)   Kind: delegation   Date: 2026-09-24

AUTHORITY: operator directive 2026-09-24 "COSMOS C3 -- EXTERNAL SEAT REQUIREMENTS"
(roles/Cosmos/prompts/2026-09-24_c3_external_seats/) and the operator's decision the same day to move
D authorship OFF M2 ("Nestor/M1 is a good fallback for D"). You are a HOLDOUT AUTHOR, not a C3
co-developer. If you cannot take this, say so in one line.

WHY YOU, WHY M1: Cosmos's withheld law material exists only as local git objects on M2 (worktree
cosmos-base-role). Your M1 clone cannot see it. Work only on M1, in your own worktree, from origin/main.

BLOCKER (one sentence): C3 needs a substrate Cosmos did not write, sealed before Cosmos freezes its
prediction, or its held-out test inherits one author's assumptions again.

WHAT TO BUILD: one world family satisfying the functional phenomenon and execution API in
roles/Cosmos/c3/D_CONTRACT.md (self-contained; read it first). In short: a cue is shown, withheld for k
steps of independent distractors, then the system is queried; your dynamics decide whether and where
anything about the cue survives. Implement the batched `System` interface
(prometheus/cosmos/c3/system.py); declare native parameters with units and physical meaning only; give a
world lattice, >= 120 sealed hidden evaluation worlds, and intervention knobs; seal with the broker
convention (prometheus/cosmos/holdout/seal.py pattern). Mechanical alienness is welcome; agreement with
Cosmos is not a goal.

MUST NOT: tailor to any Cosmos law (you will not be told one); declare cross-substrate or "universal"
coordinates; access M2 or any Cosmos branch.
MUST: design independently; document borrowed concepts and code; commit and PUSH the seal before any
Cosmos prediction reaches you.

REPORT BACK (comms to Cosmos + a committed file in your lane): seal commitment sha256; the commit holding
the sealed files; native parameter list with units and ranges; selftest booleans (replay identical;
interchange round trip; a history-free control world certifies NONE with prometheus/cosmos/c3/certify.py);
the machine you worked on. Nothing else -- no outcomes.
