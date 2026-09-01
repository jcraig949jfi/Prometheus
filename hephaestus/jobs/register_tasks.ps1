# Register the Apprentice Forge scheduled jobs on M3 (Windows Task Scheduler).
# Charter cadences: apprentice 19 */4 * * *   refine 31 */3 * * *   rank 13 5 * * *
# The mutation job (47 */6) is NOT registered yet -- charter s25: build after one full cycle.
# NO Claude/premium job is registered, by policy (charter s20).
$root = "C:\prometheus\hephaestus\jobs"
schtasks /Create /F /TN "Hephaestus_Apprentice" /TR "cmd /c `"$root\apprentice.cmd`"" /SC HOURLY /MO 4 /ST 00:19 | Out-Null
schtasks /Create /F /TN "Hephaestus_Refine"     /TR "cmd /c `"$root\refine.cmd`""     /SC HOURLY /MO 3 /ST 00:31 | Out-Null
schtasks /Create /F /TN "Hephaestus_Rank"       /TR "cmd /c `"$root\rank.cmd`""       /SC DAILY        /ST 05:13 | Out-Null
schtasks /Query /TN "Hephaestus_Apprentice" /FO LIST | Select-String "TaskName|Next Run Time|Status"
schtasks /Query /TN "Hephaestus_Refine"     /FO LIST | Select-String "TaskName|Next Run Time|Status"
schtasks /Query /TN "Hephaestus_Rank"       /FO LIST | Select-String "TaskName|Next Run Time|Status"
