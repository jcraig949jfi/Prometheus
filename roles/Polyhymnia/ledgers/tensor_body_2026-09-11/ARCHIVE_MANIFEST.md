# Polyhymnia tensor body -- archaeological residue archive (POLY-XL-01, decided by the operator 2026-09-11)

Currency: 2026-09-11. Operator ruling (roles/Polyhymnia/prompts/
2026-09-11_reactivation_direction/OPERATOR_DIRECTIVE.md): "archive it as
archaeological residue with SHA-256 and enough provenance to recover it
later. Do not treat it as the canonical representation substrate for 2.0
and do not spend time rehabilitating it yet."

This directory is a byte-identical second copy of the untracked runtime
files of agents/polyhymnia/ as they stood on the canonical checkout of
host SKULLPORT (M1) on 2026-09-11. Originals were not modified. Stored
`-text` (see .gitattributes) so git never normalises line endings; the
sha256 below is therefore the sha256 of the file on disk AND of the git
blob. Precedent: roles/Talos/ledgers/corpus_shards_2026-09-11/ (D-26).

## 1. Files, sizes, sha256 (identical on the source and archive sides; cmp exit 0 for every file)

    tesserae.jsonl                      11,529,754 B  020f5a43fe7e1ca4e88189a67ef15e70cc323f7fa08751bf5624a961ae149010
      (the tensor body; source agents/polyhymnia/tensor/tesserae.jsonl, mtime 2026-05-30 06:01 local)
    relations.jsonl                          1,700 B  7624cb183a7a69898b5756ff8e7b994d380795e36f7a891d48fec43a1e7207b6
      (17 lineage edges; ALSO tracked at agents/polyhymnia/tensor/relations.jsonl; copied for a self-contained archive)
    state_2026-05-30.json                  802,883 B  6961fe9773b8027257268eb3a19c0cc9502399a67971b1bf8ecdf2a5b6cb64fd
      (source agents/polyhymnia/state/state.json: rotation cursor, per-scour path_mtimes, counters)
    events_2026-05-24_to_05-30.jsonl       216,767 B  7ecceb3825861c0fe52030e42819099e62626beb6aed0542073b1710258d1f3f
      (source agents/polyhymnia/events.jsonl: 297 tick_end records and the self-improvement events)
    polyhymnia.pid.stale                        89 B  c182aa3471b1015ce70b1f889b6299d6e97ad59ac0ce48f75cd0e443fed7b65c
      (source agents/polyhymnia/polyhymnia.pid: pid 23960, SKULLPORT, 2026-05-25T11:41Z; the pid is not alive)
    logs/polyhymnia.log                    174,563 B  5f58062ba9a10da91db2a0218da6ba623acb6fd269c310ad4f65ece4f58ef90f
    logs/polyhymnia.stderr.log               5,833 B  4c76210a85be7336be4f2a7d56845abff4b541504d00eb9c6ba3fc82b71ea060
    logs/polyhymnia.stdout.log             170,337 B  af541e86c38a654548e832964b73067db232daac7291a64f63dde509ae0e68f2

Command used: cp, then `cmp <src> <dst>` per file (all exit 0), then
`sha256sum` on both sides (all equal). Recorded 2026-09-11 ~15:52 UTC.

## 2. NOT archived, with the reason

    agents/polyhymnia/artifacts/   297 files, 194,684,222 B (250 null_*.json + 47 tick_*.json)

Each is a per-tick snapshot whose bulk is the scour's path_mtimes map
(the same ~800 KB dictionary repeated 297 times). The delta each tick
produced is already in events_2026-05-24_to_05-30.jsonl (candidates,
new_tesserae, merged) and the final state is state_2026-05-30.json.
Recoverable content: none beyond those two files. Left in place,
untracked, on SKULLPORT; if the host changes they are lost and nothing
is lost with them. Reversible: the operator may ask for them archived.

The tracked registries agents/polyhymnia/tensor/axes/*.jsonl (8 files)
are in git already and are not duplicated here.

## 3. Census of the body (computed from the archived copy, 2026-09-11; the command is in section 5)

    lines                       4,917   (0 unparseable)
    top-level keys              tessera_id, coords, tags, content, source, confidence, first_seen_at, last_seen_at (all 4,917)
    distinct tessera_id         2,415   (the body is append-only; a re-seen tessera is re-appended, so lines > cells)
    distinct coord signatures      13
    scour of origin             prometheus_self: 4,917 (100%)

    axis                  cardinality   values
    time                          1     2026 (4,917)
    discipline                    8     cs.DS 2,574 / math.HO 1,659 / fringe 480 / (5 others)
    object_kind                   2     implementation 3,541 / algorithm 1,376
    structural_rank               1     null
    abstraction_level             1     implementation
    substrate_yield_type          1     null
    epistemic_status              1     EXTRACTED
    data_modality                 1     code
    code_language                 1     python

Reading, stated once and not repeated as a claim elsewhere: six of nine
coordinate axes were constant over the entire body, and the whole
"N-dimensional tensor" occupied 13 cells. That is what a single grep
scour of one Python repository produces; it is the measured shape of
the accumulate-before-consumer architecture the operator ruled against,
and it is the reason the body is residue rather than a substrate.

## 4. How to recover

    git show <sha>:roles/Polyhymnia/ledgers/tensor_body_2026-09-11/tesserae.jsonl > tesserae.jsonl
    sha256sum tesserae.jsonl   # must print 020f5a43...

Reader code: agents/polyhymnia/tensor.py (PolyhymniaTensor) as of
57533fa76 reads this schema; the axes registries it expects are
agents/polyhymnia/tensor/axes/. Nothing in Prometheus 2.0 depends on
this body (git grep polyhymnia at 57533fa76: only
agents/_shared/mutation_registry.py names the seat, as a registry row).

## 5. Census command (reproducible)

    python - <<'EOF'
    import json, collections
    D="roles/Polyhymnia/ledgers/tensor_body_2026-09-11"
    ids=set(); sigs=set(); axes=collections.defaultdict(collections.Counter)
    for line in open(D+"/tesserae.jsonl","rb"):
        r=json.loads(line); ids.add(r["tessera_id"]); c=r["coords"]
        sigs.add(json.dumps(c,sort_keys=True))
        for a,v in c.items(): axes[a][str(v)]+=1
    print(len(ids), len(sigs), {a:len(c) for a,c in axes.items()})
    EOF
