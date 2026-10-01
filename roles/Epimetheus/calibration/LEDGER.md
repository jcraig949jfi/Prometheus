# Epimetheus calibration ledger

Currency: 2026-10-01. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice
2026-10-01 | Read the creation directive's "Grab the latest from github" as `git pull --ff-only origin main` and ran it in the canonical checkout as the seat's first mutating command, before reading WORKING_CONTRACT.md | The contract forbids any pull in the canonical checkout (s1, s3); the phrase means fetch, record origin/main, worktree add. The pull MOVED canonical main 4a6457fbb -> 04b97a598 (fast-forward, 5468 commits, tracked tree clean before and after, two untracked operator files untouched), which s3 classes as an INCIDENT, not a boot transient | Self, on reading WORKING_CONTRACT.md s3 minutes later; reported to the operator in chat and in the creation commit; nothing reverted (a second mutation of the canonical tree would compound it) | Fetch only in the canonical checkout, always; read the base contract before the first git command that is not fetch; WAKE.md carries the conformant wording so the next wake does not depend on this seat's reading of "grab the latest"
