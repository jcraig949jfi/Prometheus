"""
register_specimen — one-line helper for workers to write task completions
into signals.specimens per the tracking mandate.

Usage:
    from agora.register_specimen import register

    register(
        task_id='wsw_F011',
        feature_id='F011',
        claim='GUE first-gap deficit — n=2M walk',
        status='resolves_uniformly',  # not SURVIVED/KILLED per Pattern 14
        projections=['P050','P051','P021','P023','P024','P025','P026'],
        feature_type='flat_below_gue',
        invariance_profile={'P050': 1, 'P051': 1, 'P021': 1, ...},
        effect_size=0.110,
        z_score=-383.0,
        p_value=0.0,
        n_samples=2009089,
        machinery='balanced per-rank stratification + N(T) unfold',
        tautology_ok=True,
        source_commit='6ae831f4',
        source_worker='Harmonia_M2_sessionC',
        output_file='cartography/docs/wsw_F011_results.json',
        interest=0.85,
        # optional: domain_a, domain_b, kill_test
    )

Returns the specimen_id. Raises on error (never silent-fails — we want you to
know if the registry write didn't land).
"""
import json
import os
import psycopg2


DEFAULT_DSN = dict(
    host=os.environ.get('AGORA_PG_HOST', '192.168.1.176'),
    port=int(os.environ.get('AGORA_PG_PORT', 5432)),
    dbname='prometheus_fire',
    user='postgres',
    password='prometheus',
)


def register(
    task_id: str,
    feature_id: str,
    claim: str,
    status: str,
    projections: list,
    feature_type: str,
    invariance_profile: dict,
    effect_size: float = None,
    z_score: float = None,
    p_value: float = None,
    n_samples: int = None,
    machinery: str = '',
    tautology_ok: bool = True,
    tautology_note: str = '',
    source_commit: str = '',
    source_worker: str = '',
    output_file: str = '',
    interest: float = 0.5,
    domain_a: str = None,
    domain_b: str = None,
    kill_test: str = None,
    dsn: dict = None,
    sweep_outcome=None,
    sweep_override: bool = False,
    sweep_override_reason: str = '',
) -> int:
    """Insert a row into signals.specimens. Returns specimen_id.

    If `sweep_outcome` is provided (a SweepOutcome from
    `harmonia.sweeps.sweep_signature`), its verdict is recorded in
    `data_provenance.sweeps`. A BLOCK verdict halts the write unless
    `sweep_override=True` with a non-empty `sweep_override_reason`.
    Overrides are logged to the sweep_results_log.

    Callers that run correlational claims SHOULD pre-compute a sweep
    outcome with a Pattern 30 CouplingCheck; non-correlational claims
    (variance deficit, sign-uniform, calibration anchor) may omit.
    """

    valid_statuses = {
        'resolves_uniformly', 'resolves_partial', 'collapses', 'refined',
        'stale_pattern_19', 'calibration_confirmed', 'axis_class_orphan',
        'reproduce_real_not_monotone', 'tautology'
    }
    if status not in valid_statuses:
        raise ValueError(
            f"status '{status}' not in {valid_statuses}. "
            "Avoid 'SURVIVED'/'KILLED' per Pattern 14 (Verdict vs Shape)."
        )

    if sweep_outcome is not None:
        from harmonia.sweeps.runner import SweepBlocked, log_outcome
        if sweep_outcome.overall == 'BLOCK' and not sweep_override:
            raise SweepBlocked(sweep_outcome)
        if sweep_outcome.overall == 'BLOCK' and sweep_override:
            if not sweep_override_reason:
                raise ValueError(
                    'sweep_override=True requires a non-empty '
                    'sweep_override_reason string')
            sweep_outcome.override = True
            sweep_outcome.override_reason = sweep_override_reason
        log_outcome(sweep_outcome, context={
            'context_id': f'{task_id}:{feature_id}',
            'task_id': task_id,
            'feature_id': feature_id,
            'source_worker': source_worker,
        })

    data_provenance = {
        'feature_id': feature_id,
        'projections': projections,
        'feature_type': feature_type,
        'invariance_profile': invariance_profile,
        'effect_size': effect_size,
        'z_score': z_score,
        'p_value': p_value,
        'n_samples': n_samples,
        'machinery_required': machinery,
        'tautology_check': {'checked': True, 'ok': tautology_ok, 'note': tautology_note},
        'source_task': task_id,
        'source_commit': source_commit,
        'source_worker': source_worker,
        'output_file': output_file,
        'sweeps': (sweep_outcome.to_provenance_block()
                   if sweep_outcome is not None else None),
    }

    conn = psycopg2.connect(**(dsn or DEFAULT_DSN))
    try:
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO signals.specimens
                (claim, status, interest, kill_test, domain_a, domain_b, data_provenance)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING specimen_id
            """,
            (claim, status, interest, kill_test, domain_a, domain_b,
             json.dumps(data_provenance, default=str)),
        )
        specimen_id = cur.fetchone()[0]
        conn.commit()
        return specimen_id
    finally:
        conn.close()


def register_from_task_result(
    task_id: str,
    completed_by: str,
    result: dict,
    feature_id: str,
    commit_hash: str = '',
    interest: float = 0.5,
) -> int:
    """Convenience: unpack a standard WORK_COMPLETE result dict and register.

    The result dict must contain: status, summary, output_path.
    It may contain any of: verdict, effect_size, z_score, p_value, n_samples,
    invariance_profile, machinery, tautology_check, etc.
    """
    # Map common result shapes to register() args
    invariance = result.get('invariance_profile') or result.get('verdict_by_projection', {})
    # Convert string verdicts "+1"/"-1" to ints if needed
    invariance_int = {}
    for k, v in invariance.items():
        if isinstance(v, str):
            try: invariance_int[k] = int(v)
            except ValueError: invariance_int[k] = v
        else:
            invariance_int[k] = v

    return register(
        task_id=task_id,
        feature_id=feature_id,
        claim=result.get('summary', f'{task_id} result')[:400],
        status=_map_status(result.get('status', ''), result.get('verdict', '')),
        projections=list(invariance_int.keys()),
        feature_type=result.get('feature_type', 'unknown'),
        invariance_profile=invariance_int,
        effect_size=result.get('effect_size'),
        z_score=result.get('z_score'),
        p_value=result.get('p_value'),
        n_samples=result.get('n_samples') or result.get('n_curves') or result.get('n_evaluated'),
        machinery=result.get('machinery_required', result.get('method_note', '')),
        tautology_ok=True,  # overrideable
        source_commit=commit_hash,
        source_worker=completed_by,
        output_file=result.get('output_path', ''),
        interest=interest,
    )


def _map_status(status: str, verdict: str) -> str:
    """Map legacy SURVIVED/KILLED words to the charter-era status vocabulary."""
    s = (status or '').lower()
    v = (verdict or '').lower()
    combined = f"{s} {v}"

    if 'killed' in combined and 'pattern 19' in combined or 'stale' in combined:
        return 'stale_pattern_19'
    if 'killed' in combined:
        return 'collapses'
    if 'survived' in combined or 'success' in combined:
        return 'resolves_uniformly'  # worker should override if partial
    if 'refined' in combined:
        return 'refined'
    if 'tautology' in combined:
        return 'tautology'
    if 'reproduce_real' in combined:
        return 'reproduce_real_not_monotone'
    return 'resolves_partial'


if __name__ == '__main__':
    # Smoke test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        sid = register(
            task_id='_smoke_test',
            feature_id='F999',
            claim='smoke test specimen',
            status='resolves_uniformly',
            projections=['P001'],
            feature_type='flat',
            invariance_profile={'P001': 1},
            source_worker='Harmonia_M2_sessionA',
            interest=0.0,
        )
        print(f'Smoke test inserted specimen_id={sid}')
