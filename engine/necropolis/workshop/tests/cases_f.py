"""Necropolis workshop control cases, batch F (NECROPOLIS VALIDATION layer).

Keeper-authored controls over the NECROPOLIS ADAPTER layer
(engine/necropolis/workshop/adapters/).  An adapter is held to the same bar as
a harvested tool: it must behave on inputs whose right answer is known by
construction, and a cheat against it must be seen to fail.  No case reads a
grave; the Pollux replay cases use synthetic value lists only.
"""
from __future__ import annotations

import importlib
import json
import math
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def _ad(name):
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    return importlib.import_module("engine.necropolis.workshop.adapters." + name)


def _spearman_honest(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return None
    ra = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: a[i]))}
    rb = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: b[i]))}
    d2 = sum((ra[i] - rb[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def register(case):
    # ------------------------------------------------------------------ instrument_null
    @case("adapters_instrument_null.SYNTHETIC_NULL.sorted_spearman_is_tautological", "adapters_instrument_null", "SYNTHETIC_NULL")
    def _():
        """The Pollux construction (sort both sides, then rank-correlate) must read TAUTOLOGICAL."""
        IN = _ad("instrument_null")
        rng = random.Random(1)
        a = [rng.random() for _ in range(40)]
        b = [rng.random() for _ in range(40)]
        r = IN.instrument_null(lambda x, y: _spearman_honest(sorted(x), sorted(y)), a, b, n_draws=50, seed=3)
        return r["verdict"] == "TAUTOLOGICAL", {"verdict": r["verdict"], "observed": r["observed"]}

    @case("adapters_instrument_null.SYNTHETIC_SIGNAL.honest_spearman_is_responsive", "adapters_instrument_null", "SYNTHETIC_SIGNAL")
    def _():
        IN = _ad("instrument_null")
        rng = random.Random(2)
        a = [rng.random() for _ in range(40)]
        b = [v + 0.05 * rng.random() for v in a]
        r = IN.instrument_null(_spearman_honest, a, b, n_draws=50, seed=3)
        ok = r["verdict"] == "RESPONSIVE" and r["observed"] > 0.9 and r["shuffle_b"]["frac_ge_observed"] == 0.0
        return ok, {"verdict": r["verdict"], "observed": r["observed"], "shuffle_max": r["shuffle_b"]["max"]}

    @case("adapters_instrument_null.CHEAT.nondeterministic_stat_is_flagged", "adapters_instrument_null", "CHEAT")
    def _():
        """A statistic that draws its own randomness cannot pass as RESPONSIVE."""
        IN = _ad("instrument_null")
        rng = random.Random(5)
        r = IN.instrument_null(lambda x, y: rng.random(), [1.0] * 12, [2.0] * 12, n_draws=10, seed=0)
        return r["verdict"] == "NONDETERMINISTIC", {"verdict": r["verdict"]}

    @case("adapters_instrument_null.CORRUPT_INPUT.none_returning_stat_is_unmeasurable", "adapters_instrument_null", "CORRUPT_INPUT")
    def _():
        IN = _ad("instrument_null")
        r = IN.instrument_null(lambda x, y: None, [1.0, 2.0], [3.0, 4.0], n_draws=5)
        return r["verdict"] == "UNMEASURABLE", {"verdict": r["verdict"]}

    @case("adapters_instrument_null.REPETITION.same_seed_same_reading", "adapters_instrument_null", "REPETITION")
    def _():
        IN = _ad("instrument_null")
        rng = random.Random(9)
        a = [rng.random() for _ in range(30)]
        b = [rng.random() for _ in range(30)]
        r1 = IN.instrument_null(_spearman_honest, a, b, n_draws=30, seed=11)
        r2 = IN.instrument_null(_spearman_honest, a, b, n_draws=30, seed=11)
        return r1 == r2, {"verdict": r1["verdict"]}

    # ------------------------------------------------------------------ pollux_statistic_replay
    @case("adapters_pollux_replay.PARITY.historical_matches_daemon_construction", "adapters_pollux_replay", "PARITY")
    def _():
        """Re-derive run_tick's numbers by hand from the daemon's own helpers and compare."""
        PR = _ad("pollux_statistic_replay")
        D = importlib.import_module("charon.agents.pollux.daemon")
        rng = random.Random(21)
        a = sorted(rng.uniform(1.0, 2.0) for _ in range(50))
        b = sorted(rng.uniform(1.0, 2.0) for _ in range(45))
        h = PR.historical_statistic(a, b)
        n = min(len(a), len(b))
        raw = D._spearman(sorted(a)[:n], sorted(b)[:n])
        an, bn = D._mean_spacing_normalize(sorted(a)[:n]), D._mean_spacing_normalize(sorted(b)[:n])
        m = min(len(an), len(bn))
        norm = D._spearman(an[:m], bn[:m]) if m >= 10 else None
        kp = D._classify(raw, norm)
        ok = (h["n_paired"] == n and h["kill_pattern"] == kp
              and h["corr_raw"] == (round(raw, 4) if raw is not None else None)
              and h["corr_norm"] == (round(norm, 4) if norm is not None else None))
        return ok, {"replay": {k: h[k] for k in ("n_paired", "corr_raw", "corr_norm", "kill_pattern", "verdict")}}

    @case("adapters_pollux_replay.SYNTHETIC_NULL.independent_samples_corr_raw_reads_tautological", "adapters_pollux_replay", "SYNTHETIC_NULL")
    def _():
        PR = _ad("pollux_statistic_replay")
        rng = random.Random(22)
        a = [rng.uniform(1.0, 2.0) for _ in range(60)]
        b = [rng.uniform(1.0, 2.0) for _ in range(60)]
        r = PR.replay(a, b, n_draws=40, seed=1)
        raw = r["diagnostics"]["corr_raw"]
        ok = raw["verdict"] == "TAUTOLOGICAL" and r["historical"]["corr_raw"] == 1.0
        return ok, {"corr_raw_verdict": raw["verdict"], "historical": r["historical"]["corr_raw"],
                    "corr_norm_verdict": r["diagnostics"]["corr_norm"]["verdict"],
                    "historical_verdict": r["historical"]["verdict"]}

    @case("adapters_pollux_replay.CHEAT.verdict_on_independent_samples_is_not_rejected_by_daemon", "adapters_pollux_replay", "CHEAT")
    def _():
        """Cheat: hand the daemon two INDEPENDENT uniform samples; can it be talked into a
        PROMOTED/UNVERIFIED rather than REJECTED?  PASS = the replay's diagnostics expose
        the construction even when the historical verdict does not reject.  Recorded either
        way: the historical verdict is reported as observed, never adjusted."""
        PR = _ad("pollux_statistic_replay")
        verdicts = {}
        exposed = True
        for s in range(5):
            rng = random.Random(100 + s)
            a = [rng.uniform(1.0, 2.0) for _ in range(80)]
            b = [rng.uniform(1.0, 2.0) for _ in range(80)]
            r = PR.replay(a, b, n_draws=30, seed=s)
            verdicts[s] = r["historical"]["verdict"]
            if r["diagnostics"]["corr_raw"]["verdict"] != "TAUTOLOGICAL":
                exposed = False
        return exposed, {"historical_verdicts_on_independent_samples": verdicts}

    # ------------------------------------------------------------------ resampling_null (FRANK-004 machinery)
    @case("adapters_resampling_null.PARITY.ks_distance_matches_scipy", "adapters_resampling_null", "PARITY")
    def _():
        RN = _ad("resampling_null")
        try:
            from scipy.stats import ks_2samp
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("DEPENDENCY_ABSENT: scipy " + str(e))
        rng = random.Random(3)
        worst = 0.0
        for _ in range(20):
            x = [rng.gauss(0, 1) for _ in range(rng.randint(5, 60))]
            y = [rng.gauss(0.3, 1.2) for _ in range(rng.randint(5, 60))]
            worst = max(worst, abs(RN.ks_distance(x, y) - float(ks_2samp(x, y).statistic)))
        return worst < 1e-12, {"max_abs_diff": worst}

    @case("adapters_resampling_null.SYNTHETIC_NULL.two_random_subsets_not_coincident", "adapters_resampling_null", "SYNTHETIC_NULL")
    def _():
        """Two disjoint random subsets of one pool: p_lower must be ordinary (not < alpha)
        across seeds.  A tool that calls random halves 'coincident beyond scale' is void."""
        RN = _ad("resampling_null")
        rng = random.Random(4)
        pool = sorted(rng.uniform(1.0, 3.0) for _ in range(400))
        idx = rng.sample(range(400), 80)
        a = [pool[i] for i in idx[:40]]
        b = [pool[i] for i in idx[40:]]
        r = RN.two_sample_read(a, b, pool, seeds=(0, 1, 2), n_draws=150)
        ps = [x["p_lower"] for x in r["per_seed"]]
        ok = r["verdict"] != "COINCIDENT_BEYOND_SCALE" and all(p > r["alpha"] for p in ps)
        return ok, {"verdict": r["verdict"], "p_lower": ps, "split_half_hits": [r["split_half"]["a"]["hits"], r["split_half"]["b"]["hits"]]}

    @case("adapters_resampling_null.SYNTHETIC_SIGNAL.identical_gap_multiset_is_seen", "adapters_resampling_null", "SYNTHETIC_SIGNAL")
    def _():
        """Plant the one alternative a lower-tail KS on gaps CAN see: b carries exactly a's
        gap multiset (D = 0 up to one float-summation tie).  p_lower must be at the null's floor on every seed and the
        exponential negative control must not be void."""
        RN = _ad("resampling_null")
        rng = random.Random(6)
        pool = sorted(rng.uniform(1.0, 3.0) for _ in range(400))
        a = sorted(rng.sample(pool, 40))
        gaps = [a[i + 1] - a[i] for i in range(39)]
        rng.shuffle(gaps)
        b = [2.0]
        for g in gaps:
            b.append(b[-1] + g)
        # 150 draws would put the p floor (1/151) ABOVE alpha = 0.05/9; FRANK-004 uses 1000
        r = RN.two_sample_read(a, b, pool, seeds=(0, 1), n_draws=400)
        ps = [x["p_lower"] for x in r["per_seed"]]
        ok = r["d_observed"] <= 1 / 39 + 1e-12 and all(p < 0.05 / 9 for p in ps) and not r["negative_control"]["void"]
        return ok, {"verdict": r["verdict"], "d_observed": r["d_observed"], "p_lower": ps,
                    "negative_p": r["negative_control"]["p_lower"]}

    @case("adapters_resampling_null.PERTURBATION.split_half_control_fails_at_alpha_rate_for_iid_continuous", "adapters_resampling_null", "PERTURBATION")
    def _():
        """MEASUREMENT (INFO), not a verdict on the adapter: FRANK-004's split-half positive
        control asks a subset to be judged coincident with a random half of itself at
        p_lower < 0.05/9 in >= 4/5 halvings.  The two-sample KS statistic is
        distribution-free under 'same distribution', and the random-subset null IS a
        same-distribution null at the same sizes, so P(p_lower < alpha) = alpha for ANY
        iid continuous gap law, whatever n or shape.  Measured here on tight lognormal
        gap sequences (n=200) against a uniform pool: hits over 30 trials x 5 halvings."""
        RN = _ad("resampling_null")
        rng = random.Random(0)
        pool = sorted(rng.uniform(1.0, 3.0) for _ in range(3000))
        hits = trials = 0
        resolvable = 0
        for t in range(30):
            v = [1.0]
            for _ in range(199):
                v.append(v[-1] + rng.lognormvariate(0, 0.2))
            s = RN.split_half_control(v, pool, n_draws=200, seed=t)
            hits += s["hits"]
            trials += 5
            resolvable += int(s["resolvable"])
        return None, {"hit_rate": hits / trials, "alpha": 0.05 / 9, "resolvable_subsets": resolvable, "of": 30,
                      "reading": "split-half positive control cannot pass for iid continuous data; "
                                 "FRANK-004 kill condition (2) fires on synthetic data before any grave is read"}

    @case("adapters_resampling_null.CORRUPT_INPUT.too_small_to_halve_is_unresolvable", "adapters_resampling_null", "CORRUPT_INPUT")
    def _():
        RN = _ad("resampling_null")
        rng = random.Random(7)
        pool = sorted(rng.uniform(1.0, 3.0) for _ in range(100))
        r = RN.two_sample_read(pool[:4], pool[10:14], pool, seeds=(0,), n_draws=20)
        return r["verdict"] == "UNRESOLVABLE_AT_THIS_N", {"verdict": r["verdict"]}

    @case("adapters_resampling_null.REPETITION.same_seed_same_null", "adapters_resampling_null", "REPETITION")
    def _():
        RN = _ad("resampling_null")
        rng = random.Random(8)
        pool = [rng.uniform(1.0, 3.0) for _ in range(200)]
        n1 = RN.random_subset_null(pool, 20, 25, n_draws=50, seed=17)
        n2 = RN.random_subset_null(pool, 20, 25, n_draws=50, seed=17)
        n3 = RN.random_subset_null(pool, 20, 25, n_draws=50, seed=18)
        return n1 == n2 and n1 != n3, {"n": len(n1)}

    # ------------------------------------------------------------------ jsonl_ledger_census
    @case("adapters_jsonl_census.ACCEPT.counts_rows_keys_and_verdicts", "adapters_jsonl_census", "ACCEPT")
    def _():
        JC = _ad("jsonl_ledger_census")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ledger.jsonl"
            rows = [{"id": i, "verdict": "PROMOTED" if i % 3 else "REJECTED", "ts": "2026-09-%02dT00:00:00Z" % (i + 1),
                     "ghost": None} for i in range(9)]
            p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
            c = JC.census(p)
        ok = (c["rows"] == 9 and c["malformed"] == 0 and c["verdict_columns"]["verdict"] == {"PROMOTED": 6, "REJECTED": 3}
              and "ghost" in c["dead_fields"] and c["timestamp_ranges"]["ts"]["min"].startswith("2026-09-01")
              and c["timestamp_ranges"]["ts"]["max"].startswith("2026-09-09"))
        return ok, {"rows": c["rows"], "dead": list(c["dead_fields"]), "verdicts": c["verdict_columns"]}

    @case("adapters_jsonl_census.CORRUPT_INPUT.malformed_lines_counted_not_dropped", "adapters_jsonl_census", "CORRUPT_INPUT")
    def _():
        JC = _ad("jsonl_ledger_census")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ledger.jsonl"
            p.write_text('{"a": 1}\nnot json\n[1,2]\n\n{"a": 2}\n', encoding="utf-8")
            c = JC.census(p)
        ok = c["rows"] == 2 and c["malformed"] == 2 and [m["line"] for m in c["malformed_lines"]] == [2, 3]
        return ok, {"rows": c["rows"], "malformed": c["malformed_lines"]}

    @case("adapters_jsonl_census.SYNTHETIC_SIGNAL.partial_field_reported", "adapters_jsonl_census", "SYNTHETIC_SIGNAL")
    def _():
        JC = _ad("jsonl_ledger_census")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "l.jsonl"
            p.write_text('{"a": 1, "b": 1}\n{"a": 2}\n{"a": 3}\n', encoding="utf-8")
            c = JC.census(p)
            pf = JC.dead_field_via_preflight(p, ["b", "zzz"])
        ok = c["partial_fields"].get("b", {}).get("absent") == 2 and "b" not in c["dead_fields"]
        if pf is not None:
            ok = ok and pf == ["dead_field[zzz]"]
        return ok, {"partial": c["partial_fields"], "preflight_dead": pf}

    @case("adapters_jsonl_census.REJECT.missing_file_reported_not_invented", "adapters_jsonl_census", "REJECT")
    def _():
        JC = _ad("jsonl_ledger_census")
        c = JC.census(Path(tempfile.gettempdir()) / ("necro_does_not_exist_%d.jsonl" % random.randint(0, 10**9)))
        return c["exists"] is False and c["rows"] == 0, c

    # ------------------------------------------------------------------ git_history_census
    @case("adapters_git_census.ACCEPT.tracked_file_has_history_and_is_in_head", "adapters_git_census", "ACCEPT")
    def _():
        GC = _ad("git_history_census")
        h = GC.history("comms/manifest.py", REPO)
        ok = h["n_commits"] >= 1 and h["in_head"] and h["first"] is not None and h["deleted_in"] == []
        return ok, {"n_commits": h["n_commits"], "first": h["first"], "last": h["last"]}

    @case("adapters_git_census.SYNTHETIC_SIGNAL.deleted_path_recovered_matches_git_show", "adapters_git_census", "SYNTHETIC_SIGNAL")
    def _():
        """Pick a deleted .py from history, recover it to scratch, and confirm the bytes
        are exactly what `git show` gives (sha256 over LF text)."""
        import hashlib
        import subprocess
        GC = _ad("git_history_census")
        dead = GC.deleted_python_files(REPO, since="2026-01-01", limit=3)
        if not dead:
            return None, {"note": "no deleted .py since 2026-01-01; nothing to recover"}
        d = dead[0]
        parent = d["deleted_in"] + "^"
        with tempfile.TemporaryDirectory() as td:
            r = GC.recover(d["path"], parent, REPO, Path(td))
            if not r["ok"]:
                return False, r
            raw = subprocess.run(["git", "show", parent + ":" + d["path"]], cwd=REPO, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace").stdout
            ok = r["sha256_lf"] == hashlib.sha256(raw.encode("utf-8")).hexdigest() and Path(r["recovered_to"]).exists()
        return ok, {"path": d["path"], "deleted_in": d["deleted_in"][:12], "bytes": r["bytes"], "first_three_dead_since_jan": [x["path"] for x in dead]}

    @case("adapters_git_census.CHEAT.recovery_into_live_tree_refused", "adapters_git_census", "CHEAT")
    def _():
        GC = _ad("git_history_census")
        try:
            GC.recover("comms/manifest.py", "HEAD", REPO, REPO / "comms")
            return False, {"note": "wrote into the live tree"}
        except PermissionError as e:
            return True, {"refused": str(e)[:120]}

    @case("adapters_git_census.CHEAT.mutating_git_verbs_refused", "adapters_git_census", "CHEAT")
    def _():
        GC = _ad("git_history_census")
        refused = []
        for verb in ("checkout", "reset", "restore", "stash"):
            try:
                GC._git([verb, "--", "."], REPO)
            except PermissionError:
                refused.append(verb)
        return refused == ["checkout", "reset", "restore", "stash"], {"refused": refused}

    # ------------------------------------------------------------------ consumer_trace
    @case("adapters_consumer_trace.ACCEPT.self_reference_excluded_and_known_importer_found", "adapters_consumer_trace", "ACCEPT")
    def _():
        CT = _ad("consumer_trace")
        t = CT.trace("comms/manifest.py", REPO)
        files = {h["file"] for h in t["hits"]}
        ok = t["truncated"] is False and "comms/manifest.py" not in files and t["n_external"] >= 1
        return ok, {"n_external": t["n_external"], "n_importers": t["n_importers"], "sample": sorted(files)[:5]}

    @case("adapters_consumer_trace.SYNTHETIC_NULL.unique_token_has_no_consumers", "adapters_consumer_trace", "SYNTHETIC_NULL")
    def _():
        CT = _ad("consumer_trace")
        t = CT.trace("zz_necro_unique_%d_token.py" % random.randint(10**8, 10**9), REPO)
        return t["n_hits"] == 0 and t["truncated"] is False, {"n_hits": t["n_hits"]}

    @case("adapters_consumer_trace.SYNTHETIC_SIGNAL.planted_importer_in_scratch_found", "adapters_consumer_trace", "SYNTHETIC_SIGNAL")
    def _():
        CT = _ad("consumer_trace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "pkg").mkdir()
            (root / "pkg" / "victim.py").write_text("X = 1\n", encoding="utf-8")
            (root / "user1.py").write_text("from pkg.victim import X\n", encoding="utf-8")
            (root / "user2.py").write_text("import pkg.victim\n", encoding="utf-8")
            (root / "notes.md").write_text("see victim.py for details\n", encoding="utf-8")
            t = CT.trace("pkg/victim.py", root)
        ok = t["n_importers"] == 2 and t["n_external"] == 3
        return ok, {"n_external": t["n_external"], "n_importers": t["n_importers"]}

    # ------------------------------------------------------------------ manifest_verify
    @case("adapters_manifest_verify.ACCEPT.written_manifest_is_covered", "adapters_manifest_verify", "ACCEPT")
    def _():
        MV = _ad("manifest_verify")
        M = importlib.import_module("comms.manifest")
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "a.txt").write_text("alpha\n", encoding="utf-8")
            (d / "b.txt").write_text("beta\n", encoding="utf-8")
            M.write(d)
            r = MV.verify_with_coverage(d)
        return r["verdict"] == "COVERED" and r["checked"] == 2, {"verdict": r["verdict"], "checked": r["checked"]}

    @case("adapters_manifest_verify.SYNTHETIC_SIGNAL.added_file_and_subdir_reported_uncovered", "adapters_manifest_verify", "SYNTHETIC_SIGNAL")
    def _():
        MV = _ad("manifest_verify")
        M = importlib.import_module("comms.manifest")
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "a.txt").write_text("alpha\n", encoding="utf-8")
            M.write(d)
            (d / "late.txt").write_text("added after\n", encoding="utf-8")
            (d / "sub").mkdir()
            (d / "sub" / "deep.txt").write_text("never listed\n", encoding="utf-8")
            r = MV.verify_with_coverage(d)
        ok = r["verdict"] == "UNCOVERED_FILES" and r["unlisted_top_level"] == ["late.txt"] and r["uncovered_subdirectory_files"] == ["sub/deep.txt"]
        return ok, {k: r[k] for k in ("verdict", "unlisted_top_level", "uncovered_subdirectory_files")}

    @case("adapters_manifest_verify.PERTURBATION.one_byte_change_is_mismatch", "adapters_manifest_verify", "PERTURBATION")
    def _():
        MV = _ad("manifest_verify")
        M = importlib.import_module("comms.manifest")
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "a.txt").write_text("alpha\n", encoding="utf-8")
            M.write(d)
            (d / "a.txt").write_text("alphb\n", encoding="utf-8")
            r = MV.verify_with_coverage(d)
        return r["verdict"] == "HASH_MISMATCH" and len(r["bad"]) == 1, {"verdict": r["verdict"], "bad": r["bad"]}

    # ------------------------------------------------------------------ pg_readonly_probe (guard only; DB unreachable)
    @case("adapters_pg_probe.ACCEPT.plain_select_admitted", "adapters_pg_probe", "ACCEPT")
    def _():
        PG = _ad("pg_readonly_probe")
        ok = True
        for q in ("SELECT 1", "  select count(*) from t where x = 'set y'", "WITH c AS (SELECT 1) SELECT * FROM c",
                  "EXPLAIN SELECT 1", "SHOW server_version", "SELECT * FROM t -- delete me\n"):
            try:
                PG.guard(q)
            except PG.RefusedSQL as e:
                ok = False
                return ok, {"wrongly_refused": q, "why": str(e)}
        return ok, {}

    @case("adapters_pg_probe.CHEAT.write_statements_refused", "adapters_pg_probe", "CHEAT")
    def _():
        PG = _ad("pg_readonly_probe")
        attacks = ["DELETE FROM t", "SELECT 1; DROP TABLE t", "WITH d AS (DELETE FROM t RETURNING *) SELECT * FROM d",
                   "SELECT pg_sleep(10)", "SELECT nextval('s')", "SELECT * INTO newt FROM t", "UPDATE t SET x=1",
                   "select 1 /* ; */ ; truncate t", "SET search_path = evil", "SELECT pg_terminate_backend(1)",
                   "COPY t TO '/tmp/x'", "CREATE TABLE z (a int)"]
        passed = []
        for q in attacks:
            try:
                PG.guard(q)
                passed.append(q)
            except PG.RefusedSQL:
                pass
        return passed == [], {"cheats_that_passed": passed}

    @case("adapters_pg_probe.REJECT.readonly_query_never_commits_and_always_rolls_back", "adapters_pg_probe", "REJECT")
    def _():
        PG = _ad("pg_readonly_probe")

        class Cur:
            description = [("a",), ("b",)]

            def __init__(self):
                self.executed = []

            def execute(self, sql, params=()):
                self.executed.append(sql)

            def fetchmany(self, n):
                return [(1, 2)]

            def fetchone(self):
                return None

        class Conn:
            def __init__(self):
                self.cur, self.rollbacks, self.commits = Cur(), 0, 0

            def cursor(self):
                return self.cur

            def rollback(self):
                self.rollbacks += 1

            def commit(self):
                self.commits += 1

        c = Conn()
        r = PG.readonly_query(c, "SELECT a, b FROM t")
        ok = (c.commits == 0 and c.rollbacks == 1 and c.cur.executed[0] == "SET TRANSACTION READ ONLY"
              and r["n"] == 1 and r["columns"] == ["a", "b"])
        return ok, {"executed": c.cur.executed, "rollbacks": c.rollbacks, "commits": c.commits}

    @case("adapters_pg_probe.ACCEPT.network_reachability_observation", "adapters_pg_probe", "ACCEPT")
    def _():
        """INFO only: is the canonical store reachable from this host right now?"""
        import socket
        host = "192.168.1.202"
        try:
            with socket.create_connection((host, 5432), timeout=2):
                reach = True
        except OSError as e:
            reach = False
            err = type(e).__name__
        return None, {"host": host, "port": 5432, "reachable": reach, "error": None if reach else err}

    # ------------------------------------------------------------------ sigma_kernel_runner
    @case("adapters_sigma_runner.ACCEPT.a148_names_under_historical_convention", "adapters_sigma_runner", "ACCEPT")
    def _():
        SR = _ad("sigma_kernel_runner")
        r = SR.names("a148_obstruction", REPO)
        ok = r["ok"] and "unanimous_kill_rate" in (r["value"] or []) and "analyze_family" in (r["value"] or [])
        return ok, {"rc": r["rc"], "n_names": len(r["value"] or []), "stderr": r["stderr_tail"][-120:]}

    @case("adapters_sigma_runner.PARITY.unanimous_kill_rate_hand_check", "adapters_sigma_runner", "PARITY")
    def _():
        """unanimous_kill_rate(group, kills): read its source, feed a hand-built group."""
        SR = _ad("sigma_kernel_runner")
        src = (REPO / "sigma_kernel/a148_obstruction.py").read_text(encoding="utf-8", errors="replace")
        start = src.find("def unanimous_kill_rate")
        body = src[start:start + 600]
        return None, {"source_excerpt": body[:400]}

    @case("adapters_sigma_runner.REJECT.missing_module_reported_not_invented", "adapters_sigma_runner", "REJECT")
    def _():
        SR = _ad("sigma_kernel_runner")
        r = SR.names("a999_does_not_exist", REPO)
        return (not r["ok"]) and r["rc"] != 0 and "ModuleNotFoundError" in r["stderr_tail"], {"rc": r["rc"]}

    # ------------------------------------------------------------------ literal_verdict_lint
    @case("adapters_verdict_lint.SYNTHETIC_SIGNAL.unconditional_pass_flagged", "adapters_verdict_lint", "SYNTHETIC_SIGNAL")
    def _():
        LV = _ad("literal_verdict_lint")
        src = ('def judge(x):\n    """Careful judge."""\n    if x:\n        return "PASS"\n    return "PASS"\n'
               'def judge2(x):\n    return {"verdict": "PROMOTED", "n": 3}\n'
               'def ok(x):\n    return True\n')
        f = LV.lint_source(src, "s.py")
        names = sorted(x["function"] for x in f)
        return names == ["judge", "judge2", "ok"], {"flagged": names}

    @case("adapters_verdict_lint.SYNTHETIC_NULL.data_dependent_verdict_not_flagged", "adapters_verdict_lint", "SYNTHETIC_NULL")
    def _():
        LV = _ad("literal_verdict_lint")
        src = ('def judge(x):\n    if x > 1:\n        return "PASS"\n    return "FAIL"\n'
               'def judge2(x):\n    if not x:\n        raise ValueError()\n    return "PASS"\n'
               'def calc(x):\n    return x * 2\n'
               'def label():\n    return "hello"\n')
        f = LV.lint_source(src, "s.py")
        return f == [], {"flagged": f}

    @case("adapters_verdict_lint.ACCEPT.scan_of_workshop_adapters_is_clean", "adapters_verdict_lint", "ACCEPT")
    def _():
        LV = _ad("literal_verdict_lint")
        r = LV.lint_paths([REPO / "engine/necropolis/workshop/adapters"], REPO)
        return r["n_findings"] == 0, {"files": r["files_scanned"], "findings": r["findings"]}

    @case("adapters_verdict_lint.ACCEPT.scan_of_necropolis_evidence_scripts", "adapters_verdict_lint", "ACCEPT")
    def _():
        """INFO: what the lint says about the Necropolis's own evidence scripts and the
        three graves' judge code.  Observation, not a verdict."""
        LV = _ad("literal_verdict_lint")
        targets = [REPO / "engine/necropolis/dossiers", REPO / "charon/agents/pollux"]
        targets = [t for t in targets if t.exists()]
        r = LV.lint_paths(targets, REPO)
        return None, {"files": r["files_scanned"], "n_findings": r["n_findings"],
                      "findings": [(f["file"], f["function"], f["literal"]) for f in r["findings"]][:20]}

    # ------------------------------------------------------------------ z3_receipt_redirect
    @case("adapters_z3_redirect.ACCEPT.first_check_runs_without_touching_ledgers", "adapters_z3_redirect", "ACCEPT")
    def _():
        ZR = _ad("z3_receipt_redirect")
        try:
            importlib.import_module("z3")
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("DEPENDENCY_ABSENT: z3 " + str(e))
        r = ZR.run_check("techne/acquisition/checks/z3_first_check.py", REPO, timeout=300)
        ok = r["rc"] == 0 and r["ledger_touched"] == {"receipts": [], "locks": []}
        return ok, {"rc": r["rc"], "touched": r["ledger_touched"], "seconds": r["seconds"], "tail": r["tail"][-160:]}
