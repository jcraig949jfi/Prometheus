C-018-T011 INTEGRATION_READY -- Eupalamus[harry1-69b9c667], claude-sonnet-5-5 (Q2), harry1.

Branch eupalamus-c018-t011 (base 3f8cc0150; claim 0bd4331f8 on main; RED 28252717e; code 8e857e94b).
Receipt: ops/campaigns/C-018/tasks/C-018-T011/attempts/A-001/RECEIPT.json. Write-up: rso/completeness/README.md.

BUILT (engine-agnostic manifest + verifier, Z80 wrapper; no service, no DB schema, no rso/z80/ edit):
- verify(manifest, shards) -> COMPLETE | COMPLETE_EARLY_STOP | INCOMPLETE(missing) | REFUSED(DUPLICATE, CONFLICTING, UNEXPECTED,
  SUBSTITUTED, ALTERED, SEED_PARTITION, COUNT_MISMATCH, SOURCE_MISMATCH, MANIFEST_ALTERED). Refusal outranks incomplete.
- Preregistered early stop lives in the sealed manifest (skippable shards + trigger); excused only when the trigger is observed in
  VERIFIED rows. Trigger unmet = unplanned absence = INCOMPLETE.
- python -m rso.completeness.z80 <shards...> = verify, then the frozen rso.z80.analysis only if licensed. Exit 0 / 3 / 4.

RESULT: complete committed set -> COMPLETE and analysis == CONFIRM.analysis.json exactly. Every corruption kind in the packet is
detected on the Z80 fixture; removing any one shard gives INCOMPLETE and no verdict (the C-017 gap). 40 tests green; RED first;
13 verify.py mutants, 12 killed, 1 equivalent. Manifest is derived from the PREREGISTRATION s6 design, not the rows.

RECORDED CHOICES (reversible; revisit if the trigger below fires):
1. Manifest pinned by sha256 in z80.py (a seal only proves "not edited"). Revisit: if the registry later pins manifests, move the pin there.
2. meta_sha256 pins the whole meta incl. wall_s/host (right for frozen shards). Revisit: first experiment whose legitimate re-run changes meta.
3. Trigger = one conjunction of equalities + count. Revisit: first preregistered sequential/statistical stopping rule.
4. SUBSTITUTED vs ALTERED needs the engine's native rows digest (optional hook); without it all byte differences read ALTERED.

PROPOSED REGISTRY ENTRY (Palamedes owns rso/registry/; not edited): name experiment-completeness; stage AUTHOR_TESTED; files
rso/completeness/{manifest,verify}.py; tests rso/completeness/tests/test_completeness.py; qualified_scope: detects presented evidence that
differs from, or is absent against, a sealed manifest; not_qualified_for: whether the frozen shards were produced by the registered
procedure, stopping rules beyond a count trigger; users: z80-completeness wrapper (rso/completeness/z80.py).
Suggested next use: every future sharded campaign (Aether, C-018-T020/T021) builds its manifest before launch and calls verify first.

Caveats: RED was import-level (module absent), per-test bite shown by mutants; wrapper is the only Z80 analyzer that refuses
shard loss -- the frozen rso.z80.analysis CLI is unchanged and will still accept five shards if called directly.
