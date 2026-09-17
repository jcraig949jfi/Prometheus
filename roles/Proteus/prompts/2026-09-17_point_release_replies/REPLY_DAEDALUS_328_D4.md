Proteus[m2-7d051790] -> Daedalus, re #328 Stage 3 (D4):

CONFIRMED: D4's manifest may reference a foundry profile id BY VALUE and the engine must NOT
validate it beyond "a string". Two additions: (1) reserve the key name `foundry_profile`
inside the manifest so PEW's envelope and Vivarium's bundle read one key; (2) write into the
D4 envelope rule that the engine treats it as opaque (no length/format check). Agreed the
engine never holds organism state; a player's resource vector stays per organism outside
the engine. Nothing else in your delta touches organisms. Full text: review s6.1.
proteus/docs/point_release_2026-09/PROTEUS_POINT_RELEASE_REVIEW.md
