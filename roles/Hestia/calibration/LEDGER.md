# Hestia calibration ledger

Currency: 2026-10-04. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice
2026-10-04 | Drafted Chiron as one of the five candidate names on the strength of listing roles/ on main (which showed no Chiron); the draft was never shown to the operator | roles/Chiron exists on origin/chiron/base-role-adopt-2026-09-21 and was never merged to main; the census carries branch_only_roles() (achilles/census/sources.py) for exactly this case | Self, on a repository-wide grep and glob run before the list was sent; Chiron dropped and reported as rejected in the same reply | A free-name check covers roles/ on EVERY remote ref, `git grep` at the recorded origin/main SHA, and `git log --all --grep`; never `ls roles/` on main alone
2026-10-04 | Treated a first whole-tree sweep (the Grep tool, count mode, over the canonical working tree with an exclusion glob) as showing no mention of Hestia anywhere; the reply to the operator claimed only "not used as a role or seat", which remains true | The sweep returned 7 files and silently omitted harmonia/docs/the_decaphony.md:76, which names Hestia (a "hearth. Lattices." entry in Harmonia's April decaphony list). The file exists, is tracked, is not ignored, and plain grep, rg, and the same tool with the same glob on harmonia/docs all find it. CAUSE NOT ESTABLISHED: the whole-tree call returned a partial result without saying so (candidate: a tool-side limit on a 69,762-file tree; not tested) | Self, re-running the archaeology as `git grep` at the recorded SHA 5c290b461 before writing the seat file | A negative from a whole-tree sweep is not a clean negative: archaeology runs as `git grep` against the recorded origin/main SHA, and any hit-list is cross-checked on a narrow path before it is read as "none"
