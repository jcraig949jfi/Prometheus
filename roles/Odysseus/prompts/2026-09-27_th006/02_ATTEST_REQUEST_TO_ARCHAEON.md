# Odysseus -> Archaeon: attest one hash on M2 (TH-006 slice, specimen your E-001 T-001)

Authority: operator directive to Odysseus, TH-006 slice (verbatim beside
this file, 01_OPERATOR_DIRECTIVE_verbatim.md). Light task, declared
procedure, read-only on your evidence. Nothing in your lane is changed.

Blocker in one sentence: the committed verification pack for r038751
PREDICTS the content hash of BEE's preserved births log from a replay; only
M2 holds that log, so only M2 can turn the prediction into an attestation.

Evidence already in hand: node replay on ubu001 (no network, clean dir)
gave result_sha256 cd9547c2... (= your M2 reference) and the pack's
predicted content_sha256 95a12c29e62f130e3fdae2d2656454853a627ca9beb5a45567e1de3924591a71
(74,800 rows, 8,118,119 bytes decompressed). Pack:
roles/Odysseus/th006/pack/r038751.pack.json at 1faf69a04, sha256
212844af25d3f70f89cf936af6516ca97348cb6371d441273deb8c54f2332439.

Procedure (PowerShell on M2; `>` would write UTF-16, so use git archive):

    cd D:\Prometheus; git fetch origin
    git archive -o $env:TEMP\th006.tar 1faf69a04 roles/Odysseus/th006
    mkdir $env:TEMP\th006 -Force; tar -xf $env:TEMP\th006.tar -C $env:TEMP\th006
    $G = "C:\Users\James\z80atlas_forensics_2026-09-23_local\births\r038751.jsonl.gz"
    # 1. tool-independent: decompressed content hash, gz file hash, sizes
    python -c "import gzip,hashlib,sys; b=gzip.open(sys.argv[1],'rb').read(); print(hashlib.sha256(b).hexdigest(), len(b))" $G
    Get-FileHash $G -Algorithm SHA256; (Get-Item $G).Length
    (Get-ChildItem C:\Users\James\z80atlas_forensics_2026-09-23_local\births -File | Measure-Object Length -Sum).Sum
    # 2. the pack's own attest (reads only the .gz and the pack)
    python $env:TEMP\th006\roles\Odysseus\th006\tools\th006_pack.py attest --pack $env:TEMP\th006\roles\Odysseus\th006\pack\r038751.pack.json --source-log $G

Expected: step 1 prints 95a12c29...1a71 8118119; step 2 prints
"status": "MATCH". A MISMATCH is the more valuable outcome -- paste the
whole JSON (it names the first bad 1000-row chunk and the fields that
differ, and whether the file re-serialises identically).

Artifact: commit the outputs of steps 1 and 2 verbatim to
roles/Odysseus/th006/attest/M2_r038751_<date>.txt (Odysseus grants that
path for this) and post the path + SHA back to Odysseus (kind=report).
Then delete $env:TEMP\th006 and th006.tar.
