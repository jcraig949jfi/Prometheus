"""Necropolis workshop control cases, batch D (NECROPOLIS VALIDATION layer).

Wave-2 Keeper-authored controls, second batch: leakage audit, chance-floor
library, liveness derivation, symmetry null check, measurement guard,
preflight meters, BOCPD, spec hashing.  Same verdict vocabulary as
run_controls.  Every case manufactures its own inputs; none reads a grave.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


class _Probe:
    """Minimal probe stand-in: the leakage audit reads .data and .ground_truth."""

    def __init__(self, data, gt):
        self.data = data
        self.ground_truth = gt


def _import_from(subdir: str, module: str):
    p = str(REPO / subdir)
    if p not in sys.path:
        sys.path.insert(0, p)
    return importlib.import_module(module)


def register(case):

    # ------------------------------------------------------------------ ladder_leakage_audit
    @case("ladder_leakage_audit.ACCEPT.r6_declared_leak_reproduced", "ladder_leakage_audit", "ACCEPT")
    def _():
        L = importlib.import_module("harmonia.diagnostics.ladder_leakage_audit")
        r = L.audit_tier("R6", L.TIERS["R6"])
        ok = r.get("verdict") == "LEAKS" and "truth" in (r.get("leaking_fields") or [])
        return ok, {"verdict": r.get("verdict"), "leaking_fields": r.get("leaking_fields"),
                    "payload_reader": r.get("payload_reader"), "chance_floor": r.get("chance_floor")}

    @case("ladder_leakage_audit.SYNTHETIC_SIGNAL.planted_exact_leak_field_detected", "ladder_leakage_audit", "SYNTHETIC_SIGNAL")
    def _():
        L = importlib.import_module("harmonia.diagnostics.ladder_leakage_audit")
        rng = random.Random(0)
        probes = []
        for _ in range(40):
            gt = rng.randrange(7)
            probes.append(_Probe({"a": rng.randrange(7), "hidden_key": gt}, gt))
        fields = list(L.leaking_fields(probes))
        return fields == ["hidden_key"], {"leaking_fields": fields}

    @case("ladder_leakage_audit.SYNTHETIC_NULL.clean_probes_report_no_leak", "ladder_leakage_audit", "SYNTHETIC_NULL")
    def _():
        L = importlib.import_module("harmonia.diagnostics.ladder_leakage_audit")
        rng = random.Random(1)
        probes = [_Probe({"a": rng.randrange(7), "b": rng.randrange(7)}, rng.randrange(7)) for _ in range(60)]
        fields = list(L.leaking_fields(probes))
        return fields == [], {"leaking_fields": fields}

    @case("ladder_leakage_audit.PERTURBATION.str_transformed_key_escapes_detection", "ladder_leakage_audit", "PERTURBATION")
    def _():
        # Scope-boundary measurement (INFO), not a cheat against the declared contract:
        # the audit tests exact equality only.
        L = importlib.import_module("harmonia.diagnostics.ladder_leakage_audit")
        rng = random.Random(2)
        probes = []
        for _ in range(40):
            gt = rng.randrange(7)
            probes.append(_Probe({"a": rng.randrange(7), "hidden_key": str(gt)}, gt))
        fields = list(L.leaking_fields(probes))
        return None, {"leaking_fields_detected": fields,
                      "note": "str(ground_truth) planted in probe.data; audit scope is exact-equality "
                              "leaks only, so a CLEAN verdict does not mean no answer key is present"}

    @case("ladder_leakage_audit.ACCEPT.chance_floor_is_majority_rate", "ladder_leakage_audit", "ACCEPT")
    def _():
        L = importlib.import_module("harmonia.diagnostics.ladder_leakage_audit")
        probes = [_Probe({}, 3)] * 7 + [_Probe({}, 1)] * 2 + [_Probe({}, 0)]
        pct, val = L.chance_floor(probes)
        # contract: percent, and the value is repr(ground_truth)
        return abs(pct - 70.0) < 1e-9 and val == repr(3), {"pct": pct, "val": val}

    # ------------------------------------------------------------------ nemesis_cheatlib
    def _cheatlib():
        return _import_from("roles/Nemesis/science", "cheatlib")

    @case("nemesis_cheatlib.PARITY.chance_floor_hand_parity", "nemesis_cheatlib", "PARITY")
    def _():
        C = _cheatlib()
        cf = C.chance_floor(["x"] * 6 + ["y"] * 3 + ["z"], candidate_counts=[3] * 10)
        ok = (cf.eligible == 10 and cf.majority_value == "x" and abs(cf.majority_rate - 0.6) < 1e-12
              and abs(cf.uniform_rate - 1 / 3) < 1e-12 and cf.distinct_answers == 3)
        return ok, {"eligible": cf.eligible, "majority": cf.majority_value, "majority_rate": cf.majority_rate,
                    "uniform_rate": cf.uniform_rate, "distinct": cf.distinct_answers}

    @case("nemesis_cheatlib.SYNTHETIC_SIGNAL.constant_responder_scores_exactly_majority", "nemesis_cheatlib", "SYNTHETIC_SIGNAL")
    def _():
        C = _cheatlib()
        items = [{"id": i, "ans": ("x" if i % 5 < 3 else "y")} for i in range(50)]
        cf = C.chance_floor([it["ans"] for it in items])
        hits, elig, rate = C.score_responder(C.DegenerateConstant(cf.majority_value), items, lambda it: it["ans"])
        return elig == 50 and abs(rate - cf.majority_rate) < 1e-12, {
            "hits": hits, "eligible": elig, "rate": rate, "majority_rate": cf.majority_rate}

    @case("nemesis_cheatlib.REJECT.empty_answers_refused_or_zero", "nemesis_cheatlib", "REJECT")
    def _():
        C = _cheatlib()
        try:
            cf = C.chance_floor([])
        except Exception as e:  # noqa: BLE001
            return True, {"raised": type(e).__name__}
        return cf.eligible == 0 and cf.majority_rate == 0.0, {
            "eligible": cf.eligible, "majority_rate": cf.majority_rate, "note": "returned rather than raised"}

    @case("nemesis_cheatlib.CORRUPT_INPUT.none_answers_count_as_answers", "nemesis_cheatlib", "CORRUPT_INPUT")
    def _():
        # Observation: None is treated as an ordinary answer value by BOTH chance_floor and
        # score_responder (denominator = len(items)), so the pair is internally consistent;
        # the caller must filter unanswerable items or the floor is over a padded population.
        C = _cheatlib()
        cf = C.chance_floor(["x", None, "x", None, "y"])
        hits, elig, rate = C.score_responder(C.DegenerateConstant(None), [
            {"a": "x"}, {"a": None}, {"a": "x"}, {"a": None}, {"a": "y"}], lambda it: it["a"])
        return None, {"eligible": cf.eligible, "majority": cf.majority_value, "majority_rate": cf.majority_rate,
                      "constant_None_rate": rate, "note": "None is not filtered anywhere in cheatlib"}

    # ------------------------------------------------------------------ pronoia_liveness
    def _pl():
        return _import_from("roles/Pronoia/science", "productive_liveness")

    def _health(P, now, cadence=60.0, **kw):
        from datetime import datetime, timezone
        dt = lambda t: None if t is None else datetime.fromtimestamp(t, tz=timezone.utc)  # noqa: E731
        h = P.derive_health(dt(now), P.WorkEvidence(**{k: dt(v) for k, v in kw.items()}), cadence)
        return str(getattr(h, "value", h)).lower()

    @case("pronoia_liveness.ACCEPT.recent_success_is_productive", "pronoia_liveness", "ACCEPT")
    def _():
        P = _pl()
        now = 10_000.0
        h = _health(P, now, started_at=now - 5000, last_heartbeat_at=now - 10,
                    last_attempt_at=now - 30, last_success_at=now - 30)
        return h.endswith("productive"), {"health": h}

    @case("pronoia_liveness.REJECT.heartbeat_only_is_stalled_not_productive", "pronoia_liveness", "REJECT")
    def _():
        P = _pl()
        now = 10_000.0
        h = _health(P, now, started_at=now - 5000, last_heartbeat_at=now - 10,
                    last_attempt_at=now - 4000, last_success_at=now - 4000)
        return "productive" not in h and h.endswith("stalled"), {"health": h}

    @case("pronoia_liveness.CHEAT.success_without_attempt_is_incoherent", "pronoia_liveness", "CHEAT")
    def _():
        P = _pl()
        now = 10_000.0
        h = _health(P, now, started_at=now - 5000, last_heartbeat_at=now - 10,
                    last_attempt_at=None, last_success_at=now - 30)
        return h.endswith("incoherent"), {"health": h}

    @case("pronoia_liveness.CHEAT.future_success_timestamp_is_incoherent", "pronoia_liveness", "CHEAT")
    def _():
        P = _pl()
        now = 10_000.0
        h = _health(P, now, started_at=now - 5000, last_heartbeat_at=now - 10,
                    last_attempt_at=now + 500, last_success_at=now + 500)
        return h.endswith("incoherent"), {"health": h}

    @case("pronoia_liveness.REJECT.attempts_without_success_is_failing", "pronoia_liveness", "REJECT")
    def _():
        P = _pl()
        now = 10_000.0
        h = _health(P, now, started_at=now - 5000, last_heartbeat_at=now - 10,
                    last_attempt_at=now - 20, last_success_at=None)
        return h.endswith("failing"), {"health": h}

    # ------------------------------------------------------------------ herakles_c3_null_check
    def _c3():
        return importlib.import_module("herakles.evca.c3_null_check")

    @case("herakles_c3_null_check.ACCEPT.author_self_test_zero_failures", "herakles_c3_null_check", "ACCEPT")
    def _():
        C = _c3()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            n = C.self_test()
        return n == 0, {"failures": n, "lines": buf.getvalue().count("\n")}

    @case("herakles_c3_null_check.SYNTHETIC_SIGNAL.digest_mismatch_is_not_identical", "herakles_c3_null_check", "SYNTHETIC_SIGNAL")
    def _():
        C = _c3()
        base = {"twin_id": "r", "transform": "none", "mask_digest": "aaa", "n_incorrect": 1, "accuracy": 0.5}
        row = {"twin_id": "r", "transform": "reflect", "ic_transformed": True, "mask_digest": "bbb",
               "n_incorrect": 1, "accuracy": 0.5}
        got = C.check_pair(base, row)
        return got["verdict"] == C.NOT_IDENTICAL, {"verdict": got["verdict"], "disagreed": got.get("disagreed")}

    @case("herakles_c3_null_check.REJECT.untransformed_ic_is_indeterminate_not_identical", "herakles_c3_null_check", "REJECT")
    def _():
        C = _c3()
        base = {"twin_id": "r", "transform": "none", "mask_digest": "aaa", "n_incorrect": 1, "accuracy": 0.5}
        row = {"twin_id": "r", "transform": "reflect", "ic_transformed": False, "mask_digest": "aaa",
               "n_incorrect": 1, "accuracy": 0.5}
        got = C.check_pair(base, row)
        return got["verdict"] == C.INDETERMINATE, {"verdict": got["verdict"]}

    @case("herakles_c3_null_check.CHEAT.accuracy_agreement_alone_cannot_buy_identical", "herakles_c3_null_check", "CHEAT")
    def _():
        C = _c3()
        base = {"twin_id": "r", "transform": "none", "mask_digest": "aaa", "n_incorrect": 3, "accuracy": 0.9}
        row = {"twin_id": "r", "transform": "complement", "ic_transformed": True, "majority_target_flipped": True,
               "mask_digest": "zzz", "n_incorrect": 3, "accuracy": 0.9}
        got = C.check_pair(base, row)
        return got["verdict"] != C.IDENTICAL, {"verdict": got["verdict"], "compared": got.get("compared")}

    @case("herakles_c3_null_check.CORRUPT_INPUT.missing_transform_field_is_indeterminate", "herakles_c3_null_check", "CORRUPT_INPUT")
    def _():
        C = _c3()
        base = {"twin_id": "r", "transform": "none", "mask_digest": "aaa"}
        got = C.check_pair(base, {"twin_id": "r", "mask_digest": "aaa"})
        return got["verdict"] == C.INDETERMINATE, {"verdict": got["verdict"]}

    # ------------------------------------------------------------------ measurement_guard
    def _mg():
        return importlib.import_module("techne.lib.measurement_guard")

    @case("measurement_guard.ACCEPT.passing_control_admits_measurement", "measurement_guard", "ACCEPT")
    def _():
        M = _mg()
        m = M.measure("t", lambda: 42, population="synthetic", controls=[("two", lambda: 1 + 1, 2)])
        return m.value == 42 and m.controls_passed == ["two"], {"value": m.value, "controls": m.controls_passed}

    @case("measurement_guard.REJECT.no_control_refused", "measurement_guard", "REJECT")
    def _():
        M = _mg()
        try:
            M.measure("t", lambda: 42, population="synthetic", controls=[])
        except M.InstrumentInvalid as e:
            return True, {"raised": str(e)[:80]}
        return False, {"note": "measured with no positive control"}

    @case("measurement_guard.REJECT.failing_control_blocks_value", "measurement_guard", "REJECT")
    def _():
        M = _mg()
        ran = []
        try:
            M.measure("t", lambda: ran.append(1) or 42, population="synthetic", controls=[("bad", lambda: 3, 2)])
        except M.InstrumentInvalid:
            return ran == [], {"fn_ran": bool(ran)}
        return False, {"note": "failed control did not block"}

    @case("measurement_guard.CHEAT.type_mismatched_control_rejected", "measurement_guard", "CHEAT")
    def _():
        M = _mg()
        try:
            M.measure("t", lambda: 42, population="synthetic", controls=[("str_two", lambda: "2", 2)])
        except M.InstrumentInvalid:
            return True, {"note": "str/int type mismatch treated as control failure"}
        return False, {"note": "double-encoded control admitted"}

    # ------------------------------------------------------------------ icarus_tier_oracle
    @case("icarus_tier_oracle.ACCEPT.cheat_fields_declared", "icarus_tier_oracle", "ACCEPT")
    def _():
        T = importlib.import_module("agents.icarus.tier_oracle")
        f = getattr(T, "_CHEAT_DATA_FIELDS", None)
        return bool(f), {"cheat_fields": sorted(f) if f else None}

    # ------------------------------------------------------------------ attacks_preflight
    def _pf():
        return _import_from("attacks", "preflight")

    def _as_list(f):
        return f if isinstance(f, list) else [f]

    @case("attacks_preflight.ACCEPT.author_selftest_all_ok", "attacks_preflight", "ACCEPT")
    def _():
        A = _pf()
        res = A.selftest()
        bad = [f.check for f in res if not f.ok]
        return not bad, {"n": len(res), "bad": bad}

    @case("attacks_preflight.SYNTHETIC_SIGNAL.dead_field_fires_on_absent_column", "attacks_preflight", "SYNTHETIC_SIGNAL")
    def _():
        # contract: dead_field fires on a field NO row carries (absent or None), not a constant one
        A = _pf()
        rows = [{"v": i, "w": None} for i in range(100)]
        fs = _as_list(A.dead_field(rows, ["k", "v", "w"]))
        bad = sorted(x.check for x in fs if not x.ok)
        return bad == ["dead_field[k]", "dead_field[w]"], {"findings": [(x.check, x.ok) for x in fs]}

    @case("attacks_preflight.SYNTHETIC_NULL.dead_field_silent_on_varying_columns", "attacks_preflight", "SYNTHETIC_NULL")
    def _():
        A = _pf()
        rows = [{"k": i % 3, "v": i} for i in range(100)]
        fs = _as_list(A.dead_field(rows, ["k", "v"]))
        return all(x.ok for x in fs), {"findings": [(x.check, x.ok) for x in fs]}

    # ------------------------------------------------------------------ stygian_bocpd
    def _bocpd():
        return importlib.import_module("charon.agents.stygian.loaders._bocpd")

    def _shifted(seed=0):
        rng = random.Random(seed)
        return [rng.gauss(0, 1) for _ in range(60)] + [rng.gauss(6, 1) for _ in range(60)]

    @case("stygian_bocpd.SYNTHETIC_SIGNAL.planted_mean_shift_located", "stygian_bocpd", "SYNTHETIC_SIGNAL")
    def _():
        B = _bocpd()
        r = B.detect_changepoints(_shifted())
        d = vars(r)
        loc = next((d[k] for k in d if "changepoint" in k and isinstance(d[k], (int, float))), None)
        return loc is not None and 55 <= int(loc) <= 65, {"located": loc, "fields": sorted(d)}

    @case("stygian_bocpd.SYNTHETIC_NULL.stationary_series_no_strong_changepoint", "stygian_bocpd", "SYNTHETIC_NULL")
    def _():
        B = _bocpd()
        rng = random.Random(3)
        r = B.detect_changepoints([rng.gauss(0, 1) for _ in range(120)])
        d = vars(r)
        post = next((d[k] for k in d if isinstance(d[k], (list, tuple)) and len(d[k]) > 10), None)
        mx = max(post[5:]) if post else None
        return mx is not None and mx < 0.5, {"max_posterior_after_5": mx, "fields": sorted(d)}

    @case("stygian_bocpd.REPETITION.deterministic", "stygian_bocpd", "REPETITION")
    def _():
        B = _bocpd()
        obs = _shifted()
        return repr(vars(B.detect_changepoints(obs))) == repr(vars(B.detect_changepoints(obs))), {}

    # ------------------------------------------------------------------ vivarium_spec_hash
    @case("vivarium_spec_hash.REPETITION.key_order_invariant", "vivarium_spec_hash", "REPETITION")
    def _():
        V = importlib.import_module("vivarium.viv.spec")
        a = V.spec_hash({"a": 1, "b": {"c": [1, 2]}})
        b = V.spec_hash({"b": {"c": [1, 2]}, "a": 1})
        return a == b and len(a) >= 16, {"hash": a[:16]}

    @case("vivarium_spec_hash.PERTURBATION.one_element_changes_hash", "vivarium_spec_hash", "PERTURBATION")
    def _():
        V = importlib.import_module("vivarium.viv.spec")
        return V.spec_hash({"a": 1, "b": {"c": [1, 2]}}) != V.spec_hash({"a": 1, "b": {"c": [1, 3]}}), {}

    @case("vivarium_spec_hash.REJECT.invalid_spec_refused", "vivarium_spec_hash", "REJECT")
    def _():
        V = importlib.import_module("vivarium.viv.spec")
        try:
            V.validate({"not": "a spec"})
        except V.SpecError as e:
            return True, {"raised": str(e)[:100]}
        except Exception as e:  # noqa: BLE001
            return False, {"raised_other": type(e).__name__}
        return False, {"note": "accepted garbage"}
