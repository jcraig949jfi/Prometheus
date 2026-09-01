# Remove the Apprentice Forge scheduled jobs.
schtasks /Delete /F /TN "Hephaestus_Apprentice"
schtasks /Delete /F /TN "Hephaestus_Refine"
schtasks /Delete /F /TN "Hephaestus_Rank"
