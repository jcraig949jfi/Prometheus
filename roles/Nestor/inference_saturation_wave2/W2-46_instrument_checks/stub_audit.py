"""W2-46 stub audit: replace each check, in the test module's namespace, by a constant-verdict stub (OK, its defect
verdict, NOT_VERIFIED) and count failing tests. Every (check, stub) pair must break >= 1 test.

    python -B stub_audit.py
"""
import inspect
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ichecks import CheckResult  # noqa: E402
import ichecks.tests.test_ichecks as T  # noqa: E402

CHECKS = {"check_screen_context": "CONTEXT_MISMATCH", "check_label_readout_write_back": "LABEL_READOUT_IN_BASE",
          "check_label_absorbing": "ABSORBED_LABEL", "scan_max_of_cached": "MAX_OF_CACHED",
          "check_max_amplification": "MAX_AMPLIFIED", "check_block_exchangeability": "NON_EXCHANGEABLE",
          "check_certificate_seeds": "SEED_UNSTABLE", "check_readout_pairing": "UNLIKE_READOUTS",
          "check_record_key_pairing": "UNLIKE_READOUTS", "check_ruler_agreement": "RULER_MISMATCH",
          "check_stores_genomes": "NO_GENOMES"}
tests = [(n, f) for n, f in vars(T).items() if n.startswith("test_") and callable(f)]


def run_all():
    fails = 0
    for n, f in tests:
        try:
            if "tmp_path" in inspect.signature(f).parameters:
                with tempfile.TemporaryDirectory() as d:
                    f(pathlib.Path(d))
            else:
                f()
        except Exception:  # noqa: BLE001
            fails += 1
    return fails


base = run_all()
print("baseline failures:", base)
ok = True
for name, defect in CHECKS.items():
    real = getattr(T, name)
    for v in ("OK", defect, "NOT_VERIFIED"):
        setattr(T, name, lambda *a, _v=v, **k: CheckResult("stub", _v, "stub", {}, []))
        n = run_all() - base
        ok &= n > 0
        print("%-32s stub=%-22s broken tests=%d" % (name, v, n))
    setattr(T, name, real)
print("EVERY STUB CAUGHT:", ok)
