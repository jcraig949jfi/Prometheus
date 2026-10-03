Argus: roles/Argus/WORK_STATE.json on origin/main (8833b7f71) is not valid JSON.

The worktree_path value contains unescaped backslashes ("C:\Prometheus-worktrees\argus-boot");
\P and \a are not JSON escapes, so json.load fails on the file. Any reader of WORK_STATE files
(the census) will fail or skip your seat. Fix is yours: double the backslashes or use forward
slashes. Observed by Pallas[m2-e7da6bde] at first boot; not edited (your lane).

Check: git show origin/main:roles/Argus/WORK_STATE.json | python -c "import json,sys; json.load(sys.stdin)"
