# Clymene -- forensic dossier (Tityos Phase 3, signal-vs-hallucination lane)

Crawler: Tityos worker g6 (read-only). Worktree read: F:/Prometheus-worktrees/tityos-phase3 at 36ffe8073
(origin/main 5c98f59f1 + Tityos charter commit). Every claim carries an epistemic label. Paths are
repo-relative. Holdout and nestor_secrets paths were excluded from every search; none was opened.

## 0. Summary

- [HISTORICAL CLAIM] Clymene was born 2026-03-23 (eb17886fa) as "the Knowledge Hoarder", step 5 of the
  Pronoia serial pipeline (Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes). It cloned repos and
  downloaded HF model weights into a gitignored vault/ and wrote a SQLite registry and dated reports.
  Active life: four hoard runs, 2026-03-22..03-31 (roles/Clymene/RESPONSIBILITIES.md s0).
- [IMPLEMENTATION FACT] It was NOT a signal-vs-hallucination instrument in March. It made no scientific
  claims; it emitted artifacts and summary counts (agents/clymene/src/clymene.py).
- [HISTORICAL CLAIM] On 2026-09-11 an operator wake directive reseated it under roles/Clymene/ (ba926b129);
  the same day operator ruling CLY-01 chartered it narrowly for "archive integrity and utility" and
  retired the hoarding mission (roles/Clymene/STATUS.md s1).
- [IMPLEMENTATION FACT] The 2026-09-11 pass built one real, small measurement apparatus: a preregistered
  vault audit (04952e186) with four instruments (roles/Clymene/science/{repo_audit,model_audit,
  weights_probe,consumption_audit}.py), 7 controls including a CHEAT control, raw rows committed
  (roles/Clymene/science/runs/*.jsonl) and a disposition ledger (edd5df087).
- [REPORTED RESULT -- UNVERIFIED] Headline: 26/26 repo snapshots reproducible from the record, 0/37
  artifacts consumed by live code, repo snapshots 2.46% complete on M2, 9/9 model payloads
  integrity-verified, google/gemma-2-2b now gated (401) and the only irreplaceable artifact.
- What it policed: PROVENANCE AND STATUS-ACCOUNTING of external artifacts -- whether "archived",
  "updated", "Models: 14" labels corresponded to properties. Its most transferable output is the
  reconciliation of its own March reporting: every summary measured its own execution rather than its
  output (R-1..R-6, roles/Clymene/ledgers/HISTORICAL_RECONCILIATION_2026-09-11.md).
- Strength of machinery: [CODE-INFERRED CAPABILITY] narrow but genuinely controlled. The repo
  comparator has a demonstrated positive (cheat) control and two negative controls; the model probe was
  found to be measuring the wrong file (CLY-CAL-009) and was supplemented mid-pass. Scope is M2-only,
  tracked-files-at-HEAD-only, single auditor auditing its own history with a declared conflict of
  interest. No independent replication exists.
- Terminal state: [HISTORICAL CLAIM] CHARTERED, bounded pass COMPLETE, AWAITING operator rulings
  CLY-01b/c/d; recommended default PARK (STATUS.md s7). No commit touches the seat after 2026-09-11
  (git log --all).

## 1. Charter and role evolution

- Aliases: "Clymene -- The Knowledge Hoarder" (agents/clymene/README.md). No other alias found.
- Original charter: [DESIGN INTENT] agents/clymene/README.md -- "download and archive everything we might
  need before it becomes unavailable"; 72-hour cooldown via agents/clymene/data/last_run.txt; manifest
  agents/clymene/configs/manifest.yaml (26 repos, 20 models, 8 datasets; "28 GB VRAM line"; architecture
  diversity "to test whether RPH signatures are architecture-universal").
  Created eb17886fa (2026-03-23, "agents: add Aletheia, Clymene, Hermes, Pronoia + wire full pipeline");
  manifest +15 lines 7e9719cb0 (03-24); doc-only touch b674a9976 (04-03).
- Never a roles/ seat, never an operator charter until September [HISTORICAL CLAIM,
  roles/Clymene/RESPONSIBILITIES.md s0]. Archived "by association" with the whole Pronoia chain in
  aporia/docs/program_audit_2026-06-10.md L136 and aporia/docs/STATUS_2026-06-15_reset.md L105; absent
  from pivot/COMPONENT_DOSSIERS_2026-06-24.md and from engine/ledger/AGENT_AUTOPSIES.jsonl (not
  re-verified line-by-line by me beyond the seat's citations).
- 2026-09-11 adoption: operator directive verbatim in
  roles/Clymene/prompts/2026-09-11_adoption/OPERATOR_DIRECTIVE.md ("Don't do anything other than this
  bootstrap and registration except remind me what you did when you were active"). The seat corrected
  the directive's premise: operating life was March, not May [HISTORICAL CLAIM, same file].
- Same-day pivot: operator ruling CLY-01 -> chartered for archive integrity and utility; March mission
  RETIRED (roles/Clymene/journal/2026-09-11.md L163-L170; STATUS.md s1). The ruling text itself is
  quoted only in seat files; I did not find it in archaeon/docs/expansion/DECISIONS.md
  [UNKNOWN / AMBIGUOUS].
- Hosts: March runs on M1 (registry paths are M1 paths); September pass on M2 (SPECTREX5), worktree
  Prometheus-worktrees/clymene-base-role [HISTORICAL CLAIM].
- Relations: upstream Metis, downstream Hermes (March); reported a MONITORS.md gap to Archaeon
  (roles/Clymene/prompts/2026-09-11_adoption/REPORT_M2_UNREGISTERED_TASKS.md, 060338dca) corroborating
  Atalanta's earlier find; reused Nemesis-style CHEAT-control doctrine from the base role.
- Terminal: AWAITING operator; candidate narrow function "watch gate state on artifacts the program
  depends on" offered, not assumed (STATUS.md s5).

## 2. Code/system architecture

Engine A -- March hoarder [IMPLEMENTATION FACT]
- agents/clymene/src/clymene.py (single script; subcommands repos/models/status/--once), manifest
  agents/clymene/configs/manifest.yaml, SQLite agents/clymene/data/vault_registry.db (tables repos,
  models, datasets), log agents/clymene/data/clymene.log, reports agents/clymene/reports/*_hoard.md.
- Data flow: manifest -> git clone --depth 1 / git pull, or huggingface download -> registry row
  (status from subprocess exit code) -> report (len() of registry query).
- Status logic: update_repo() returns True on `git pull --ff-only` exit 0 (lines ~203-215 at 8714b2709);
  status = "updated" if success (line ~252); report "Models: N" = len(registry models) unfiltered
  (line ~575) [HISTORICAL CLAIM by the seat, line numbers at 8714b2709; I confirmed the README/manifest
  design but did not re-read those exact lines].
- Persistence: vault/ (gitignored, .gitignore L83), ~51 GB on M2.
- Dependency: PyYAML, not installed on M2; script not run in September [HISTORICAL CLAIM].

Engine B -- September vault audit (roles/Clymene/science/) [IMPLEMENTATION FACT]
- repo_audit.py (252 lines): R1 identity (URL + 40-hex SHA), R2 blob-less fetch
  `git fetch --depth 1 --filter=blob:none <url> <sha>` into a scratch repo, R3 ls-tree non-empty,
  completeness comparator (git blob sha1 over raw or CRLF-normalised bytes; LFS pointer oid added by
  amendment). Emits header/control/repo/reconciliation/footer rows to runs/repo_audit.jsonl.
  Network-failure keywords route R2 failures to `indeterminate` (lines ~226-229).
- model_audit.py / model_audit_resume.py: payload presence, HF sidecar
  .cache/huggingface/download/<file>.metadata commit+etag, local integrity (git-sha1 or sha256 etag),
  HEAD probe on a sidecar-covered file.
- weights_probe.py: supplementary HEAD on a WEIGHT file (added after CLY-CAL-009), can only move a row
  toward IRREPRODUCIBLE.
- consumption_audit.py: census over tracked non-documentary files at HEAD for vault paths, HF ids and
  package imports; resolves whether imports land in site-packages vs vault.
- build_ledger.py -> roles/Clymene/ledgers/VAULT_DISPOSITION_ROWS_2026-09-11.jsonl.
- Scale: 37 artifacts; repo probe 49 s; model probe < 1 min [REPORTED RESULT -- UNVERIFIED].

## 3. Inputs and outputs

- Inputs (Sept): vault/ on M2, vault_registry.db, manifest, upstream GitHub/HF endpoints, tracked tree
  at HEAD. M1 filesystem NOT readable (only Postgres) [HISTORICAL CLAIM, PREREGISTRATION s0].
- Outputs: runs/*.jsonl (repo_audit 33 lines, model_audit 15, weights_probe 12, consumption_audit 40),
  VAULT_DISPOSITION ledger + rows, HISTORICAL_RECONCILIATION, calibration LEDGER (CLY-CAL-001..009),
  QUEUE_ARCHAEOLOGY, BACKLOG_H0H5, MONITORS.md row ClymeneHoardCycle [IMPLEMENTATION FACT].

## 4. Claim class it was meant to police

- March: none (archivist; artifacts not assertions) [HISTORICAL CLAIM].
- September: [DESIGN INTENT] "PINNED, not merely present" and "CONSUMED, not merely stored"
  (RESPONSIBILITIES.md s2) -- i.e. claims of the form "artifact X is archived / reproducible / used".
  Indirectly it polices provenance of external inputs to experiments: can a run's external inputs be
  reconstructed? It never tested any scientific claim.

## 5. Measurement methodology

- [IMPLEMENTATION FACT] Preregistration committed (04952e186, 12:10 -0400) before the first run row
  (repo_audit header started_utc 16:20Z = 12:20 -0400). Definitions R1-R3, COMPLETENESS, CONSUMED-PATH /
  CONSUMED-IDENTITY / NOT CONSUMED, model PAYLOAD/STUB/PROVENANCE/INTEGRITY/REPRODUCIBLE fixed in
  advance; documentary references (.md, reports, pipelines/*.yaml) excluded by rule before the search.
- [IMPLEMENTATION FACT] Instrument CODE was committed only with the result (edd5df087, 13:12); the
  preregistration froze definitions, not code. Order of code edits vs result reading is not
  reconstructable from git [UNKNOWN / AMBIGUOUS].
- Population enumerated before testing (26 dirs / 26 rows / 11 model dirs / 14 rows / 20 manifest /
  8 datasets / 1 unaccounted dir) with attainable ranges stated (0..26) [IMPLEMENTATION FACT,
  PREREGISTRATION s0].
- Predictions written to lose (P1-P6), with the two least favourable to the seat named (P3, P4)
  [DESIGN INTENT].

## 6. Null/control generation

- No statistical null. The "nulls" are channel controls (section 7/8). The only rate estimate is
  1/9 window-closing with a stated 95% CI ~2%-48% [REPORTED RESULT -- UNVERIFIED, VAULT_DISPOSITION s3].

## 7. Positive controls

- POSITIVE: tensorly @ acc439e9... fetches (PASS, 239 entries) [IMPLEMENTATION FACT,
  runs/repo_audit.jsonl line 2].
- CHEAT_KNOWN_GOOD_TREE: real checkout of baukit at its recorded SHA scored match 1.0, 0 missing,
  0 extra, 0 mismatch -- through the same comparator (runs/repo_audit.jsonl line 5) [IMPLEMENTATION
  FACT]. Note: 23 of 24 files matched only after CRLF normalisation, so the CRLF branch is load-bearing
  for the control and for 238/257 vault matches [IMPLEMENTATION FACT / REPORTED RESULT].
- INTEGRITY_CHANNEL_CHEAT, WEIGHTS_PROBE_CHANNEL (open repo weights 200), SEARCH_CHANNEL (known-present
  string found) [REPORTED RESULT -- UNVERIFIED; rows in runs/*.jsonl].

## 8. Negative controls

- NEGATIVE_FABRICATED_SHA ("upload-pack: not our ref") and NEGATIVE_DEAD_URL (repository not found)
  both refused -> PASS [IMPLEMENTATION FACT, runs/repo_audit.jsonl lines 3-4].
- Integrity: deliberately corrupted copy hashes differently; weights probe: fabricated filename 404;
  consumption search: 0 hits for a known-absent string [REPORTED RESULT -- UNVERIFIED].
- [CODE-INFERRED CAPABILITY] Controls return PASS=None when setup fails (repo_audit.py ~L187-192), a
  third outcome; but I found no code that stops the run or withdraws results when a control is None or
  False -- the "withdraw if cheat fails" rule is enforced by the author, not by code.

## 9. Neutral/intermediate controls

- INDETERMINATE branch for network-class R2 failures (keyword match on stderr) [IMPLEMENTATION FACT].
  Keyword routing is a heuristic: a refusal phrased with "connection" would be misfiled as indeterminate
  [CODE-INFERRED CAPABILITY]. Zero INDETERMINATE observed [REPORTED RESULT].
- GATED as its own value distinct from failure (401/403) [DESIGN INTENT, PREREGISTRATION s1].

## 10. Qualification criteria / gates / thresholds

- Buckets: REPRODUCIBLE x CONSUMED 2x2 + INVALID/STUB/MISRECORDED (precedence) + UNKNOWN.
- Hard criteria: R1&R2&R3; completeness reported separately, never folded into buckets.
- Cheat control must return 1.0 or completeness is withdrawn [DESIGN INTENT].
- One amendment after reading results: LFS pointer comparison (CLY-CAL-008), declared as moving the
  answer AGAINST the seat's interest (removed the only "damaged file") [HISTORICAL CLAIM].

## 11. Statistical methods

- Counts and fractions; one binomial-ish CI on n=9 (method not stated) [REPORTED RESULT]. No
  multiple-comparison issue (census, not inference).

## 12. Independence assumptions

- Auditor == author of the audited historical agent's successor seat: Clymene audited its own March
  output and its own disposition; conflict declared (STATUS.md s6) [HISTORICAL CLAIM].
- Same Claude session wrote the preregistration, the instruments, the controls, ran them, and
  interpreted them. No second auditor, no second host, no independent replication [IMPLEMENTATION
  FACT by commit authorship: all commits on one branch, one day].
- Integrity relies on huggingface_hub sidecar etags -- written by the same download process that wrote
  the payload; an etag check proves payload == what the downloader recorded, not == upstream today
  [CODE-INFERRED CAPABILITY]. Reproducibility relies on upstream servers' own answers.
- Consumption census assumes TRACKED files at HEAD in ONE repo on ONE host are the universe of
  consumers; untracked scripts, M1/M3/M4, notebooks excluded (named as falsifiers, VAULT_DISPOSITION s5).

## 13. Provenance tracking

- Saved the day: the registry recorded commit hashes for all 26 repos, which made all 26 reproducible
  despite the on-disk snapshots being 97.5% absent [REPORTED RESULT]. HF sidecars (not Clymene's
  registry, which has no revision column) carried model revisions [IMPLEMENTATION FACT per seat;
  registry schema not re-read by me].
- Failed: reports aggregated over rows the registry had already flagged as failed (R-1, R-2, R-6);
  "Updated (26)" asserted an exit code (R-3); THOR promoted CLONE_FAILED -> updated by a code path
  that could not observe the defect (R-4); datasets stage structurally unreportable (R-5)
  [HISTORICAL CLAIM, HISTORICAL_RECONCILIATION_2026-09-11.md].
- Near-miss: `git -C vault/repos/<name> log -1` walked up to the enclosing Prometheus repo and reported
  today's date for 26 non-repos (CLY-CAL-003) [HISTORICAL CLAIM].

## 14. Known defects

- CLY-CAL-001..009 in roles/Clymene/calibration/LEDGER.md [HISTORICAL CLAIM, self-reported]:
  001 throughput report with no productivity signal; 002/005 count over wrong population; 003 command
  addressed the wrong object; 004 comms resolver reached a local empty DB on M2 (connection success !=
  right store); 006 THOR exit-code promotion; 007 invisible no-op datasets stage; 008 comparator did
  not model Git LFS; 009 reproducibility HEAD on a public sidecar file not the weights.
- Remaining [CODE-INFERRED CAPABILITY]: control outcomes not wired to abort; network-keyword
  indeterminate heuristic; consumption census name-substring hazard acknowledged ("THOR" matches
  "AUTHORS" 198 times) and avoided for the verdict; M1 unmeasured.

## 15. Historical audits performed (by and on this seat)

- BY: CLY-01 vault audit (04952e186 -> 413f36c08 -> edd5df087); queue archaeology
  (roles/Clymene/QUEUE_ARCHAEOLOGY_2026-09-11.md: 0 STILL_LIVE, 3 NEEDS_REPREMISE, 1 PARKED,
  1 SUPERSEDED, 1 RETIRED, 1 TRANSFER PROPOSED); M2 scheduled-task registry gap report (060338dca).
- ON: Pronoia era-1 in-process audit read Clymene's STDOUT, not its artifacts (roles/base-role/MONITORS.md
  row "Pronoia Era 1 pipeline audit": zero_output detector could not fire, knowledge_growth had no
  predicate, vram check misattributed another process's GPU memory) [HISTORICAL CLAIM]. Program audits
  June 2026 archived it as part of a chain only. No individual human adjudication found.

## 16. Historical findings (outcome labels)

- March hoard reports "Repos 26, Models 14, 60.82 GB" -- LATER OVERTURNED (9 archived, 3 counted from
  another profile's HF cache, 2 failed stubs; 51.39 GiB honest) [LATER CORRECTION / CONTRADICTION].
- 26/26 repos reproducible from record -- REPORTED POSITIVE [REPORTED RESULT -- UNVERIFIED].
- 0/37 consumed -- REPORTED NEGATIVE/NULL (scope: tracked HEAD, M2).
- Repo snapshots 2.46% complete, every subdirectory empty, all 258 files mtime within 2.5 s on
  2026-04-11 ("a copy, not a clone") -- REPORTED NEGATIVE, M2 copy only.
- 9/9 model payloads integrity-verified (112 files) -- REPORTED POSITIVE.
- gemma-2-2b downloaded 2026-03-23, 401 on weights 2026-09-11 -- REPORTED POSITIVE for "the window
  closes" (n=1) -- MIXED as a base rate.

## 17. Later corrections (timelines)

- "Models: 14" (03-23..03-31 reports) -> registry statuses -> CLY-01 reconciliation R-1 (413f36c08) ->
  annotated, originals untouched -> historical status: OVERSTATED.
- THOR "Updated" (03-23) -> log shows checkout failure on Windows-illegal path -> R-4 -> MISRECORD.
- Morning 09-11 recommendation "do not revive the March thesis" -> gemma gate finding -> STATUS.md s4
  "SUPERSEDED BY MEASUREMENT" (edd5df087).
- Preregistered model reproducibility predicate (HEAD on any sidecar file) -> stubs scored 200 ->
  supplementary weights_probe -> CLY-CAL-009 -> three gated not one.
- Comparator "1 content mismatch" -> LFS pointer -> amendment annotation -> 0 mismatches (CLY-CAL-008).

## 18. Pivots

- Archivist (March) -> dormant (April-September; host pronoia.py deleted by 3b3c74bc0 2026-04-23 per
  MONITORS.md) -> reseated (09-11 morning) -> chartered auditor of archive integrity and utility
  (09-11 afternoon) -> proposed gate-state watcher or PARK [HISTORICAL CLAIM].

## 19. Journals / TODOs / backlogs

- roles/Clymene/journal/2026-09-11.md (293 lines): two passes, commands and SHAs.
- roles/Clymene/BACKLOG_H0H5.md: self-declared below schema floor (refuses to pad to 20 items);
  CLY-01..05 (charter ruling, reproducibility, consumption, registry to Mnemosyne, 403 failure class).
- roles/Clymene/QUEUE_ARCHAEOLOGY_2026-09-11.md: March queue C-A..C-E classified.
- roles/base-role/MONITORS.md row ClymeneHoardCycle: DORMANT, not relaunched.

## 20. Research reports

- roles/Clymene/ledgers/VAULT_DISPOSITION_2026-09-11.md -- measured disposition, controls first.
- roles/Clymene/ledgers/HISTORICAL_RECONCILIATION_2026-09-11.md -- March reporting vs ground truth.
- roles/Clymene/PREREGISTRATION_2026-09-11_vault_audit.md -- definitions, controls, predictions, one
  LFS annotation.
- roles/Clymene/prompts/2026-09-11_adoption/REPORT_M2_UNREGISTERED_TASKS.md -- archaeon base-role test
  red on M2 for three unregistered scheduled tasks.
- agents/clymene/reports/2026-03-{23,27,31}_hoard.md -- the March reports (cited by the seat; present
  in tree per seat; contents only summarised here).

## 21. Failure cases

False positives (labels green for the wrong reason):
- Status-from-exit-code ("Updated" for THOR) [HISTORICAL CLAIM].
- Count-over-rows ("Models: 14" including failures and someone else's cache).
- Freshness from the enclosing repo (CLY-CAL-003).
- Reproducibility from the public sidecar file rather than the weights (CLY-CAL-009).
- "Connection succeeded" = reached the right store (CLY-CAL-004).
Plausible false negatives (FN):
- FN: consumption census blind to untracked code, other hosts, notebooks, hand loads -> "0 consumed"
  could be wrong; the seat names this.
- FN: completeness measured on the M2 copy only; an intact M1 vault would invert the completeness
  finding (seat names this).
- FN: comparator required exact or CRLF-normalised blob match; other line-ending or filter
  transformations (smudge filters other than LFS, autocrlf=input variants) would read as mismatch;
  only LFS was modelled after the fact [CODE-INFERRED CAPABILITY].
- FN: the weights probe tests ONE weight file per model; partial gating of shards would be missed
  [CODE-INFERRED CAPABILITY].

## 22. Mechanism archaeology

Not applicable (no mechanism claims).

## 23. Novelty/prior-art audit

Not applicable. Tangential: the March manifest selected models "for architecture diversity" to test
"whether RPH signatures are architecture-universal" [DESIGN INTENT]; nothing in the repo shows those
vault models were ever used for that test (0 consumed) [REPORTED RESULT].

## 24. Lens inventory

- Lens: an external-artifact provenance and reachability instrument -- "can this run's external inputs
  be reconstructed today, and is the copy we hold the bytes that were recorded?" Components worth
  keeping: blob-less fetch reproducibility probe (cheap, 49 s for 26 repos), tree comparator with a
  cheat control, sidecar-etag integrity check, weights-not-sidecar gate probe, path-vs-identity
  consumption distinction (import resolves to site-packages vs archive).
- Resolution ceiling: binary per-artifact properties; n=37; one host; no time series (gate watching
  is proposed, not running).
- Noise: network heuristics; upstream servers' answers are taken as ground truth.
- Reusable vs toy: reusable as a pattern; the scripts hard-code vault layout and registry schema.
- Unknowns: M1 vault state; whether any experiment's reproducibility actually depended on these
  artifacts.

## 25. What I did not read / open questions

- Did not open agents/clymene/data/vault_registry.db, clymene.log, or the three March reports; relied
  on the seat's quotations for line numbers (L203-215, L249, L252, L575 at 8714b2709).
- Did not re-run any instrument (forbidden). Did not read model_audit.py / consumption_audit.py /
  weights_probe.py in full (read repo_audit.py control and main loops).
- Open: where is the CLY-01 operator ruling recorded outside the seat? Were CLY-01b/c/d ever ruled
  (no later commit found)? Is gemma-2-2b's single copy still present? Is vault/evolutionary_agents
  (funsearch, OpenELM) relevant to Phase 3 evolutionary-substrate work?
