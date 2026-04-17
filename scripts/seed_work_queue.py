"""
Seed the work queue with initial tasks.

Run by sessionA when bootstrapping the multi-worker system.
"""
import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

from agora.work_queue import push_task, queue_status


INITIAL_TASKS = [
    # ---- Weak signal walks (low priority = first out of queue) ----
    {
        "task_id": "wsw_F011",
        "task_type": "weak_signal_walk",
        "priority": -10.0,  # urgent
        "payload": {
            "specimen_id": "F011",
            "specimen_label": "GUE 14% first-gap deficit",
            "target_projections": ["P050", "P051", "P021", "P023", "P024", "P025", "P026"],
            "data_source": "bsd_joined + prometheus_fire.zeros.object_zeros",
            "method": "For each projection, compute within-stratum spacing variance vs GUE Wigner (0.178). Report per-projection deviation and n_stratified. Do NOT run H09 conductor-window yet — that's a follow-up.",
            "output_path": "cartography/docs/wsw_F011_results.json",
        },
        "expected_output": {
            "schema": {
                "per_projection": "dict: projection_id -> {n, var, deviation_from_gue, z_score}",
                "verdict_by_projection": "dict: projection_id -> '+1' | '-1' | '0'",
                "shape_summary": "1-2 sentence description of invariance pattern",
            },
        },
        "required_qualification": "basic",
    },
    {
        "task_id": "wsw_F012",
        "task_type": "weak_signal_walk",
        "priority": -9.0,
        "payload": {
            "specimen_id": "F012",
            "specimen_label": "Möbius bias at g2c aut groups, |z|=6.15",
            "target_projections": ["P022", "P040", "P043", "P023"],
            "data_source": "g2c_curves + Mobius sieve",
            "method": "Run P040 (aut_grp label permutation null, 1000 shuffles) on the |z|=6.15 signal. Identify which specific aut_grp carries the signal (per-stratum z). Check for n_per_stratum adequacy (>= 100). P023 as joint stratification to check rank-mediation.",
            "output_path": "cartography/docs/wsw_F012_results.json",
            "WARNING": "This task was previously handed to Harmonia_M2_sessionB pending James HITL authorization. DO NOT CLAIM without checking Agora main for authorization first. If sessionB already ran it, claim only if results need independent verification.",
        },
        "expected_output": {
            "schema": {
                "per_aut_grp": "dict: aut_grp_id -> {n, z, signed_sum_mu, survives_perm_null}",
                "permutation_null_summary": "real |z| vs null distribution (mean, std, p-value)",
                "verdict": "SURVIVES | KILLED | INCONCLUSIVE + shape",
            },
        },
        "required_qualification": "basic",
        "blocked_on": "HITL authorization from James for compute run",
    },

    # ---- Catalog entries (from coordinate_system_catalog.md Section 9 "Not-Yet-Catalogued") ----
    {
        "task_id": "catalog_katz_sarnak",
        "task_type": "catalog_entry",
        "priority": 0.0,
        "payload": {
            "coordinate_system": "Katz-Sarnak family symmetry type",
            "brief": "Document the Katz-Sarnak symmetry classification (SO_even, SO_odd, U, Sp) as a stratification projection. What features does it resolve in zero statistics? What does it collapse?",
            "reference_materials": [
                "Katz-Sarnak (1999) 'Zeros of zeta functions and symmetries'",
                "Conrey-Farmer-Mezzadri-Snaith (2008) on L-function families",
            ],
            "output_path": "harmonia/memory/coordinate_system_catalog.md",
            "output_format": "Section-style markdown entry matching existing catalog format. Append to Section 4 (Stratifications). Do NOT commit — post via TENSOR_DIFF for sessionA review.",
        },
        "required_qualification": "basic",
    },
    {
        "task_id": "catalog_mf_weight",
        "task_type": "catalog_entry",
        "priority": 1.0,
        "payload": {
            "coordinate_system": "MF weight stratification",
            "brief": "Document splitting by mf_newforms.weight. What features resolve? What are the small-n strata issues? Canonical use cases from prior work.",
            "output_path": "harmonia/memory/coordinate_system_catalog.md",
            "output_format": "Catalog entry, post as TENSOR_DIFF for review.",
        },
        "required_qualification": "basic",
    },
    {
        "task_id": "catalog_artin_dim",
        "task_type": "catalog_entry",
        "priority": 2.0,
        "payload": {
            "coordinate_system": "Artin representation dimension stratification",
            "brief": "Document splitting by artin_reps.Dim. Connect to H61 (killed: dim-2-even/dim-3 ratio 1.8:1 not 50:1) and H63 (killed: no spike at dim 4).",
            "output_path": "harmonia/memory/coordinate_system_catalog.md",
            "output_format": "Catalog entry, post as TENSOR_DIFF for review.",
        },
        "required_qualification": "basic",
    },

    # ---- Review passes ----
    {
        "task_id": "review_catalog",
        "task_type": "review_pass",
        "priority": 3.0,
        "payload": {
            "target_file": "harmonia/memory/coordinate_system_catalog.md",
            "review_criteria": [
                "Are any coordinate systems missing? Compare against harmonia/src/coupling.py and cartography/shared/scripts/falsification_battery.py.",
                "Are any characterizations wrong (what resolves / what collapses)?",
                "Are tautology pairs complete? Check for known identities not yet listed.",
                "Does each entry cite a calibration anchor or known failure mode? Fill gaps.",
                "Language discipline: any 'cross-domain' or 'bridge' language that slipped in?",
            ],
            "output_path": "cartography/docs/review_catalog_<worker_name>.md",
            "output_format": "Markdown review notes. One section per issue found. Propose fixes; don't modify the catalog directly.",
        },
        "required_qualification": "basic",
    },

    # ---- Ingestion / data tasks ----
    {
        "task_id": "ingest_codata",
        "task_type": "ingest_snippet",
        "priority": 5.0,
        "payload": {
            "source": "cartography/physics/data/codata constants JSON if it exists, else NIST CODATA reference",
            "target_table": "prometheus_sci.physics.codata",
            "schema_ref": "thesauros/postgres_sci.md",
            "method": "Load ~300 CODATA physical constants into the empty physics.codata table. Coordinate with Mnemosyne before writing — she owns the schema.",
            "output_path": "cartography/docs/ingest_codata_log.json",
        },
        "required_qualification": "basic",
        "blocked_on": "Mnemosyne schema approval",
    },
]


def main():
    print("Seeding work queue...")
    for task in INITIAL_TASKS:
        tid = push_task(
            task_id=task["task_id"],
            task_type=task["task_type"],
            payload=task["payload"],
            priority=task["priority"],
            required_qualification=task["required_qualification"],
            expected_output=task.get("expected_output"),
            posted_by="Harmonia_M2_sessionA",
        )
        blocked = task.get("blocked_on", "")
        block_note = f" [BLOCKED: {blocked}]" if blocked else ""
        print(f"  pushed {tid} ({task['task_type']}){block_note}")

    from agora.work_queue import queue_status
    print("\nQueue status:")
    status = queue_status()
    for k, v in status.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
