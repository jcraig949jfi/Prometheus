"""Offline tests for the zoo-matrix scheduler (no network, no real sleeps).

Exercises the four load-bearing pieces of run_zoo_matrix that make a
thousands-of-call run survivable: the error taxonomy, per-provider pacing
(min-interval + RPM window) on a FAKE clock, resumable checkpointing, the
per-examinee parse-rate gate, and the bounded single re-ask. All reasoners and
the grader are injected fakes, so this runs instantly and deterministically.

Run: python harmonia/experiments/test_zoo_matrix.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_EXP = Path(__file__).resolve().parent
if str(_EXP) not in sys.path:
    sys.path.insert(0, str(_EXP))

from run_zoo_matrix import (  # noqa: E402
    err_class, ProviderPacer, Checkpoint, run_matrix, examinee_key,
)

_PASS = 0
_FAIL = 0


def check(name, cond, detail=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ok   {name}")
    else:
        _FAIL += 1
        suffix = f"  {detail}" if detail else ""
        print(f"  FAIL {name}{suffix}")


# ----------------------------------------------------------------- fakes
class FakeClock:
    """Monotonic clock that only advances when sleep() is called."""
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        if s > 0:
            self.sleeps.append(round(s, 6))
            self.t += s


def mkprobes(n):
    """n synthetic probes with stable ids; run_matrix only reads tier/version/kind."""
    return [(f"{i:04d}:T{i}:clean",
             SimpleNamespace(tier=f"T{i}", version="clean", kind="linear"))
            for i in range(n)]


def make_fake_factory(behavior):
    """behavior: examinee_key -> fn(probe, prompt_suffix) -> (ans_or_None, parse_error)."""
    def factory(provider, model, call_log, prompt_suffix=None):
        ek = examinee_key(provider, model)
        def reasoner(probe):
            ans, perr = behavior[ek](probe, prompt_suffix)
            return ans, {"_parse_error": perr, "_provider": ek, "ok": ans is not None and perr is None}
        return reasoner
    return factory


def fake_grader(probe, ans, tr):
    ok = bool(tr.get("ok"))
    return {"_kill_pattern": None if ok else "x"}, ok


def _no_sleep_pacer():
    return ProviderPacer({"_default": {"min_interval": 0.0}},
                         now=lambda: 0.0, sleep=lambda s: None)


# ----------------------------------------------------------------- tests
def test_err_class():
    check("err None -> ok", err_class(None) == "ok")
    check("err http_error:429 -> transport", err_class("http_error:429") == "transport")
    check("err call_exception:Timeout -> transport",
          err_class("call_exception:TimeoutError") == "transport")
    check("err api_error -> transport", err_class("api_error:overloaded") == "transport")
    check("err no_choices -> content", err_class("no_choices") == "content")
    check("err empty_content -> content", err_class("empty_content") == "content")
    check("err json_decode_error -> parse", err_class("json_decode_error:Expecting") == "parse")
    check("err no_json_object -> parse", err_class("no_json_object") == "parse")
    check("err unbalanced_braces -> parse", err_class("unbalanced_braces") == "parse")
    check("err mystery -> other", err_class("totally_unknown") == "other")


def test_pacer_min_interval():
    clk = FakeClock()
    p = ProviderPacer({"P": {"min_interval": 5.0}, "Q": {"min_interval": 0.0}},
                      now=clk.now, sleep=clk.sleep)
    p.wait("P")                       # first call: no wait
    check("min-interval: first call no sleep", clk.sleeps == [])
    p.wait("P")                       # second call to P: must wait 5s
    check("min-interval: second same-provider sleeps 5", clk.sleeps == [5.0])
    p.wait("Q")                       # different provider: not blocked by P's interval
    check("min-interval: other provider not blocked", clk.sleeps == [5.0])


def test_pacer_rpm_window():
    clk = FakeClock()
    p = ProviderPacer({"P": {"min_interval": 0.0, "rpm": 2}}, now=clk.now, sleep=clk.sleep)
    p.wait("P"); p.wait("P")          # fill the 2/min window at t=0
    check("rpm: first two no sleep", clk.sleeps == [])
    p.wait("P")                       # third must wait ~60s for the window to slide
    check("rpm: third call sleeps ~60", clk.sleeps == [60.0])


def test_checkpoint_resume():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        c1 = Checkpoint(path)
        check("ckpt empty initially", c1.done == set())
        c1.record({"examinee": "P:m", "probe_id": "0001", "ok": True})
        c1.record({"examinee": "P:m", "probe_id": "0002", "ok": False})
        c1.close()
        c2 = Checkpoint(path)         # reopen: done-set rebuilt from disk
        check("ckpt resume loads 2", len(c2.records) == 2)
        check("ckpt is_done true", c2.is_done("P:m", "0001"))
        check("ckpt is_done false for new", not c2.is_done("P:m", "0003"))
        c2.close()


def test_checkpoint_tolerates_halfwritten_line():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        path.write_text('{"examinee":"P:m","probe_id":"0001","ok":true}\n{"examinee":"P:m","pr',
                        encoding="utf-8")
        c = Checkpoint(path)          # second line is a killed half-write
        check("ckpt skips half-written final line", len(c.records) == 1)
        check("ckpt good line survives", c.is_done("P:m", "0001"))
        c.close()


def test_run_matrix_basic_and_resume():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(5)
        examinees = [("P", "strong", "mid"), ("P", "weak", "open-small")]
        behavior = {
            "P:strong": lambda probe, sfx: (["a"], None),                 # always clean
            "P:weak":   lambda probe, sfx: (["a"], None),                 # also clean here
        }
        pacer = _no_sleep_pacer()
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer,
                          factory=make_fake_factory(behavior), grader=fake_grader,
                          warmup=False, log=lambda *_: None)
        ck.close()
        check("basic: all cells graded", summ["n_cells"] == 10)
        check("basic: strong acc present", summ["matrix"]["P:strong"]["n_scored"] == 5)

        # resume: reopen same ckpt, run again -> nothing new should be queued
        ck2 = Checkpoint(path)
        before = len(ck2.records)
        summ2 = run_matrix(examinees, probes, ck2, pacer,
                           factory=make_fake_factory(behavior), grader=fake_grader,
                           warmup=False, log=lambda *_: None)
        ck2.close()
        check("resume: no new cells added", len(ck2.records) == before == 10)
        check("resume: summary stable", summ2["n_cells"] == 10)


def test_reask_recovers_parse_failure():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(5)
        examinees = [("P", "flaky", "mid")]
        # parse-fails when no suffix; complies when the re-ask suffix is present
        def flaky(probe, sfx):
            return (["a"], None) if sfx else (None, "no_json_object")
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory({"P:flaky": flaky}),
                          grader=fake_grader, warmup=False, reask=True,
                          log=lambda *_: None)
        ck.close()
        m = summ["matrix"]["P:flaky"]
        check("reask: all recovered to ok", m["n_scored"] == 5)
        check("reask: parse-fail rate 0 after recovery", m["parse_fail_rate"] == 0.0)
        oks = [r["ok"] for r in ck.records]
        check("reask: every cell ok", all(oks) and len(oks) == 5)


def test_gate_degrades_and_drops():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(10)
        examinees = [("P", "hopeless", "open-small")]
        # genuine parse fail on EVERY attempt, even with the re-ask suffix
        behavior = {"P:hopeless": lambda probe, sfx: (None, "no_json_object")}
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory(behavior), grader=fake_grader,
                          gate_min_attempts=8, gate_parse_thresh=0.40,
                          drop_degraded=True, warmup=False, log=lambda *_: None)
        ck.close()
        m = summ["matrix"]["P:hopeless"]
        check("gate: examinee flagged degraded", m["degraded"] is True)
        skipped = [r for r in ck.records if r.get("err_class") == "skipped_degraded"]
        graded = [r for r in ck.records if r.get("err_class") == "parse"]
        check("gate: first 8 attempted then dropped remainder", len(graded) == 8)
        check("gate: remaining 2 cells recorded as skipped_degraded", len(skipped) == 2)
        check("gate: total cells still 10 (nothing lost)", len(ck.records) == 10)


def test_gate_does_not_fire_below_threshold():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(10)
        examinees = [("P", "clean", "mid")]
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory({"P:clean": lambda probe, sfx: (["a"], None)}),
                          grader=fake_grader, gate_min_attempts=8,
                          drop_degraded=True, warmup=False, log=lambda *_: None)
        ck.close()
        check("gate: clean examinee not degraded", summ["matrix"]["P:clean"]["degraded"] is False)
        check("gate: all 10 graded", summ["matrix"]["P:clean"]["n_scored"] == 10)


def test_transport_not_counted_as_parse():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(10)
        examinees = [("P", "rate-limited", "mid")]
        # pure transport failures (429s) — must NOT trip the parse-rate gate
        behavior = {"P:rate-limited": lambda probe, sfx: (None, "http_error:429")}
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory(behavior), grader=fake_grader,
                          gate_min_attempts=8, drop_degraded=True, warmup=False,
                          log=lambda *_: None)
        ck.close()
        m = summ["matrix"]["P:rate-limited"]
        check("transport: not degraded by 429s", m["degraded"] is False)
        # all attempts were transport -> zero scoreable cells -> rate undefined (None),
        # NOT 0 (which would falsely imply clean parses), and NOT counted as wrong answers
        check("transport: parse_fail_rate undefined (None)", m["parse_fail_rate"] is None)
        check("transport: nothing scored as wrong", m["n_scored"] == 0)
        check("transport: transport_fails counted", m["transport_fails"] == 10)


def test_round_robin_interleaves_providers():
    """Two examinees on DIFFERENT providers: pacer calls should interleave
    A,B,A,B,A,B... rather than draining all-of-A then all-of-B (which would burst
    one provider into its 429 floor)."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(4)
        examinees = [("P", "alpha", "mid"), ("Q", "beta", "mid")]
        # record provider-call order via a fake pacer
        calls: list[str] = []

        class RecordingPacer(ProviderPacer):
            def wait(self, provider):
                calls.append(provider)
        rp = RecordingPacer({"_default": {"min_interval": 0.0}},
                            now=lambda: 0.0, sleep=lambda s: None)
        ck = Checkpoint(path)
        behavior = {"P:alpha": lambda probe, sfx: (["a"], None),
                    "Q:beta":  lambda probe, sfx: (["a"], None)}
        run_matrix(examinees, probes, ck, rp,
                   factory=make_fake_factory(behavior), grader=fake_grader,
                   warmup=False, log=lambda *_: None)
        ck.close()
        # 2 examinees * 4 probes = 8 calls; interleaved order should alternate P,Q,P,Q,...
        check("interleave: 8 calls recorded", len(calls) == 8)
        check("interleave: first 4 alternate providers",
              calls[:4] == ["P", "Q", "P", "Q"],
              detail=f"got {calls[:4]}")


def test_reask_bounded_to_one_retry():
    """Re-ask must fire AT MOST once per cell — even if the re-ask itself parse-fails,
    no second re-ask happens (cost guard)."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(3)
        examinees = [("P", "always-parse-fail", "mid")]
        attempts_per_probe: list[int] = []

        def factory(provider, model, call_log, prompt_suffix=None):
            def reasoner(probe):
                # count attempts globally; behavior unaffected by suffix
                attempts_per_probe.append(1)
                return None, {"_parse_error": "no_json_object",
                              "_provider": "P:always-parse-fail", "ok": False}
            return reasoner
        ck = Checkpoint(path)
        run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                   factory=factory, grader=fake_grader,
                   gate_min_attempts=999, warmup=False, log=lambda *_: None)
        ck.close()
        # 3 probes * (1 first attempt + 1 re-ask) = exactly 6 calls; NEVER 9 (would be 2 re-asks)
        check("reask-bounded: at most 2 calls per probe", len(attempts_per_probe) == 6,
              detail=f"got {len(attempts_per_probe)} calls for 3 probes")


def test_examinee_state_isolation():
    """A degrading examinee must NOT degrade or otherwise affect a sibling running
    on the same/different provider."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(10)
        examinees = [("P", "hopeless", "open-small"), ("P", "fine", "mid")]
        behavior = {"P:hopeless": lambda probe, sfx: (None, "no_json_object"),
                    "P:fine":     lambda probe, sfx: (["a"], None)}
        ck = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory(behavior), grader=fake_grader,
                          gate_min_attempts=8, gate_parse_thresh=0.40,
                          drop_degraded=False, warmup=False, log=lambda *_: None)
        ck.close()
        check("isolation: hopeless flagged degraded",
              summ["matrix"]["P:hopeless"]["degraded"] is True)
        check("isolation: fine NOT degraded",
              summ["matrix"]["P:fine"]["degraded"] is False)
        check("isolation: fine fully scored",
              summ["matrix"]["P:fine"]["n_scored"] == 10)
        check("isolation: fine parse-fail rate 0",
              summ["matrix"]["P:fine"]["parse_fail_rate"] == 0.0)


def test_kill_then_resume_finishes_remainder():
    """Simulate a real kill mid-run by stopping after N cells, then re-instantiating
    the runner — it must complete the remaining cells and produce the same total."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        probes = mkprobes(6)
        examinees = [("P", "stable", "mid")]
        behavior = {"P:stable": lambda probe, sfx: (["a"], None)}

        # Phase 1: factory that raises after the 4th call to simulate a kill
        n_calls = [0]
        def crashing_factory(provider, model, call_log, prompt_suffix=None):
            def reasoner(probe):
                n_calls[0] += 1
                if n_calls[0] > 4:
                    raise RuntimeError("simulated kill mid-cell-5")
                return ["a"], {"_parse_error": None, "_provider": "P:stable", "ok": True}
            return reasoner
        ck1 = Checkpoint(path)
        try:
            run_matrix(examinees, probes, ck1, pacer=_no_sleep_pacer(),
                       factory=crashing_factory, grader=fake_grader,
                       warmup=False, log=lambda *_: None)
        except RuntimeError:
            pass
        ck1.close()
        check("kill+resume: phase 1 wrote partial",
              0 < len(ck1.records) < 6,
              detail=f"phase 1 records={len(ck1.records)}")

        # Phase 2: clean factory, fresh Checkpoint instance, same file -> should resume
        ck2 = Checkpoint(path)
        summ = run_matrix(examinees, probes, ck2, pacer=_no_sleep_pacer(),
                          factory=make_fake_factory(behavior), grader=fake_grader,
                          warmup=False, log=lambda *_: None)
        ck2.close()
        check("kill+resume: total 6 cells after resume",
              summ["matrix"]["P:stable"]["n_scored"] == 6,
              detail=f"got n_scored={summ['matrix']['P:stable']['n_scored']}")
        # the checkpoint file should have exactly 6 records (no duplicates from resume)
        recs_on_disk = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        check("kill+resume: no duplicate records on disk",
              len(recs_on_disk) == 6,
              detail=f"file has {len(recs_on_disk)} lines")


def main():
    for fn in [test_err_class, test_pacer_min_interval, test_pacer_rpm_window,
               test_checkpoint_resume, test_checkpoint_tolerates_halfwritten_line,
               test_run_matrix_basic_and_resume, test_reask_recovers_parse_failure,
               test_gate_degrades_and_drops, test_gate_does_not_fire_below_threshold,
               test_transport_not_counted_as_parse,
               test_round_robin_interleaves_providers,
               test_reask_bounded_to_one_retry,
               test_examinee_state_isolation,
               test_kill_then_resume_finishes_remainder]:
        print(f"\n# {fn.__name__}")
        fn()
    print(f"\n==== {_PASS} passed, {_FAIL} failed ====")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
