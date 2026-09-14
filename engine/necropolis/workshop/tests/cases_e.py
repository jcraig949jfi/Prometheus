"""Necropolis workshop control cases, batch E (NECROPOLIS VALIDATION layer).

Wave-2 Keeper-authored controls, third batch: Charon C1/C2 pool checks,
divergence decomposition identities, prometheus_math instrument contract and
degenerate audit, Eos intake gate, comms identity guard (with a FAKE
connection: the guard's logic is exercised, no database is touched), and the
Apollo E9 scorer (fixture-bound; only checked for the exact published number).
Same verdict vocabulary as run_controls.  No case reads a grave.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def _import_from(subdir: str, module: str):
    p = str(REPO / subdir)
    if p not in sys.path:
        sys.path.insert(0, p)
    return importlib.import_module(module)


class _FakeCursor:
    def __init__(self, row, raise_exc=None):
        self.row, self.raise_exc = row, raise_exc

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql):
        if self.raise_exc:
            raise self.raise_exc

    def fetchone(self):
        return self.row


class _FakeConn:
    def __init__(self, row, raise_exc=None):
        self.row, self.raise_exc, self.rolled_back = row, raise_exc, 0

    def cursor(self):
        return _FakeCursor(self.row, self.raise_exc)

    def rollback(self):
        self.rolled_back += 1


def register(case):

    # ------------------------------------------------------------------ charon_c1c2 (charon/probe/c1c2_checks.py)
    def _c1c2():
        return importlib.import_module("charon.probe.c1c2_checks")

    def _pool(tmp, name, rows):
        p = Path(tmp) / name
        p.write_bytes(("\n".join(json.dumps(r) for r in rows) + "\n").encode())
        return p

    @case("charon_c1c2.ACCEPT.c1_matching_fingerprint_passes", "charon_c1c2", "ACCEPT")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            p = _pool(tmp, "pool.jsonl", [{"uid": i} for i in range(5)])
            fp = C.pool_fingerprint(p)
            v = C.check_c1_pool_fingerprint({"prepass_fingerprints": {"pool": fp}}, {"pool": p})
            return v.verdict == "PASS", {"verdict": v.verdict, "reasons": v.reasons[:3]}

    @case("charon_c1c2.PERTURBATION.c1_one_appended_row_fails", "charon_c1c2", "PERTURBATION")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            p = _pool(tmp, "pool.jsonl", [{"uid": i} for i in range(5)])
            fp = C.pool_fingerprint(p)
            with open(p, "ab") as fh:
                fh.write(b'{"uid": 99}\n')
            v = C.check_c1_pool_fingerprint({"prepass_fingerprints": {"pool": fp}}, {"pool": p})
            return v.verdict == "FAIL", {"verdict": v.verdict, "reasons": v.reasons[:3]}

    @case("charon_c1c2.CHEAT.c1_receipt_without_fingerprint_fails_not_indeterminate", "charon_c1c2", "CHEAT")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            p = _pool(tmp, "pool.jsonl", [{"uid": i} for i in range(5)])
            v = C.check_c1_pool_fingerprint({"note": "fingerprints omitted"}, {"pool": p})
            return v.verdict == "FAIL", {"verdict": v.verdict, "reasons": v.reasons[:3]}

    @case("charon_c1c2.ACCEPT.c1_crlf_normalised_fingerprint_is_stable", "charon_c1c2", "REPETITION")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "lf.jsonl"
            b = Path(tmp) / "crlf.jsonl"
            a.write_bytes(b'{"uid": 1}\n{"uid": 2}\n')
            b.write_bytes(b'{"uid": 1}\r\n{"uid": 2}\r\n')
            fa, fb = C.pool_fingerprint(a), C.pool_fingerprint(b)
            return fa["sha256"] == fb["sha256"] and fa["record_count"] == 2, {"lf": fa["sha256"][:12], "crlf": fb["sha256"][:12]}

    @case("charon_c1c2.SYNTHETIC_SIGNAL.c2_loader_admitting_transport_failed_uid_fails", "charon_c1c2", "SYNTHETIC_SIGNAL")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            rows = [{"uid": "u%d" % i, "rep": 1, "status": ("ok" if i != 3 else "http_504")} for i in range(6)]
            p = _pool(tmp, "pool.jsonl", rows)
            loader = lambda path: [r for _, r in C.read_rows(path)]  # admits everything, incl. u3  # noqa: E731
            v = C.check_c2_transport_not_residue(p, loader)
            return v.verdict == "FAIL", {"verdict": v.verdict, "fired": v.fired_count, "eligible": v.eligible_count}

    @case("charon_c1c2.SYNTHETIC_NULL.c2_loader_excluding_transport_failed_uid_passes", "charon_c1c2", "SYNTHETIC_NULL")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            rows = [{"uid": "u%d" % i, "rep": 1, "status": ("ok" if i != 3 else "http_504")} for i in range(6)]
            p = _pool(tmp, "pool.jsonl", rows)
            loader = lambda path: [r for _, r in C.read_rows(path) if r.get("status") == "ok"]  # noqa: E731
            v = C.check_c2_transport_not_residue(p, loader)
            return v.verdict == "PASS", {"verdict": v.verdict, "fired": v.fired_count, "eligible": v.eligible_count}

    @case("charon_c1c2.CORRUPT_INPUT.c2_no_transport_failures_is_indeterminate", "charon_c1c2", "CORRUPT_INPUT")
    def _():
        C = _c1c2()
        with tempfile.TemporaryDirectory() as tmp:
            rows = [{"uid": "u%d" % i, "rep": 1, "status": "ok"} for i in range(6)]
            p = _pool(tmp, "pool.jsonl", rows)
            loader = lambda path: [r for _, r in C.read_rows(path)]  # noqa: E731
            v = C.check_c2_transport_not_residue(p, loader)
            return v.verdict == "INDETERMINATE", {"verdict": v.verdict, "reasons": v.reasons[:2]}

    # ------------------------------------------------------------------ divergence_decomposition (harmonia/diagnostics/divergence_decomposition.py)
    def _dd():
        return importlib.import_module("harmonia.diagnostics.divergence_decomposition")

    @case("divergence_decomposition.ACCEPT.author_identity_tests_pass", "divergence_decomposition", "ACCEPT")
    def _():
        D = _dd()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = D.run_tests()
        return rc == 0, {"rc": rc, "tail": buf.getvalue().strip().splitlines()[-1:]}

    @case("divergence_decomposition.PARITY.ceiling_and_bounds_hand_values", "divergence_decomposition", "PARITY")
    def _():
        D = _dd()
        c = D.ceiling(0.5)
        lo, hi = D.bound_on_action_effect(0.5, 0.5)  # D equals ceiling -> excess 0
        lo2, hi2 = D.bound_on_action_effect(0.7, 0.5)  # excess 0.2 -> half 0.1
        ok = abs(c - 0.5) < 1e-12 and lo == 0.0 and abs(hi - 0.25) < 1e-12 and abs(lo2 - 0.1) < 1e-12 and abs(hi2 - 0.35) < 1e-12
        return ok, {"ceiling(0.5)": c, "bounds(D=ceiling)": (lo, hi), "bounds(D=0.7)": (lo2, hi2)}

    @case("divergence_decomposition.REJECT.below_ceiling_gives_zero_lower_bound", "divergence_decomposition", "REJECT")
    def _():
        D = _dd()
        lo, hi = D.bound_on_action_effect(0.3, 0.5)
        return lo == 0.0 and hi < 0.25, {"lo": lo, "hi": hi,
                                          "note": "a sub-ceiling divergence licenses NO positive action effect"}

    # ------------------------------------------------------------------ pm_instrument_contract (prometheus_math/instrument_contract.py)
    def _ic():
        return importlib.import_module("prometheus_math.instrument_contract")

    def _contract(I, name="parity_meter"):
        return I.InstrumentContract(
            name=name,
            positive=lambda: [2, 4, 6],
            negative=lambda: [1, 3, 5],
            invalid=lambda: None,
            sensitivity=lambda: ([2, 4, 6], [2, 4, 7]),
            is_signal=lambda v: v == "ALL_EVEN",
            is_no_signal=lambda v: v == "NOT_ALL_EVEN",
        )

    def _meter(xs):
        if xs is None:
            raise ValueError("no input")
        return "ALL_EVEN" if all(x % 2 == 0 for x in xs) else "NOT_ALL_EVEN"

    @case("pm_instrument_contract.ACCEPT.honest_meter_certified", "pm_instrument_contract", "ACCEPT")
    def _():
        I = _ic()
        r = I.certify(_meter, _contract(I), draws=3)
        return bool(r.admissible), {k: getattr(r, k) for k in vars(r) if not k.startswith("_")}

    @case("pm_instrument_contract.CHEAT.constant_signal_meter_refused", "pm_instrument_contract", "CHEAT")
    def _():
        I = _ic()
        r = I.certify(lambda xs: "ALL_EVEN", _contract(I), draws=1)
        return not r.admissible, {k: getattr(r, k) for k in vars(r) if not k.startswith("_")}

    @case("pm_instrument_contract.CHEAT.meter_ignoring_invalid_input_refused", "pm_instrument_contract", "CHEAT")
    def _():
        I = _ic()
        lenient = lambda xs: "NOT_ALL_EVEN" if xs is None else _meter(xs)  # noqa: E731
        r = I.certify(lenient, _contract(I), draws=1)
        return not r.admissible, {k: getattr(r, k) for k in vars(r) if not k.startswith("_")}

    @case("pm_instrument_contract.REJECT.contract_without_negative_refused", "pm_instrument_contract", "REJECT")
    def _():
        I = _ic()
        try:
            I.InstrumentContract(name="x", positive=lambda: 1, negative=None, invalid=lambda: None,
                                 sensitivity=lambda: (1, 2), is_signal=bool, is_no_signal=lambda v: not v)
        except I.ContractError as e:
            return True, {"raised": str(e)[:80]}
        return False, {"note": "contract with no anti-case accepted"}

    # ------------------------------------------------------------------ pm_degenerate_audit (prometheus_math/degenerate_audit.py)
    @case("pm_degenerate_audit.SYNTHETIC_SIGNAL.conflating_measure_flagged", "pm_degenerate_audit", "SYNTHETIC_SIGNAL")
    def _():
        A = importlib.import_module("prometheus_math.degenerate_audit")
        row = A.classify(lambda xs: 0.0, "constant_measure", "synthetic")
        return row.verdict == A.CONFLATES if hasattr(row, "verdict") else "CONFLATES" in repr(row), {"row": repr(row)[:160]}

    @case("pm_degenerate_audit.SYNTHETIC_NULL.refusing_measure_not_flagged", "pm_degenerate_audit", "SYNTHETIC_NULL")
    def _():
        A = importlib.import_module("prometheus_math.degenerate_audit")

        def strict(xs):
            if len(xs) < 2:
                raise ValueError("degenerate")
            return float(len(xs))
        row = A.classify(strict, "strict_measure", "synthetic")
        return (getattr(row, "verdict", None) == A.REFUSES) or ("REFUSES" in repr(row)), {"row": repr(row)[:160]}

    # ------------------------------------------------------------------ eos_intake (agents/eos/src/intake.py)
    def _intake():
        return _import_from("agents/eos/src", "intake")

    @case("eos_intake.CHEAT.unknown_sought_state_is_refused", "eos_intake", "CHEAT")
    def _():
        K = _intake()
        item = K.Item(id="i1", title="t", source="synthetic", provenance="keeper-fixture")
        v = K.classify(item, K.Claim(sought="ADMITTED", rationale="please"))
        return v.state == "REFUSED", {"state": v.state, "reason": v.reason[:100] if hasattr(v, "reason") else None}

    @case("eos_intake.CHEAT.anchor_with_no_referent_cannot_reach_pending", "eos_intake", "CHEAT")
    def _():
        K = _intake()
        item = K.Item(id="i2", title="t", source="synthetic", provenance="keeper-fixture")
        v = K.classify(item, K.Claim(sought="ANCHOR", rationale="it is very relevant and useful", falsifier="none"))
        return v.state != K.PENDING, {"state": v.state}

    @case("eos_intake.ACCEPT.proposer_refusal_preserved", "eos_intake", "ACCEPT")
    def _():
        K = _intake()
        item = K.Item(id="i3", title="t", source="synthetic")
        v = K.classify(item, K.Claim(sought="REFUSED", rationale="off-charter"))
        return v.state == "REFUSED", {"state": v.state}

    # ------------------------------------------------------------------ comms_identity (comms/identity.py) with a fake connection
    def _ident():
        return importlib.import_module("comms.identity")

    @case("comms_identity.ACCEPT.matching_identity_ok", "comms_identity", "ACCEPT")
    def _():
        I = _ident()
        reg = {"m1": {"db_system_id": "123", "db_name": "prom"}}
        v = I.check(_FakeConn(("123", "prom")), "m1", registry=reg)
        return v["ok"] is True and v["reason"] == "MATCH", {"reason": v["reason"]}

    @case("comms_identity.REJECT.wrong_database_refused", "comms_identity", "REJECT")
    def _():
        I = _ident()
        reg = {"m1": {"db_system_id": "123", "db_name": "prom"}}
        v = I.check(_FakeConn(("999", "prom")), "m1", registry=reg)
        return v["ok"] is False and v["reason"] == "WRONG_ENVIRONMENT" and v.get("mismatched") == ["db_system_id"], {
            "reason": v["reason"], "mismatched": v.get("mismatched")}

    @case("comms_identity.CHEAT.unknown_environment_fails_closed", "comms_identity", "CHEAT")
    def _():
        I = _ident()
        v = I.check(_FakeConn(("123", "prom")), "m9", registry={"m1": {"db_system_id": "123", "db_name": "prom"}})
        return v["ok"] is False and v["reason"] == "NO_EXPECTATION", {"reason": v["reason"]}

    @case("comms_identity.CORRUPT_INPUT.unreadable_identity_refused_and_rolled_back", "comms_identity", "CORRUPT_INPUT")
    def _():
        I = _ident()
        conn = _FakeConn(None, raise_exc=RuntimeError("connection dropped"))
        v = I.check(conn, "m1", registry={"m1": {"db_system_id": "123", "db_name": "prom"}})
        return v["ok"] is False and v["reason"] == "IDENTITY_UNREADABLE" and conn.rolled_back == 1, {
            "reason": v["reason"], "rolled_back": conn.rolled_back}

    # ------------------------------------------------------------------ apollo_e9_score (apollo/scripts/e9_score.py), fixture-bound
    @case("apollo_e9_score.PARITY.published_mix_adjusted_0_0667_reproduced", "apollo_e9_score", "PARITY")
    def _():
        p = REPO / "apollo" / "scripts" / "e9_score.py"
        battery = REPO / "roles" / "Charon" / "apollo_e9" / "charon_battery_E9.json"
        if not battery.exists():
            raise RuntimeError("DEPENDENCY_ABSENT: %s" % battery.relative_to(REPO))
        import subprocess
        r = subprocess.run([sys.executable, str(p)], cwd=str(REPO), capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        # the target is printed on every run; only the REPRODUCED line is computed
        return r.returncode == 0 and "REPRODUCED:" in out and "DRIFT" not in out, {
            "rc": r.returncode, "tail": out.strip().splitlines()[-6:]}
