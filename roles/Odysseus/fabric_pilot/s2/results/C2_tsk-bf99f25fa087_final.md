All parts of claim C2 check out.

- **The 27,083 count:** `archaeon/causal_lens/out_v02/B6_PROBE_r038751.json:6` gives `"W_by_location=NO | W_by_material=YES": 27083`. The file was added in commit 949b9ba4d, which is on `origin/main`, and the file on `origin/main` is the same as in my checkout (blob 69070e12).
- **The hash matches the recipe and pack:** the committed recipe (`roles/Odysseus/th006/pack/r038751.recipe.json:9`) and pack (`r038751.pack.json:188,195`) both give `cd9547c24811…f6cd`. The same files are on `origin/main`. Recorded replays agree with that hash: E-001 A-002 (`ops/campaigns/C-001/E-001/TASKS.md:52`), TH-006 (`roles/Odysseus/th006/REPORT.md:68`) and R-13 (`R-13/REPORT.md:73`). I couldn't run the replay myself, so this rests on those records.
- **The M2 attestation is on main:** `roles/Odysseus/th006/attest/M2_r038751_2026-09-28.txt` was added in commit f525de9ef, which is on `origin/main`. Its status is MATCH, with content_sha256 95a12c29… equal to the expected value, over 74,800 rows.

Two details don't change the verdict:
- The attestation checks the hash of the preserved source log (95a12c29…), which the pack predicts from the replay. It does not re-hash cd9547c2 on M2 directly.
- The committed pack still says the attestation is PENDING (`pack.json:152-156`). The MATCH was recorded only in the separate attestation file, not written back into the pack.

The verdict is in `out/verdict.json`.

VERDICT: CONFIRMED