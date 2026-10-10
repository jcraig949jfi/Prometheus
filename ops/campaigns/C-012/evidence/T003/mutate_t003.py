"""C-012-T003 mutation table: one planted bug per copy of moonshot/, aimed at the coordinator and the approved
executor; same mechanics as ../T002/mutate_pg.py (copies only moonshot/, evidence_wiki/comms/fabric via PYTHONPATH).

    EW_DB_HOST=192.168.1.202 python ops/campaigns/C-012/evidence/T003/mutate_t003.py [--out results.json] [--only TM01]
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("mutate_pg", Path(__file__).resolve().parents[1] / "T002" / "mutate_pg.py")
MP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MP)

X = "moonshot.nf.tests.test_fabric_exec."
K = "moonshot.nf.tests.test_coordinator."
E, CO = "epoch/fabric_exec.py", "nf/coordinator.py"

MP.M[:] = [
    ("TM01", "production namespaces honour fault files", E,
     "    if not TEST_NAMESPACE.match(namespace):\n        return None", "    if False:\n        return None",
     [X + "TestNodeLocalFaults.test_production_namespaces_ignore_fault_files"]),
    ("TM02", "a fault applies to every epoch of its chain", E,
     "s.get(\"chain_id\") == chain_id and k in (s.get(\"epochs\") or [])", "s.get(\"chain_id\") == chain_id",
     [X + "TestNodeLocalFaults.test_a_fault_applies_only_to_its_chain_and_epochs"]),
    ("TM03", "the input hash is not checked", E,
     "    if hashlib.sha256(inp).hexdigest() != a.input_sha256:", "    if False:",
     [X + "TestExecutor.test_an_input_that_does_not_match_its_hash_is_refused"]),
    ("TM04", "no check for existing output before writing", E,
     "    if any(os.path.exists(p) for p, _ in targets):", "    if False:",
     [X + "TestExecutor.test_existing_output_is_never_overwritten"]),
    ("TM04b", "writes are not exclusive (expected EQUIVALENT: a backstop for a race the tests cannot schedule)", E,
     "            with open(p, \"xb\") as f:", "            with open(p, \"wb\") as f:",
     [X + "TestExecutor.test_existing_output_is_never_overwritten"]),
    ("TM05", "the publisher ignores the module", CO,
     "        if params.get(\"module\") != MODULE or params.get(\"script\"):", "        if False:",
     [K + "TestRefusals.test_another_module_is_refused_even_when_its_bytes_are_right"]),
    ("TM06", "the publisher ignores the task's base_sha", CO,
     "        if t.get(\"base_sha\") != chain[\"approved_code_sha\"]:", "        if False:",
     [K + "TestRefusals.test_unapproved_code_is_refused"]),
    ("TM07", "the publisher ignores the namespace", CO,
     "        if _arg(args, \"--namespace\") != chain[\"namespace\"] or m.get(\"namespace\") != chain[\"namespace\"]:",
     "        if m.get(\"namespace\") != chain[\"namespace\"]:",
     [K + "TestRefusals.test_a_test_namespace_task_cannot_publish_into_another_namespace"]),
    ("TM08", "refusals are recorded but publication goes ahead", CO,
     "                                 approved=not p[\"refused\"])", "                                 approved=True)",
     [K + "TestRefusals"]),
    ("TM09", "failed attempts are classified too", CO,
     "                if a[\"status\"] == \"succeeded\" and a[\"attempt_id\"] not in done:",
     "                if a[\"attempt_id\"] not in done:",
     [K + "TestHappyPath.test_a_failed_execution_is_left_to_fabric_and_retried"]),
    ("TM10", "validation never finds a mismatch", CO,
     "(\"VALIDATED\" if replay.epoch_digest == p[\"epoch_digest\"] else \"MISMATCH\")", "\"VALIDATED\"",
     [K + "TestStraggler"]),
    ("TM11", "dispatch ignores the generation (keys collide across a rewind)", CO,
     "key = \"moonshot/{}/{}/{}/{}/g{}\".format(self.schema, ns, chain_id, k, gen)",
     "key = \"moonshot/{}/{}/{}/{}\".format(self.schema, ns, chain_id, k)",
     [K + "TestStraggler"]),
    ("TM12", "the receipt is not stored", CO,
     "        sha = self._h(\"coordinator\").record_receipt(chain_id, C.canonical_bytes(body))",
     "        sha = C.sha256_hex(C.canonical_bytes(body))",
     [K + "TestHappyPath.test_the_receipt_is_durable_canonical_and_complete"]),
    ("TM13", "the dispatcher sends the wrong input checkpoint", CO,
     "        inp = self.reader.checkpoint_at(chain_id, h[\"head_index\"])",
     "        inp = self.reader.checkpoint_at(chain_id, 0)",
     [K + "TestHappyPath.test_one_chain_end_to_end_is_the_c008_identity"]),
    ("TM14", "accounting is dropped", CO,
     "            res = handle.publish(*args, p[\"files\"], detail={\"fabric\": acct, \"refused\": p[\"refused\"]},",
     "            res = handle.publish(*args, p[\"files\"], detail={\"refused\": p[\"refused\"]},",
     [K + "TestHappyPath.test_accounting_lives_outside_the_trace"]),
    ("TM15", "resolution trusts the published bytes", CO,
     "        bytes_ok = files is not None and model.verify_epoch(files, C.sha256_hex(inp)) == []",
     "        bytes_ok = True",
     [K[:-1]]),
]

if __name__ == "__main__":
    MP.main()
