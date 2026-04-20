"""
Build the narrative MD logs for gen_05, gen_03, gen_07 from the JSON
outputs produced by the executors.
"""
import json, datetime as dt
from pathlib import Path
from collections import Counter, defaultdict

now = dt.datetime.now(dt.timezone.utc).isoformat()


# ============================================================================
# gen_05: kill_replay_log.md
# ============================================================================

g5 = json.loads(Path('harmonia/memory/kill_replay_candidates.json').read_text(encoding='utf-8'))
seeded = g5['seeded']

# per-F-ID breakdown
per_f = defaultdict(list)
for s in seeded:
    per_f[s['feature_id']].append(s)

# also show "no candidate" kills if any
all_candidates = g5['all_candidates']
f_seen = set(per_f.keys())

lines = []
lines.append('# Kill-Replay Log — Generator #5')
lines.append('')
lines.append('**Generated:** {}'.format(g5['generated_at']))
lines.append('**Source:** `docs/prompts/gen_05_attention_replay.md` @ commit `ac354b26`')
lines.append('**Runner:** Harmonia_M2_sessionA_20260420')
lines.append('')
lines.append('## Purpose')
lines.append('')
lines.append('Every killed F-ID is terrain. When a new projection lands in the catalog, '
             'every killed F-ID becomes a re-test candidate against that projection. '
             'This log records the initial seeding and the ongoing audit trail.')
lines.append('')
lines.append('## Summary')
lines.append('')
lines.append('- **Killed / artifact F-IDs inspected:** 13')
lines.append('- **Candidate (F, P) pairs enumerated:** {}'.format(g5['n_candidates_total']))
lines.append('- **Tasks seeded this tick:** {}'.format(g5['n_seeded']))
lines.append('- **Per-F-ID guarantee:** ≥ 1 candidate per killed F-ID')
lines.append('')

lines.append('## Scoring function (v1)')
lines.append('')
lines.append('```')
lines.append('score = adjacency + 2 * type_novelty + 1.5 * recency')
lines.append('```')
lines.append('')
lines.append('- **adjacency** — count of live specimens for which this projection resolves at +1 or +2 (higher = more validated lens).')
lines.append('- **type_novelty** — 1 if this projection\'s type does not appear in the F-ID\'s already-tested set.')
lines.append('- **recency** — 1.0 if P-ID ≥ 100 (added post-sessionA 2026-04-17), 0.5 if P-ID ≥ 28, else 0.')
lines.append('')
lines.append('**Known concentration:** P023 (Rank stratification) dominates top-of-queue because it resolves 9 live specimens. The per-F-ID guarantee ensures every killed F-ID still gets a replay slot even when P023 saturates; the Map-Elites meta-allocator (#1) will eventually diversify by enforcing behavior-cell uniqueness in quality-diversity mode.')
lines.append('')

lines.append('## Seeded replay tasks ({})'.format(g5['n_seeded']))
lines.append('')
lines.append('| # | F-ID | P-ID | P type | Score | Task ID |')
lines.append('|---|---|---|---|---|---|')
for i, s in enumerate(seeded, 1):
    tid = 'replay_{}_{}_20260420'.format(s['feature_id'], s['projection_id'])
    lines.append('| {} | {} | {} | {} | {:.2f} | `{}` |'.format(
        i, s['feature_id'], s['projection_id'], s['projection_type'], s['score'], tid))
lines.append('')

lines.append('## Per-killed-F-ID candidate summary')
lines.append('')
for fid in sorted(per_f.keys()):
    cs = per_f[fid]
    lines.append('- **{}** — {} replay task(s) seeded: {}'.format(
        fid, len(cs), ', '.join('`{}`'.format(c['projection_id']) for c in cs)))
lines.append('')

lines.append('## Epistemic discipline applied')
lines.append('')
lines.append('1. **Resurrections are high scrutiny.** Any (killed F, P) that returns +1 or +2 must pass `symbols/protocols/null_protocol_v1.md` claim-class check before promotion, AND manual Pattern 30 gate (gen_06 not yet live).')
lines.append('2. **Kill reinforcement is not waste.** Reinforced kills get logged here as Pattern 13 anchor-growth.')
lines.append('3. **No silent promotion.** Any tier change on a killed F-ID routes through `decisions_for_james.md`.')
lines.append('4. **Pattern 19 applies.** Reopening a kill changes the instrument reading of a prior measurement; provenance block required on any updated F-ID description.')
lines.append('')

lines.append('## Audit trail')
lines.append('')
lines.append('As replay tasks complete and verdicts arrive, append entries here:')
lines.append('')
lines.append('```')
lines.append('### YYYY-MM-DD [task_id]')
lines.append('- Verdict: KILL_REINFORCED | RESURRECTED | INFORMATIVE_NULL')
lines.append('- z-score / effect: ...')
lines.append('- Null used: NULL_*@v* with stratifier')
lines.append('- Pattern 30 gate: CLEAR / WARN / BLOCK')
lines.append('- Action: tensor cell updated / no change / escalated')
lines.append('```')
lines.append('')

lines.append('## Composition notes')
lines.append('')
lines.append('- **Waiting on #2 null-family** to upgrade each replay from single-null to family-vector.')
lines.append('- **Waiting on #6 pattern auto-sweeps** to replace manual Pattern 30 gate.')
lines.append('- **Waiting on #3 cross-domain transfer** to supply new P-IDs (every new P-ID triggers a fresh replay sweep).')
lines.append('')

lines.append('## Version')
lines.append('')
lines.append('- **v1.0** — 2026-04-20 — initial seeding under generator pipeline v1.0.')

Path('harmonia/memory/kill_replay_log.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Wrote harmonia/memory/kill_replay_log.md ({} lines)'.format(len(lines)))


# ============================================================================
# gen_03: domain_catalog.md
# ============================================================================

g3 = json.loads(Path('harmonia/memory/transfer_matrix.json').read_text(encoding='utf-8'))
domains = g3['domains']
cells = g3['cells']
verdict_counts = g3['verdict_counts']

lines = []
lines.append('# Domain Catalog — Generator #3 Phase 1')
lines.append('')
lines.append('**Generated:** {}'.format(g3['generated_at']))
lines.append('**Source:** `docs/prompts/gen_03_cross_domain_transfer.md` @ commit `ac354b26`')
lines.append('**Runner:** Harmonia_M2_sessionA_20260420')
lines.append('')
lines.append('## Purpose')
lines.append('')
lines.append('Canonical enumeration of the data domains we currently have measurement access to. '
             'Every domain has a schema, cardinality, and list of primary F-IDs that inhabit it. '
             'Phase 2 classifies each projection\'s applicability to each domain (the transfer matrix).')
lines.append('')
lines.append('## Domains ({})'.format(len(domains)))
lines.append('')
for d in domains:
    lines.append('### {} — {}'.format(d['id'], d['name']))
    lines.append('')
    lines.append('- **Data source:** `{}`'.format(d['data_source']))
    lines.append('- **Cardinality:** ~{:,}'.format(d['cardinality']))
    lines.append('- **Primary fields:** `{}`'.format('`, `'.join(d['fields'])))
    lines.append('- **Primary F-IDs already inhabiting this domain:** {}'.format(
        ', '.join(d['primary_F_IDs'])))
    lines.append('')

lines.append('## Transfer matrix summary')
lines.append('')
lines.append('- **Projections:** {}'.format(g3['n_projections']))
lines.append('- **Domains:** {}'.format(g3['n_domains']))
lines.append('- **Total (P, D) cells:** {}'.format(g3['n_cells']))
lines.append('- **Verdict distribution:**')
for v, n in sorted(verdict_counts.items(), key=lambda x: -x[1]):
    lines.append('  - `{}`: {} ({:.1%})'.format(v, n, n / g3['n_cells']))
lines.append('')

lines.append('## Applies-directly breakdown by projection type')
lines.append('')
by_type = defaultdict(lambda: defaultdict(int))
for c in cells:
    if c['verdict'] == 'applies_directly':
        by_type[c['projection_type']][c['domain_id']] += 1
lines.append('| Projection type | ' + ' | '.join(d['id'] for d in domains) + ' |')
lines.append('|---|' + '|'.join('---' for _ in domains) + '|')
for ptype in sorted(by_type):
    row = [ptype]
    for d in domains:
        row.append(str(by_type[ptype].get(d['id'], 0)))
    lines.append('| ' + ' | '.join(row) + ' |')
lines.append('')

lines.append('## Heuristic classification rules (v1)')
lines.append('')
lines.append('See `harmonia/tmp_gen03_exec.py::classify()`. Core logic:')
lines.append('')
lines.append('- **Agnostic scorers** (null_model, preprocessing, feature_distribution, etc.) default to `applies_directly` unless the projection references a domain-specific data object (e.g., zero-spacings require L-function origin; Mahler measure requires polynomial representative).')
lines.append('- **Stratifications** are `applies_directly` iff the stratifying field appears in the domain\'s schema; `inapplicable` otherwise.')
lines.append('- **Ambiguous** cases resolve to `applies_with_adaptation` — these become tasks to define the adapter.')
lines.append('')
lines.append('**Known limitation:** the v1 classifier is a keyword heuristic. False-positives (marked directly-applicable but actually need adaptation) and false-negatives both exist. Phase 3 audits against specimen-level runs will calibrate the classifier over time.')
lines.append('')

lines.append('## Epistemic discipline')
lines.append('')
lines.append('1. **An adapter is a new projection.** Any `applies_with_adaptation` run that produces a valid measurement emits a new P-ID via `reserve_p_id()`, not a re-use of the origin ID.')
lines.append('2. **Apparent transfers are Pattern 5 candidates.** A projection that works in two domains may be measuring shared known structure (Langlands, class field theory). Pattern 5 check required before novelty claim.')
lines.append('3. **Pattern 30 gate** applies to every correlation-based transfer.')
lines.append('4. **Null-protocol claim class** inherits with the projection.')
lines.append('')

lines.append('## Next steps')
lines.append('')
lines.append('1. Seeded transfer tasks: see `harmonia/memory/transfer_tasks_seeded.json` (60 tasks).')
lines.append('2. As each task completes, update `transfer_matrix.json` with realized verdicts.')
lines.append('3. New P-IDs emerging from adapters get added to the catalog.')
lines.append('4. Co-mined with gen_05 (attention-replay): every new P-ID triggers replays on killed F-IDs.')
lines.append('')

lines.append('## Version')
lines.append('')
lines.append('- **v1.0** — 2026-04-20 — initial domain catalog + transfer matrix under generator pipeline v1.0.')

Path('harmonia/memory/domain_catalog.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Wrote harmonia/memory/domain_catalog.md ({} lines)'.format(len(lines)))


# ============================================================================
# gen_07: literature_diff_log.md + calibration_anchors_from_lit.md + cadence
# ============================================================================

g7 = json.loads(Path('harmonia/memory/literature_diff_entries.json').read_text(encoding='utf-8'))
entries = g7['entries']
cat_counts = g7['classification_counts']

# ---- literature_diff_log.md
lines = []
lines.append('# Literature Diff Log — Generator #7')
lines.append('')
lines.append('**Generated:** {}'.format(g7['generated_at']))
lines.append('**Source:** `docs/prompts/gen_07_literature_diff.md` @ commit `ac354b26`')
lines.append('**Runner:** Harmonia_M2_sessionA_20260420')
lines.append('**Paper cache:** `{}`'.format(g7['source']))
lines.append('')
lines.append('## Summary')
lines.append('')
lines.append('- **Papers processed:** {}'.format(g7['n_papers']))
lines.append('- **Diff entries generated:** {} (papers × matched F-IDs)'.format(g7['n_diff_entries']))
lines.append('- **Classification distribution:**')
for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
    lines.append('  - `{}`: {} ({:.1%})'.format(c, n, n / g7['n_diff_entries']))
lines.append('')

lines.append('## Classification schema')
lines.append('')
lines.append('| Category | Meaning | Action |')
lines.append('|---|---|---|')
lines.append('| REPRODUCTION | Paper claim matches our measurement within uncertainty | Log as calibration reinforcement |')
lines.append('| DIVERGENCE_NUMERICAL | Paper numerical claim differs beyond uncertainty | Seed debug task (priority -1.5) |')
lines.append('| DIVERGENCE_STRUCTURAL | Paper makes a different claim class / framing | Seed reconciliation task (priority -1.0) |')
lines.append('| RETRACTION_CROSS_CHECK | Paper touches an F-ID we retracted | Cross-check retraction reasoning against paper |')
lines.append('| KILL_REINFORCEMENT_CANDIDATE | Paper touches a killed F-ID | Feed into gen_05 replay queue |')
lines.append('| CANDIDATE_NEW_F_ID | Paper claims a structure we have not registered | Conductor evaluates for new F-ID opening |')
lines.append('')

# ---- per category, top entries
lines.append('## Entries by classification (top 5 per category)')
lines.append('')
for cat in ['REPRODUCTION','DIVERGENCE_STRUCTURAL','DIVERGENCE_NUMERICAL',
            'RETRACTION_CROSS_CHECK','KILL_REINFORCEMENT_CANDIDATE','CANDIDATE_NEW_F_ID']:
    es = [e for e in entries if e['classification'] == cat][:5]
    if not es: continue
    lines.append('### {} ({} total, showing 5)'.format(cat, cat_counts.get(cat, 0)))
    lines.append('')
    for e in es:
        fid = e.get('f_id', '—')
        auth = ', '.join(e.get('paper_authors') or [])[:50] or '—'
        yr = e.get('paper_year') or '?'
        title = e.get('paper_title', '')[:100]
        lines.append('- **{} · {} ({})** — {}'.format(fid, auth, yr, title))
        if e.get('paper_url'):
            lines.append('  - URL: <{}>'.format(e['paper_url']))
        if e.get('paper_tldr'):
            lines.append('  - TL;DR: _{}_'.format(e['paper_tldr'][:160]))
        lines.append('  - Rationale: {}'.format(e['rationale']))
    lines.append('')

lines.append('## Epistemic discipline applied')
lines.append('')
lines.append('1. **LLM-assisted classification is provisional.** The v1 classifier uses tier + keyword heuristics on the paper TL;DR. Any DIVERGENCE_NUMERICAL re-classification into an action item requires human conductor verification of the paper\'s specific claim.')
lines.append('2. **Paraphrase drift hazard.** TL;DR fields are Semantic Scholar summaries, not author text. Before emitting a tensor-mutation task from a diff, re-read the abstract verbatim.')
lines.append('3. **Publication bias.** Reproductions over-represent easy measurements; divergences over-represent controversial claims. Do not aggregate as if this were an unbiased sample of truth.')
lines.append('4. **Pattern 30 gate** applies to every CANDIDATE_NEW_F_ID before registration.')
lines.append('')

lines.append('## Next steps')
lines.append('')
lines.append('1. Manual conductor review of top-10 CANDIDATE_NEW_F_ID entries — which deserve F-ID allocation?')
lines.append('2. RETRACTION_CROSS_CHECK entries feed F043 audit continuation.')
lines.append('3. Cadence runbook at `harmonia/memory/literature_diff_cadence.md` for scheduled re-runs.')
lines.append('4. As Aporia paper stream refreshes, re-run gen_07 executor; incremental diff.')
lines.append('')

lines.append('## Version')
lines.append('')
lines.append('- **v1.0** — 2026-04-20 — initial diff pass over 190-paper cache from first map-building wave.')

Path('harmonia/memory/literature_diff_log.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Wrote harmonia/memory/literature_diff_log.md ({} lines)'.format(len(lines)))


# ---- calibration_anchors_from_lit.md
repros = [e for e in entries if e['classification'] == 'REPRODUCTION']
lines = []
lines.append('# Calibration Anchors from Literature')
lines.append('')
lines.append('**Generated:** {}'.format(now))
lines.append('**Purpose:** Running list of paper-based reproductions of our F-IDs. Each entry is a pointer to external literature that corroborates (or is claimed to corroborate) a measured F-ID. Strengthens the calibration tier.')
lines.append('')
lines.append('**Source:** gen_07 literature diff v1, entries classified as REPRODUCTION.')
lines.append('**Count this pass:** {}'.format(len(repros)))
lines.append('')
lines.append('## Entries')
lines.append('')
by_fid = defaultdict(list)
for e in repros:
    by_fid[e.get('f_id', '?')].append(e)
for fid in sorted(by_fid):
    lines.append('### {}'.format(fid))
    lines.append('')
    for e in by_fid[fid]:
        auth = ', '.join(e.get('paper_authors') or [])[:60] or '—'
        yr = e.get('paper_year') or '?'
        title = e.get('paper_title', '')[:110]
        lines.append('- **{} ({})** — {}'.format(auth, yr, title))
        if e.get('paper_arxiv'):
            lines.append('  - arXiv: `{}`'.format(e['paper_arxiv']))
        if e.get('paper_url'):
            lines.append('  - URL: <{}>'.format(e['paper_url']))
        lines.append('  - Rationale: {}'.format(e['rationale']))
    lines.append('')

lines.append('## Discipline')
lines.append('')
lines.append('1. Entries here are PROVISIONAL until human-verified. The v1 classifier is keyword-based; a paper tagged REPRODUCTION may actually make a subtly different claim.')
lines.append('2. A strong reproduction (paper\'s specific numerical claim within 1 sigma of ours) is promotable to an explicit calibration-anchor reference. Provisional entries that clear human review get this upgrade.')
lines.append('3. Calibration anchors are load-bearing — see `pattern_library.md` Pattern 7. Any anchor failure triggers instrument-health investigation.')
lines.append('')

Path('harmonia/memory/calibration_anchors_from_lit.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Wrote harmonia/memory/calibration_anchors_from_lit.md ({} lines)'.format(len(lines)))


# ---- literature_diff_cadence.md
lines = []
lines.append('# Literature Diff Cadence Runbook')
lines.append('')
lines.append('**Purpose:** Turn gen_07 from a one-shot into a scheduled cadence.')
lines.append('**Owner:** Harmonia conductor (any session).')
lines.append('**Cadence target:** weekly batch pull + diff.')
lines.append('')
lines.append('## Weekly procedure')
lines.append('')
lines.append('1. Pull latest paper batch from Aporia stream (or S2 API directly) since last run timestamp. Store at `aporia/data/literature_scan_<yyyymmdd>.json`.')
lines.append('2. Run `python harmonia/tmp_gen07_exec.py` (or promoted `harmonia/runners/literature_diff.py` once it exists).')
lines.append('3. Script produces:')
lines.append('   - `harmonia/memory/literature_diff_entries.json` (machine-readable, overwrite-on-run)')
lines.append('   - Append-only entries to `harmonia/memory/literature_diff_log.md`')
lines.append('   - Append-only entries to `harmonia/memory/calibration_anchors_from_lit.md`')
lines.append('4. Conductor reviews top-priority entries manually (CANDIDATE_NEW_F_ID, DIVERGENCE_*, RETRACTION_CROSS_CHECK).')
lines.append('5. For each reviewed item: either promote to Agora task, retract the classification, or log as noted.')
lines.append('6. Commit.')
lines.append('')
lines.append('## Entry-to-task promotion rules')
lines.append('')
lines.append('| Classification | Promotion condition | Priority |')
lines.append('|---|---|---|')
lines.append('| REPRODUCTION | Auto-log; no task | — |')
lines.append('| DIVERGENCE_NUMERICAL | Paper claim extracted + human-verified | -1.5 |')
lines.append('| DIVERGENCE_STRUCTURAL | Claim-class mismatch confirmed by conductor | -1.0 |')
lines.append('| RETRACTION_CROSS_CHECK | Always, but bundled per F-ID | -1.0 |')
lines.append('| KILL_REINFORCEMENT_CANDIDATE | Feed into gen_05 candidate pool; don\'t double-seed | — |')
lines.append('| CANDIDATE_NEW_F_ID | Conductor approves F-ID registration | -0.5 |')
lines.append('')
lines.append('## PROBLEM_TO_FIDS map maintenance')
lines.append('')
lines.append('The diff executor uses a static `PROBLEM_TO_FIDS` map. As new F-IDs land, this map must be extended. Check: `git log --follow harmonia/tmp_gen07_exec.py` for history; bump when F-ID roster changes.')
lines.append('')
lines.append('## Epistemic limits')
lines.append('')
lines.append('- Semantic matching is lossy. A paper about "the 42% CFKRS-excised deficit" may be the same finding as F011\'s "~38% residual" under different framing — the matcher can miss this. Human review required for anything tensor-mutating.')
lines.append('- Paraphrase drift: TL;DRs are S2 summaries, not author text. Cite abstracts verbatim in the diff log when promoting.')
lines.append('- Pattern 30 gate: before registering a new F-ID from literature, run the algebraic-coupling diagnostic on the paper\'s claim.')
lines.append('')
lines.append('## Version')
lines.append('')
lines.append('- **v1.0** — 2026-04-20 — initial cadence under generator pipeline v1.0.')

Path('harmonia/memory/literature_diff_cadence.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Wrote harmonia/memory/literature_diff_cadence.md ({} lines)'.format(len(lines)))

print()
print('All 4 log / catalog files written.')
