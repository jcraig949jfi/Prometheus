# Addendum 4 (2026-09-01, Q6): NO scheduled tasks. The clock sentinel was killed rather than polished
# into an event system. Work triggers compute: a human or a session runs the jobs by hand when there is
# a packet to refine. Historical walls are inert evidence at zero compute.
#
# Manual equivalents (repo root, PYTHONPATH=C:\prometheus):
#   python -m hephaestus.src.closure_test <spec>     # the standard Forge test (run FIRST for any new wall)
#   python -m hephaestus.src.refine                  # state transitions from executed evidence
#   python -m hephaestus.src.apprentice              # cheap models, only if a packet is APPRENTICE-TESTING
#   python -m hephaestus.src.rank ; python -m hephaestus.src.handoff
#
# This script now only verifies that nothing is scheduled (and removes any leftover task).
foreach ($t in "Hephaestus_Apprentice", "Hephaestus_Refine", "Hephaestus_Rank") { schtasks /Delete /F /TN $t 2>$null | Out-Null }
$left = schtasks /Query /FO LIST | Select-String "Hephaestus"
if ($left) { $left } else { "no Hephaestus scheduled tasks (by policy, Addendum 4)" }
