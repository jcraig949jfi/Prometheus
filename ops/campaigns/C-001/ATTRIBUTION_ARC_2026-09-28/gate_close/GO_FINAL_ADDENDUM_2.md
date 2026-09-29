# GO_FINAL addendum 2 (2026-09-28): production run 2 receipts, rulings, sample transfer
GO_FINAL v2 (a79a0af6...) is unchanged. Archaeon has computed no production outcome and has read no production file.

**Run 2** (Nestor #910; commit 81895e729):
- 20:16-20:28 ET, exit 0, under a fabric lease.
- START_RECEIPT: every GO_FINAL v2 binding holds.
- Duplicates are exactly s9200006 C -> A and s9200008 C -> A; there are 9 distinct simulations.

**Rulings:**
1. **Determinism condition.**
   - Births exports: byte-identical to run 1, 11/11.
   - 1% sample: uncompressed content identical, 11/11. The .gz files differ ONLY in the gzip header mtime.
   - RULING: the condition is SATISFIED. Its purpose was to show the tracer output is deterministic; a gzip header timestamp is
     not tracer output.
   - This is recorded as Archaeon's reading of its own wording ("byte-identical"), made after the report. No re-run.
   - The transfer is verified on BOTH hashes per file: gz_sha256 for transfer integrity, uncompressed_sha256 for content.
2. **production_launch.py:** changed only its three binding constants to the v2 hashes, as declared by the owner. The new sha256
   is 1e2c4394... (full hash in the owner's receipt). It is recorded as a declared change to the receipts wrapper, not to
   production logic.
3. **S4 tallies now seen by Archaeon** (posted unrequested in #910; recorded as exposure):
   - prefix-flip coverage: self 0.447, other 0.125;
   - FAILED share: 0.0; completeness leak: 0.0;
   - precision: 0.37 / 0.52.
   - Per addendum 1 they are NOT USED until the independent final reviewer has checked s4_run.py.
   - Nothing changes in response. In particular, the flip floor (v4 s2.1 / v5 C4) and the flip rule (C7.2) stay as frozen. If
     the tallies stand after review, the frozen precedence applies as written.

**Sample bindings (manifests committed by the owner at 81895e729; sha256 LF):**
- SAMPLE_MANIFEST.json: 694a7bb3e2a07836dd57dadb024cdf3b6600b836a03b4adc061de34251f58b08.
- SAMPLE_MANIFEST_CONTENT.json: e1584484bb77045eccf9091373b4f056240299c7e23d767391e9219310dc8c93.
- 11 files, 28,055 records, about 112 MB.

**Transfer:** BLOCKED.
- M1 has no SSH route to M2 (owner). M2 cannot reach M1 on port 22 either (Archaeon checked with keys only; no credentials were
  tried).
- Proposed relay: ubu001, which M2 reaches.
  1. The owner tests a key-only BatchMode ssh from M1 to jcraig@192.168.1.218.
  2. If that works: scp to ubu001:~/wk/arc/npe_sample/.
  3. Archaeon pulls the files to M2 C:/Prometheus-data/evidence/attribution_arc_2026-09-28/npe_sample/ and verifies both hashes
     per file before reading.
- If that fails: the operator sets up a route.
- The fabric artifact store is NOT used: it has a 16 MB-per-artifact limit and is shared Postgres.
- The sample is not reduced or altered either way.
