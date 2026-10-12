"""C-012-T005 mutation table for the materializer (moonshot/nf/materialize.py) and the catalogue view. Same mechanics
as ../T002/mutate_pg.py. Run it with Moonshot's lake venv so the target tests execute (they skip without pyarrow):

    EW_DB_HOST=192.168.1.202 C:/Prometheus-data/moonshot/venv/Scripts/python.exe \
        ops/campaigns/C-012/evidence/LAKE/mutate_t005.py [--out results.json]
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("mutate_pg", Path(__file__).resolve().parents[1] / "T002" / "mutate_pg.py")
MP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MP)

T = "moonshot.nf.tests.test_materialize."
MZ, S = "nf/materialize.py", "nf/schema.sql"

MP.M[:] = [
    ("MM01", "the watermark is ignored (every eligible row appended each run)", MZ,
     "            new = [x for x in eligible if wm is None or x[key] > wm]",
     "            new = list(eligible)",
     [T + "TestMaterialize.test_a_second_run_appends_nothing"]),
    ("MM02", "off by one at the watermark", MZ,
     "            new = [x for x in eligible if wm is None or x[key] > wm]",
     "            new = [x for x in eligible if wm is None or x[key] >= wm]",
     [T + "TestMaterialize.test_a_second_run_appends_nothing"]),
    ("MM03", "the watermark is not written into the snapshot", MZ,
     "                       snapshot_properties={\"watermark\": str(watermark), \"writer\": \"moonshot.nf.materialize\"})",
     "                       snapshot_properties={\"writer\": \"moonshot.nf.materialize\"})",
     [T + "TestMaterialize"]),
    ("MM04", "the oracle never reports a missed row", MZ,
     "        missing = sorted(set(pg_keys) - set(lake_keys))", "        missing = []",
     [T + "TestMaterialize.test_the_oracle_catches_a_missed_row_and_repair_restores_exactly_it"]),
    ("MM05", "the oracle never reports duplicates", MZ,
     "        dupes = len(lake_keys) - len(set(lake_keys))", "        dupes = 0",
     [T + "TestMaterialize"]),
    ("MM06", "repair ignores what the lake already holds", MZ,
     "            new = [x for x in eligible if _row_key(table, x) not in have]", "            new = list(eligible)",
     [T + "TestMaterialize.test_the_oracle_catches_a_missed_row_and_repair_restores_exactly_it"]),
    ("MM07", "no single-writer lock", MZ,
     "        if not got:\n            raise Busy(", "        if False:\n            raise Busy(",
     [T + "TestMaterialize.test_one_materializer_at_a_time"]),
    ("MM08", "the settle window is ignored", MZ,
     "            if r[-1]:\n                eligible.extend(mapped)", "            if True:\n                eligible.extend(mapped)",
     [T + "TestMaterialize.test_the_settle_window_defers_fresh_rows"]),
    ("MM09", "the final trace line is lost", MZ,
     "        if lines and lines[-1] == b\"\":\n            lines = lines[:-1]",
     "        lines = lines[:-2]",
     [T + "TestMaterialize.test_first_run_fills_every_table_and_the_oracle_holds"]),
    ("MM10", "trace lines numbered from 0", MZ,
     "for i, ln in enumerate(lines, 1)]", "for i, ln in enumerate(lines)]",
     [T + "TestMaterialize.test_rows_carry_pans_provenance_columns"]),
    ("MM11", "the run is not logged in Moonshot's records", MZ,
     "        report[\"logged_event_id\"] = coord.record_materialization(report)",
     "        report[\"logged_event_id\"] = None",
     [T + "TestMaterialize.test_each_run_is_logged_in_moonshots_own_records"]),
    ("MM12", "the catalogue lists rejected epochs too", S,
     "JOIN {schema}.chains c ON c.chain_id = p.chain_id\nWHERE p.rejected_at IS NULL;",
     "JOIN {schema}.chains c ON c.chain_id = p.chain_id;",
     [T + "TestCatalogueView"]),
    ("MM13", "the epochs record is not the canonical manifest", MZ,
     "kind=\"epoch\", record=bytes(content).decode(\"ascii\")", "kind=\"epoch\", record=None",
     [T + "TestMaterialize.test_first_run_fills_every_table_and_the_oracle_holds"]),
    ("MM14", "attempts miss a classification kind", MZ,
     "CLASSIFICATIONS = (\"published\", \"duplicate\", \"disagreement\", \"stale\", \"invalid\", \"refused_unapproved\", \"halted\")",
     "CLASSIFICATIONS = (\"published\", \"duplicate\", \"stale\", \"invalid\", \"refused_unapproved\", \"halted\")",
     [T + "TestMaterialize.test_first_run_fills_every_table_and_the_oracle_holds"]),
]

if __name__ == "__main__":
    MP.main()
