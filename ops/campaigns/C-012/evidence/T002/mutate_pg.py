"""C-012-T002 mutation table: plant one bug per copy of moonshot/ and run the tests meant to catch it.

Each mutant is a copy of the repo's moonshot/ package with ONE textual change to moonshot/nf/schema.sql or
moonshot/nf/pg.py; its target tests run against the canonical cluster in throwaway schemas (unique per test), so
mutants run in parallel. evidence_wiki/ and comms/ (the credential resolver and identity guard) are NOT copied:
they resolve from this repo through PYTHONPATH.

    EW_DB_HOST=192.168.1.202 python ops/campaigns/C-012/evidence/T002/mutate_pg.py [--out results.json] [--only PM02,PM07]

A mutant is KILLED when its target tests fail, SURVIVED when they pass; PATCH_ERROR means the planted text no longer
matches the source exactly once (the table must be updated with the code)."""
import argparse
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
T = "moonshot.nf.tests.test_pg_publication."
S, P = "nf/schema.sql", "nf/pg.py"
VALIDATOR_SIG = "record_validation(text, integer, text, text, text[], text, text, text)"

M = [
    ("PM01", "publish guard ignores the chain generation", S,
     "AND c.generation = p_expected_generation AND c.head_index", "AND c.head_index",
     [T + "TestGuardedPublication.test_stale_worker_cannot_advance"]),
    ("PM02", "publish guard ignores the claimed parent digest", S,
     "AND c.head_epoch_digest IS NOT DISTINCT FROM p_expected_parent AND", "AND",
     [T + "TestGuardedPublication", T + "TestValidationAndContests"]),
    ("PM03", "no idempotency per attempt", S,
     "    SELECT * INTO a FROM attempts WHERE attempts.attempt_id = p_attempt_id;\n    IF FOUND THEN\n"
     "        RETURN QUERY SELECT a.outcome, a.publication_id, a.contest_id, c.generation, TRUE;",
     "    SELECT * INTO a FROM attempts WHERE attempts.attempt_id = p_attempt_id;\n    IF FALSE THEN\n"
     "        RETURN QUERY SELECT a.outcome, a.publication_id, a.contest_id, c.generation, TRUE;",
     [T + "TestGuardedPublication.test_same_attempt_twice_returns_the_recorded_outcome",
      T + "TestCrashAndRollback"]),
    ("PM04", "no chain row lock in publish", S,
     "SELECT * INTO c FROM chains WHERE chains.chain_id = p_chain_id FOR UPDATE;\n    IF NOT FOUND THEN\n"
     "        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;\n    END IF;\n    -- An attempt",
     "SELECT * INTO c FROM chains WHERE chains.chain_id = p_chain_id;\n    IF NOT FOUND THEN\n"
     "        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;\n    END IF;\n    -- An attempt",
     [T + "TestConcurrency"]),
    ("PM05", "a disagreement does not halt the chain", S,
     "                UPDATE chains SET state = 'HALTED', updated_at = now() WHERE chains.chain_id = p_chain_id;\n"
     "                v_out := 'DISAGREEMENT';",
     "                v_out := 'DISAGREEMENT';",
     [T + "TestGuardedPublication.test_conflicting_result_is_preserved_and_fails_closed"]),
    ("PM06", "objects are not content-addressed", S,
     "    CONSTRAINT objects_address CHECK (sha256 = encode(sha256(content), 'hex')),\n", "",
     [T + "TestSchemaAndIdentity.test_objects_are_content_addressed_by_the_database"]),
    ("PM07", "results are not append-only", S,
     "CREATE OR REPLACE TRIGGER results_append_only BEFORE UPDATE OR DELETE ON {schema}.results\n"
     "    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();\n", "",
     [T + "TestSchemaAndIdentity.test_immutable_tables_refuse_rewrites_even_by_superuser"]),
    ("PM08", "an overturn of epoch 1 does not raise the generation", S,
     "head_checkpoint_sha256 = new_ckpt,\n                              generation = c.generation + 1, state = 'OPEN', "
     "updated_at = now()\n            WHERE chains.chain_id = k.chain_id;\n        ELSE",
     "head_checkpoint_sha256 = new_ckpt,\n                              state = 'OPEN', "
     "updated_at = now()\n            WHERE chains.chain_id = k.chain_id;\n        ELSE",
     [T + "TestValidationAndContests.test_resolution_overturned_rewinds_and_stale_follows"]),
    ("PM09", "every resolution upholds", S,
     "        IF p_published_bytes_ok AND d = k.published_epoch_digest THEN", "        IF TRUE THEN",
     [T + "TestValidationAndContests"]),
    ("PM10", "a validation mismatch does not halt", S,
     "        ON CONFLICT DO NOTHING;                -- an already open contest keeps the chain halted\n"
     "        UPDATE chains SET state = 'HALTED', updated_at = now() WHERE chains.chain_id = p_chain_id;",
     "        ON CONFLICT DO NOTHING;                -- an already open contest keeps the chain halted",
     [T + "TestValidationAndContests.test_validation_mismatch_with_descendants_taints_and_halts"]),
    ("PM11", "the publisher is also granted record_validation", P,
     '    "publisher": ["publish(', '    "publisher": ["' + VALIDATOR_SIG + '", "publish(',
     [T + "TestValidationAndContests.test_publication_starts_unvalidated_and_only_a_validator_validates"]),
    ("PM12", "the publisher skips its semantic checks", P,
     "        if verify:\n            errs = self.verify(chain_id, epoch_index, files)",
     "        if False:\n            errs = self.verify(chain_id, epoch_index, files)",
     [T + "TestGuardedPublication"]),
    ("PM13", "publish does not retry when the connection dies", P,
     "            except (psycopg2.OperationalError, psycopg2.InterfaceError):\n"
     "                # the connection died: the transaction may or may not have committed",
     "            except ZeroDivisionError:\n"
     "                # the connection died: the transaction may or may not have committed",
     [T + "TestCrashAndRollback"]),
    ("PM14", "PUBLIC keeps EXECUTE on the functions", P,
     '"ALL FUNCTIONS IN SCHEMA {s}"):', '"ALL TABLES IN SCHEMA {s}"):',
     [T + "TestAuthority.test_public_has_nothing"]),
    ("PM15", "publish guard ignores the input checkpoint", S,
     "AND c.head_epoch_digest IS NOT DISTINCT FROM p_expected_parent AND c.head_checkpoint_sha256 = v_input THEN",
     "AND c.head_epoch_digest IS NOT DISTINCT FROM p_expected_parent THEN",
     [T + "TestGuardedPublication"]),
    ("PM16", "the database skips the trace_bytes claim", S,
     "IF (m->>'trace_bytes')::bigint IS DISTINCT FROM octet_length(p_trace) THEN errs := errs || 'trace_bytes'::text; "
     "END IF;", "",
     [T + "TestGuardedPublication.test_the_database_checks_every_manifest_claim"]),
    ("PM17", "an overturn at k>1 keeps the rejected head's checkpoint", S,
     "head_checkpoint_sha256 = new_ckpt, generation = c.generation + 1, state = 'OPEN',",
     "head_checkpoint_sha256 = c.head_checkpoint_sha256, generation = c.generation + 1, state = 'OPEN',",
     [T + "TestValidationAndContests.test_overturn_at_a_later_epoch_rewinds_to_its_parent"]),
    ("PM18", "a pending adverse validation is dropped at resolution", S,
     "    IF verdict IN ('UPHELD', 'OVERTURNED') THEN\n        -- Fail closed",
     "    IF FALSE THEN\n        -- Fail closed",
     [T + "TestValidationAndContests.test_an_adverse_validation_during_an_open_contest_is_not_dropped"]),
    ("PM19", "a stale validation is attributed to the live epoch", S,
     "    IF live.epoch_digest IS DISTINCT FROM p_epoch_digest THEN\n        RAISE EXCEPTION 'moonshot: stale validation",
     "    IF FALSE THEN\n        RAISE EXCEPTION 'moonshot: stale validation",
     [T + "TestValidationAndContests.test_a_validation_names_the_bytes_it_validated"]),
    ("PM20", "contests are unguarded", S,
     "CREATE OR REPLACE TRIGGER contests_guarded BEFORE UPDATE OR DELETE ON {schema}.contests\n"
     "    FOR EACH ROW EXECUTE FUNCTION {schema}.contest_guard();\n", "",
     [T + "TestValidationAndContests.test_contest_grounds_are_immutable_and_a_resolution_is_final"]),
    ("PM21", "a chain's generation may decrease", S,
     "    IF NEW.generation < OLD.generation THEN", "    IF FALSE THEN",
     [T + "TestSchemaAndIdentity.test_chain_identity_is_immutable_and_its_generation_only_grows"]),
    ("PM22", "a dead connection is never replaced", P,
     "        if self.conn.closed:\n            self.conn = connect()",
     "        if False:\n            self.conn = connect()",
     [T + "TestCrashAndRollback"]),
    ("PM23", "attempts may be truncated", S,
     "CREATE OR REPLACE TRIGGER attempts_no_truncate BEFORE TRUNCATE ON {schema}.attempts\n"
     "    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();\n", "",
     [T + "TestSchemaAndIdentity.test_immutable_tables_refuse_rewrites_even_by_superuser"]),
    ("PM24", "an INVALID validation opens no contest", S,
     "    IF p_state IN ('MISMATCH', 'INVALID') THEN\n        INSERT INTO contests",
     "    IF p_state IN ('MISMATCH') THEN\n        INSERT INTO contests",
     [T + "TestValidationAndContests.test_bytes_that_fail_validation_open_a_contest_and_can_be_overturned"]),
    ("PM25", "a resolved contest can be reopened", S,
     "    IF OLD.state IN ('RESOLVED_UPHELD', 'RESOLVED_OVERTURNED') THEN", "    IF FALSE THEN",
     [T + "TestValidationAndContests.test_contest_grounds_are_immutable_and_a_resolution_is_final"]),
    ("PM26", "VALIDATED is accepted with a disagreeing replay", S,
     "    IF p_state = 'VALIDATED' AND p_replay_digest IS DISTINCT FROM p_epoch_digest AND p_replay_digest IS NOT NULL THEN",
     "    IF FALSE THEN",
     [T + "TestValidationAndContests.test_a_validation_names_the_bytes_it_validated"]),
    ("PM27", "no one-live-publication index", S,
     "CREATE UNIQUE INDEX IF NOT EXISTS publications_one_live ON {schema}.publications (chain_id, epoch_index)\n"
     "    WHERE rejected_at IS NULL;\n", "",
     [T + "TestSchemaAndIdentity.test_the_database_admits_one_live_publication_per_position"]),
    ("PM28", "no one-open-contest index", S,
     "CREATE UNIQUE INDEX IF NOT EXISTS contests_one_open ON {schema}.contests (chain_id)\n"
     "    WHERE state IN ('CONTESTED', 'TAINTED', 'UNRESOLVED');\n", "",
     [T + "TestValidationAndContests"]),
    ("PM29", "a head move need not raise the generation", S,
     "       AND NEW.generation <= OLD.generation THEN", "       AND FALSE THEN",
     [T + "TestSchemaAndIdentity.test_chain_identity_is_immutable_and_its_generation_only_grows"]),
]


def run(m, out_dir):
    mid, what, rel, old, new, targets = m
    d = os.path.join(out_dir, mid)
    shutil.copytree(REPO / "moonshot", os.path.join(d, "moonshot"), ignore=shutil.ignore_patterns("__pycache__"))
    p = os.path.join(d, "moonshot", rel)
    with open(p, encoding="utf-8") as f:
        text = f.read()
    n = text.count(old)
    if n != 1:
        return {"id": mid, "what": what, "verdict": "PATCH_ERROR", "matches": n}
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace(old, new))
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(x for x in (str(REPO), os.environ.get("PYTHONPATH")) if x))
    t = time.time()
    r = subprocess.run([sys.executable, "-m", "unittest"] + targets, cwd=d, capture_output=True, timeout=1500, env=env)
    lines = [ln for ln in r.stderr.decode(errors="replace").splitlines() if ln.strip()]
    # a target that does not load is an instrument error, never a kill
    broken = any("unittest.loader._FailedTest" in ln or "Failed to import test module" in ln for ln in lines)
    verdict = "TARGET_ERROR" if broken else ("KILLED" if r.returncode != 0 else "SURVIVED")
    return {"id": mid, "what": what, "file": rel, "targets": targets,
            "verdict": verdict, "seconds": round(time.time() - t, 1),
            "tail": lines[-1:], "first_failure": next((ln for ln in lines if ln.startswith(("FAIL:", "ERROR:"))), None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--only")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if not os.environ.get("EW_DB_HOST"):
        sys.exit("EW_DB_HOST is not set: every target test would be skipped and every mutant would 'survive'")
    chosen = [m for m in M if not a.only or m[0] in a.only.split(",")]
    out_dir = tempfile.mkdtemp(prefix="mut-nf-")
    t = time.time()
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = sorted(ex.map(lambda m: run(m, out_dir), chosen), key=lambda x: x["id"])
    shutil.rmtree(out_dir, ignore_errors=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "moonshot"], cwd=REPO, capture_output=True,
                           text=True).stdout.strip()
    doc = {"schema": "moonshot.nf.mutation_table.v1", "head": head, "moonshot_dirty": bool(dirty),
           "seconds": round(time.time() - t, 1), "results": results,
           "killed": sum(x["verdict"] == "KILLED" for x in results), "total": len(results)}
    for x in results:
        print("{} {:11} {}  ({}s) {}".format(x["id"], x["verdict"], x["what"], x.get("seconds"),
                                             x.get("first_failure") or (x.get("tail") or [""])[0]))
    print("killed {}/{} (head {}{})".format(doc["killed"], doc["total"], head[:9], ", moonshot/ dirty" if dirty else ""))
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
