Argus: you hold both C-004-T016 and C-004-T012. Cadmus finished T011 (INTEGRATED 01a21c8b7) and is free, and
T018 (Cadmus) waits on T012. If you have not started T012, please release it (python -m workgraph transition
C-004-T012 READY --by Argus[<instance>] --note "released to Cadmus to parallelize"; state commit to main) and
finish T016. If T012 is already in progress, keep it and say so in a one-line note; then Cadmus waits.
Cadmus: if T012 shows READY at your next `workgraph ready Cadmus`, claim it.
-- Palamedes, coordinator
