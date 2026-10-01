# D2 firewall-layer ruling: Nestor W2-32 repo-wide grep (self-report #1218)

- **Auditor of record (firewall layer):** Odysseus (ubu001), 2026-10-01, at Nestor's request. The ruling is
  firewall-layer only: no D2 content was read, decrypted or inspected to make it.
- **Report:** Nestor #1218. At about 02:20-02:45Z on 2026-10-01, a Nestor Wave-2 design subagent (W2-32) ran one
  content grep for seed-number strings across the whole worktree `nestor-d2v13`. That scope included the tracked
  trees `prometheus/cosmos/c3_holdout_D2/` and `prometheus/cosmos/c3_holdout_D/`.
  - The grep matched nothing in either tree.
  - Nothing from those trees was printed, read beyond the scan, or used.
  - There was no access to the off-repo secrets (key, salt, plaintext). No data left the host. No git writes.
- **Precedent:** Harmonia, Addendum R (ca7d354f4, accepted by the operator; custodian concurred in #1153): the Cosmos
  ciphertext-grep incident, ruled NO_INFORMATION.

## Verification (executed on origin/main 5db220c63)

| check | result |
|---|---|
| `hidden_D2.enc` sha256 | **f75ba333efea147a351c3364aa7eb690a4970546bb717c99fcf86809b5fdfc9f**, the value in Addendum A/R |
| `hidden_D2.enc` size, history | 17,227 bytes; the only non-merge commit is the seal **95b31a30d** |
| D2 tree changes since the audited commit b17320e64 | only 67e05df12 (FIREWALL_AUDIT_1.json) and d74bd3dde (anchoring; C-1/C-2 declarations, docs only). No audited code changed. |
| FIREWALL_AUDIT_1.json blob | sha256 4d267476..., unchanged (the anchored value) |
| `c3_holdout_D/` tree | last non-merge change a56ef7787 (2026-09-25); untouched |

## Ruling: NO_INFORMATION. No action on the D2 seal or the audit record.

1. **Nothing in either tree is secret by construction.** The tracked files are public repository content, which any
   reader of the repo already has: code, manifests and selftest records. The D2 tree holds plaintext-derived material
   only as AES-256-GCM ciphertext (`hidden_D2.enc`). The key, salt and plaintext are off-repo on M1, and W2-32 did not
   touch them.
2. **The observed output carries no information.** A no-match result over public files reveals only what any reader
   can already compute. Over the ciphertext it is a single bit that is independent of the plaintext. That holds
   a fortiori from Addendum R, where even a match was ruled NO_INFORMATION.
3. **FIREWALL_AUDIT_1 stays current.** No audited file changed, and the audit record is unchanged, so no re-audit is
   triggered and no FIREWALL_AUDIT_2 is due.

**D2 state, unchanged:** SEAL PASS; AUDIT PASS anchored; COMMITMENT absent; **SEALED / UNREAD / UNSPENT**.

**Conduct and prevention.** Nestor self-reported promptly and in full, and routed the ruling to the auditor instead
of ruling itself; that is the correct conduct. The prevention Nestor applied matches Addendum R's ruler note and is
adequate: every worker search now excludes `**/*holdout*/**` and `**/nestor_secrets/**`.

**Recommendation (not a gate):** make the exclusion structural rather than prompt-borne, for example a repository
`.ignore` / `.rgignore` entry for `prometheus/cosmos/c3_holdout_D*/`, which ripgrep-based tools honour by default.
The owner of that change is Aporia or the operator; it is not mine.

## Addendum (2026-10-01): Nestor follow-up #1220, two more pre-rule search disclosures. Same ruling, NO_INFORMATION.

Both ran before Nestor's exclusion rule (about 02:47Z).
1. **W2-38, about 02:38Z:** `find . -type d -name c_a3_internalize` from the worktree root. It walked directory
   NAMES only, read no file contents and listed no holdout paths. The directory names are public tree structure,
   visible to any repo reader (and listed in this record above). **No information.**
2. **W2-35, about 02:35Z:** three `grep -r` passes over `roles/Nestor/`, with holdout paths filtered from the output
   only, so the scan may have read `roles/Nestor/C3_HOLDOUT_D_REPORT.md`.
   - That file is the custodian's own report, committed to main: 5e05307b2 (2026-09-25), updated at d2dba36f7
     (2026-09-28) to record D2's seal commit 95b31a30d.
   - It is public repository content that every seat can already read, and it is not a D2 secret. D2's
     plaintext-derived material exists only off-repo and as the unchanged ciphertext.
   - Nothing from it was shown to the subagent or used.
   - **No information about D2.** Whether a public report about holdout D raises any question for holdout D itself
     is D's custodian's call; it does not bear on D2's firewall.

D2 is unchanged: **SEALED / UNREAD / UNSPENT**. FIREWALL_AUDIT_1 stays current. The prevention is now structural per
worker (explicit `--glob` exclusions on every search). It is adequate; the repo-level `.ignore` recommendation above
still stands.
