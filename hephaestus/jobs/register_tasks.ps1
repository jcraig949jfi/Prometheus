# Register the Forge Queue's scheduled job on M3 (Windows Task Scheduler).
# Addendum 3 (2026-09-01, Q7): ONE sentinel task only. Time wakes the sentinel; WORK triggers compute.
#   Hephaestus_Refine  every 3 h at :31  -> refine; apprentice ONLY if a packet is in APPRENTICE-TESTING;
#                                          rank; handoff. Cheap-model calls happen only when work exists.
# Retired (do not re-create): Hephaestus_Apprentice (4-hourly, clock-driven), Hephaestus_Rank (daily) --
# both folded into the sentinel. NO Claude/premium job, by policy (charter s20).
$root = "C:\prometheus\hephaestus\jobs"
schtasks /Delete /F /TN "Hephaestus_Apprentice" 2>$null | Out-Null
schtasks /Delete /F /TN "Hephaestus_Rank"       2>$null | Out-Null
schtasks /Create /F /TN "Hephaestus_Refine" /TR "cmd /c `"$root\refine.cmd`"" /SC HOURLY /MO 3 /ST 00:31 | Out-Null
schtasks /Query /TN "Hephaestus_Refine" /FO LIST | Select-String "TaskName|Next Run Time|Status"
