"""Stdlib fixtures, all under tempfile outside the workspace.

Run with python -B test_validate_package.py -v. Add --harmonia-defect to
execute ONLY selected AST functions from the inspected Harmonia source.
Those optional tests deliberately confirm defects, not correct statistics.
"""

import ast
from collections import namedtuple
from contextlib import redirect_stdout
import io
import itertools
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import validate_package as validator


HARMONIA_ENABLED = "--harmonia-defect" in sys.argv
if HARMONIA_ENABLED:
    sys.argv.remove("--harmonia-defect")


def fixture_documents():
    groups = "SCI ORG DEV WLD SRH MSR CAU TRF PRV REP APR CMP INF ENE ATT OUT".split()
    docs = {name: "# Fixture\n" for name in validator.DOCUMENTS}
    docs["REQUIREMENTS.md"] = "\n".join(
        f"## {i}. Group\n" + "\n".join(
            f"### R-{group}-{j:02} | REQUIRED | Fixture" for j in range(1, 4))
        for i, group in enumerate(groups, 1)
    ) + "\n"
    docs["RSE_ARCHITECTURE.md"] = "# Architecture\n" + "body\n" * 200
    docs["ENGINE_PORTFOLIO.md"] = "\n".join(
        f"### Q{i}. Fixture\n| Required field | Specification |\n|---|---|\n"
        + "\n".join(f"| {field} | Spec |" for field in validator.CARD_FIELDS)
        for i in range(1, 7)
    ) + "\n"
    docs["FAILURE_TO_GATE_MAP.md"] = "\n".join(
        f"### T{i:02} / FG{i:02}: fixture" for i in range(1, 25)) + "\n"
    docs["SALVAGE_MATRIX.md"] = "\n".join(
        f"| C{i:02} / S / fixture | C | R-SCI-01 | isolated | REBUILD | 1 / 1 | Y/none/N |"
        for i in range(1, 57)
    ) + "\n" + "\n".join(
        f"| {decision} | {56 if decision == 'REBUILD' else 0} | 0 | {56 if decision == 'REBUILD' else 0} |"
        for decision in validator.DECISIONS
    ) + "\n| **Total** | **56** | **0** | **56** |\n"
    docs["PHASE3_META_ANALYSIS.md"] = "\n".join(
        f"## {i}. Section" for i in range(1, 26)
    ) + "\n" + "\n".join(f"### Q{i} - Answer" for i in range(1, 11)) + "\n"
    return docs


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        # Fail before creating anything if TEMP has been pointed inside a workspace.
        temp_base = Path(tempfile.gettempdir()).resolve()
        for workspace in (Path(__file__).absolute().parents[5], Path.cwd()):
            if temp_base == workspace or workspace in temp_base.parents:
                raise RuntimeError("Tests require a temporary directory outside the workspace")
        self.temp = tempfile.TemporaryDirectory(prefix="astra-package-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = fixture_documents()
        self.result = validator.Validation()
        self.frozen = {name: self.docs[name].encode("utf-8")
                       for name in ("REQUIREMENTS.md", "RSE_ARCHITECTURE.md")}
        for name, text in self.docs.items():
            self.write(validator.PACKAGE / name, text)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def codes(self):
        return [entry["code"] for entry in self.result.errors]

    def install_intake(self):
        for source in validator.INTAKE:
            self.write(source, "# Intake fixture\n")
        for seat, counts in validator.PERSPECTIVES.items():
            for kind, count in zip(("artifact", "engine"), counts):
                self.write(f"docs/phase3/intake/{seat}/{kind}_index.jsonl", '{}\n' * count)
        rulers = [{"ruler_id": f"TR-{i:03}", "same_instrument_as": []} for i in range(1, 153)]
        for index in range(6):
            rulers[index]["same_instrument_as"] = [f"TR-{index + 7:03}"]
        self.write("docs/phase3/intake/tityos/ruler_inventory.jsonl",
                   "\n".join(json.dumps(row) for row in rulers) + "\n")

    def test_positive_structure(self):
        validator.check_structure(self.docs, self.result)
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.metrics["engine_card_fields"], [27] * 6)
        self.assertEqual(self.result.metrics["salvage"]["decisions"]["REBUILD"]["total"], 56)

    def test_positive_complete_package(self):
        self.install_intake()
        with mock.patch.object(validator, "frozen_sources", return_value=self.frozen):
            result, manifest = validator.validate(self.root)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metrics["intake"]["parsed_totals"], {"artifact": 1802, "engine": 247})
        self.assertEqual(result.metrics["intake"]["ruler_records"], 152)
        self.assertEqual(result.metrics["intake"]["aliases"]["groups"], 146)
        self.assertEqual(len(manifest["sources"]), 16)
        self.assertTrue(all(len(source["sha256_lf"]) == 64 for source in manifest["sources"]))
        for name in ("process/VALIDATION.md", "process/REVIEW_PACKET_2026-10-01.md"):
            self.assertEqual(manifest["document_sha256_lf"][name],
                             validator.digest(self.docs[name].encode("utf-8")))
        self.assertEqual(result.summary()["scientific_qualification"], "NOT_VERIFIED")

    def test_missing_required_companion(self):
        self.install_intake()
        (self.root / validator.PACKAGE / "OPEN_QUESTIONS.md").unlink()
        with mock.patch.object(validator, "frozen_sources", return_value=self.frozen):
            result, _ = validator.validate(self.root)
        self.assertIn({"code": "MISSING_FILE", "source": "OPEN_QUESTIONS.md"}, result.errors)
        self.assertEqual(result.metrics["required_documents"]["readable"], 7)
        self.assertEqual(result.summary()["status"], "FAIL")

    def test_bad_requirement_reference(self):
        self.docs["FALSIFIERS.md"] += "R-NOT-99\n"
        validator.check_structure(self.docs, self.result)
        self.assertIn("UNKNOWN_REQUIREMENT", self.codes())

    def test_duplicate_requirement(self):
        self.docs["REQUIREMENTS.md"] = self.docs["REQUIREMENTS.md"].replace("R-SCI-02", "R-SCI-01")
        validator.check_structure(self.docs, self.result)
        self.assertIn("REQUIREMENT_CENSUS", self.codes())

    def test_engine_field_duplicate_cannot_replace_missing(self):
        self.docs["ENGINE_PORTFOLIO.md"] = self.docs["ENGINE_PORTFOLIO.md"].replace("| Claim ceiling |", "| Kill criteria |", 1)
        validator.check_structure(self.docs, self.result)
        self.assertIn("ENGINE_CARD_FIELDS", self.codes())

    def test_failure_class_missing(self):
        self.docs["FAILURE_TO_GATE_MAP.md"] = self.docs["FAILURE_TO_GATE_MAP.md"].replace("### T24", "### T23")
        validator.check_structure(self.docs, self.result)
        self.assertIn("FAILURE_CLASS_CENSUS", self.codes())

    def test_salvage_duplicate_and_wrong_decision_summary(self):
        self.docs["SALVAGE_MATRIX.md"] = self.docs["SALVAGE_MATRIX.md"].replace("C56 /", "C55 /").replace("| REBUILD | 56 |", "| REBUILD | 55 |")
        validator.check_structure(self.docs, self.result)
        self.assertIn("SALVAGE_ROW_CENSUS", self.codes())
        self.assertIn("SALVAGE_DECISION_ARITHMETIC", self.codes())

    def test_main_section_and_answer_missing(self):
        self.docs["PHASE3_META_ANALYSIS.md"] = self.docs["PHASE3_META_ANALYSIS.md"].replace("## 25.", "## Last").replace("### Q10", "### Last")
        validator.check_structure(self.docs, self.result)
        self.assertIn("MAIN_SECTION_CENSUS", self.codes())
        self.assertIn("MAIN_QUESTION_CENSUS", self.codes())

    def test_positive_inline_reference_collapsed_and_shortcut_links(self):
        text = ('[inline](REQUIREMENTS.md#L1-L3) [ref][A] [A][] [A]\n'
                '[A]: <RSE_ARCHITECTURE.md#L200-L201> "title"\n')
        validator.check_links(self.root, {"FALSIFIERS.md": text}, self.result)
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.metrics["links"]["line_ranges_checked"], 2)

    def test_missing_inline_and_reference_target(self):
        text = "[missing](missing.md) [ref][A]\n[A]: missing-too.md\n"
        validator.check_links(self.root, {"FALSIFIERS.md": text}, self.result)
        self.assertEqual(self.codes().count("MISSING_LINK_TARGET"), 2)

    def test_undefined_reference(self):
        validator.check_links(self.root, {"FALSIFIERS.md": "[missing][UNDEFINED]"}, self.result)
        self.assertIn("UNDEFINED_LINK_REFERENCE", self.codes())

    def test_malformed_and_out_of_bounds_ranges(self):
        for fragment, code in (("L3-Lx", "MALFORMED_LINE_RANGE"),
                               ("Lx-L3", "MALFORMED_LINE_RANGE"),
                               ("L3-L2", "MALFORMED_LINE_RANGE"),
                               ("L0", "MALFORMED_LINE_RANGE"),
                               ("L999", "LINE_RANGE_OUT_OF_BOUNDS")):
            with self.subTest(fragment=fragment):
                result = validator.Validation()
                validator.check_links(self.root, {"FALSIFIERS.md": f"[x](REQUIREMENTS.md#{fragment})"}, result)
                self.assertEqual(result.errors[0]["code"], code)

    def test_external_links_and_code_not_opened(self):
        text = "[web](https://example.org/a_(b))\n`[code](missing.md)`\n```\n[x](absent.md)\n```\n"
        with mock.patch.object(Path, "open", side_effect=AssertionError("No content reads")):
            validator.check_links(self.root, {"FALSIFIERS.md": text}, self.result)
        self.assertEqual(self.result.errors, [])
        self.assertEqual(self.result.metrics["links"]["external_not_fetched"], 1)

    def test_prohibited_targets_blocked_before_stat(self):
        paths = ("docs/phase3/design/OTHER/file.md", "roles/Dionysus/file.md",
                 "roles/Epimetheus/file.md", ".env", "keys/private.pem")
        with mock.patch.object(Path, "lstat", side_effect=AssertionError("No traversal")):
            for relative in paths:
                self.assertIsNotNone(validator.guarded_path(self.root, self.root / relative))

    def test_percent_encoded_prohibited_link_blocked(self):
        text = "[no](../../../../roles/%44ionysus/file.md#L1)"
        with mock.patch.object(Path, "open", side_effect=AssertionError("No read")):
            validator.check_links(self.root, {"FALSIFIERS.md": text}, self.result)
        self.assertIn("EXCLUDED_ROLE", self.codes())

    def test_outside_repository_link_blocked(self):
        validator.check_links(self.root, {"FALSIFIERS.md": "[x](../../../../../outside.md)"}, self.result)
        self.assertIn("OUTSIDE_REPOSITORY", self.codes())

    def test_reparse_point_rejected(self):
        info = mock.Mock(st_mode=0, st_file_attributes=0x400)
        with mock.patch.object(Path, "lstat", return_value=info):
            self.assertEqual(validator.guarded_path(self.root, self.root / "alias/file.md"), "EXCLUDED_REPARSE_POINT")

    def test_windows_path_aliases_rejected_before_stat(self):
        with mock.patch.object(Path, "lstat", side_effect=AssertionError("No traversal")):
            for path in ("roles/Dionysus./file.md", "roles/DIONYS~1/file.md", "file.txt:stream"):
                with self.subTest(path=path):
                    self.assertEqual(validator.guarded_path(self.root, self.root / path), "UNSAFE_PATH_ALIAS")

    def test_alias_check_precedes_os_normalization(self):
        with mock.patch.object(validator.os.path, "abspath", side_effect=AssertionError("No normalization")):
            self.assertEqual(validator.guarded_path(self.root, self.root / "roles/Dionysus./file.md"),
                             "UNSAFE_PATH_ALIAS")

    def test_jsonl_blank_lines_are_not_records(self):
        records = validator.parse_jsonl(b'{"row":1}\n\n{"row":2}\n', self.result, "fixture.jsonl")
        self.assertEqual(len(records), 2)
        self.assertEqual(self.result.errors, [])

    def test_invalid_jsonl_and_no_record_content_in_errors(self):
        marker = "fixture-private-text"
        raw = ('{"x":1}\n' + marker + '\n[]\n{"x":NaN}\n{"x":1,"x":2}\n').encode()
        records = validator.parse_jsonl(raw, self.result, "fixture.jsonl")
        self.assertEqual(len(records), 1)
        self.assertEqual(self.codes().count("INVALID_JSONL_RECORD"), 4)
        self.assertNotIn(marker, json.dumps(self.result.summary()))

    def test_alias_chains_and_missing_target(self):
        rows = [{"ruler_id": "TR-001", "same_instrument_as": ["TR-002"]},
                {"ruler_id": "TR-002", "same_instrument_as": ["TR-003"]},
                {"ruler_id": "TR-003", "same_instrument_as": ["TR-001"]}]
        self.assertEqual(validator.ruler_aliases(rows, self.result)["groups"], 1)
        rows[0]["same_instrument_as"].append("TR-999")
        validator.ruler_aliases(rows, self.result)
        self.assertIn("INVALID_ALIAS_TARGET", self.codes())

    def test_freeze_canonical_lf_and_appendix_allowed(self):
        self.docs["REQUIREMENTS.md"] = self.docs["REQUIREMENTS.md"].replace("\n", "\r\n")
        self.docs["RSE_ARCHITECTURE.md"] += "\n## Appendix\nExplicit delta.\n"
        validator.check_freeze(self.docs, self.frozen, self.result)
        self.assertEqual(self.result.errors, [])
        self.assertEqual(validator.digest(b"a\r\nb\r"), validator.digest(b"a\nb\n"))

    def test_freeze_changed_requirements(self):
        self.docs["REQUIREMENTS.md"] += "Changed\n"
        validator.check_freeze(self.docs, self.frozen, self.result)
        self.assertIn("REQUIREMENTS_FREEZE_CHANGED", self.codes())

    def test_freeze_changed_architecture_original(self):
        self.docs["RSE_ARCHITECTURE.md"] = self.docs["RSE_ARCHITECTURE.md"].replace("body", "changed", 1)
        validator.check_freeze(self.docs, self.frozen, self.result)
        self.assertIn("ARCHITECTURE_FREEZE_CHANGED", self.codes())

    def test_git_failure_is_not_pass(self):
        self.install_intake()
        with mock.patch.object(validator, "frozen_sources", side_effect=OSError):
            result, _ = validator.validate(self.root)
        self.assertIn("FREEZE_GIT_UNAVAILABLE", [entry["code"] for entry in result.errors])

    def test_git_reads_only_two_commits_and_two_frozen_files(self):
        outputs = [validator.FREEZE.encode() + b"\n", validator.BASE.encode() + b"\n",
                   self.frozen["REQUIREMENTS.md"], self.frozen["RSE_ARCHITECTURE.md"]]
        with mock.patch.object(validator, "git_output", side_effect=outputs) as reader:
            self.assertEqual(validator.frozen_sources(self.root), self.frozen)
        self.assertEqual(reader.call_count, 4)
        self.assertEqual(reader.call_args_list[0].args[1], ["rev-parse", "--verify", validator.FREEZE + "^{commit}"])
        for call, name in zip(reader.call_args_list[2:], self.frozen):
            self.assertEqual(call.args[1], ["show", "--no-ext-diff", "--no-textconv",
                                           f"{validator.FREEZE}:{validator.PACKAGE.as_posix()}/{name}"])

    def test_secret_detection_reports_no_values(self):
        marker = "gh" + "p_" + "A" * 24
        path = self.write(validator.PACKAGE / "FALSIFIERS.md", marker)
        raw = validator.read_allowed(self.root, path, self.result, "FALSIFIERS.md")
        self.assertIsNone(raw)
        self.assertIn("SECRET_PATTERN_DETECTED", self.codes())
        self.assertNotIn(marker, json.dumps(self.result.summary()))

    def test_manifest_cli_write_verify_and_drift_exit_codes(self):
        self.install_intake()
        with mock.patch.object(validator, "frozen_sources", return_value=self.frozen):
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(validator.main(["--root", str(self.root), "--write-manifest"]), 0)
            self.assertEqual(json.loads(output.getvalue())["status"], "PASS")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(validator.main(["--root", str(self.root)]), 0)
            self.write(validator.PACKAGE / "ASSUMPTIONS.md", "# Changed fixture\n")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(validator.main(["--root", str(self.root)]), 1)
            self.assertIn("MANIFEST_MISMATCH", [entry["code"] for entry in json.loads(output.getvalue())["errors"]])


@unittest.skipUnless(HARMONIA_ENABLED, "Opt in with --harmonia-defect; expected defects, not qualification")
class HarmoniaExpectedDefectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).absolute().parents[5]
        source = root / "roles/Harmonia/qualification/h0h5/qualification_rules.py"
        if validator.guarded_path(root, source):
            raise RuntimeError("Harmonia source blocked")
        # Inspected source ends paired_contrast at line 284. Never import the
        # package, other modules, campaign entrypoints or its remaining code.
        with source.open(encoding="utf-8") as handle:
            tree = ast.parse("".join(itertools.islice(handle, 284)))
        names = {"_mean", "_sd", "min_attainable_p_paired", "t_crit", "paired_contrast"}
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        if {node.name for node in functions} != names:
            raise RuntimeError("Inspected Harmonia function layout changed")
        table = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "_T" for target in node.targets))
        estimate = namedtuple("Estimate", "name point lo hi se n_blocks alpha_used min_attainable_p")
        namespace = {"math": math, "_T": ast.literal_eval(table), "Estimate": estimate,
                     "__builtins__": {"sum": sum, "len": len, "max": max, "float": float,
                                      "int": int, "abs": abs, "sorted": sorted}}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "harmonia-selected-functions", "exec"), namespace)
        cls.functions = namespace

    def test_expected_defect_three_primary_alpha_changes_but_interval_does_not(self):
        values = [i / 100 for i in range(12)]
        two = self.functions["paired_contrast"]("fixture", values, n_primary=2)
        three = self.functions["paired_contrast"]("fixture", values, n_primary=3)
        self.assertGreater(two.se, 0)
        self.assertEqual((two.lo, two.hi), (three.lo, three.hi))
        self.assertEqual(two.alpha_used, 0.025)
        self.assertEqual(three.alpha_used, 0.05 / 3)
        self.assertNotEqual(two.alpha_used, three.alpha_used)

    def test_expected_defect_df11_uses_df12_lookup(self):
        self.assertEqual(self.functions["t_crit"](11, 0.05), 2.179)
        self.assertEqual(self.functions["t_crit"](11, 0.05), self.functions["t_crit"](12, 0.05))


if __name__ == "__main__":
    unittest.main()