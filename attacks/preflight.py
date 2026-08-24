"""Admissibility preflight — deterministic, no LLM, no network, no judgment.

    A verdict is ADMISSIBLE when a program can confirm the claim could have come out
    the other way, on the population named, from rows that still exist.

This does NOT decide whether a finding is true. That needs inference and always will. It
decides whether the finding is WELL-FORMED — and every defect this program shipped in the week
of 2026-08-17..24 was a well-formedness failure, not a reasoning failure. Each check below is
derived from one of them, and each fires on the real artifact that produced it.

Why non-LLM: an LLM checking an LLM's work shares ancestry with it and converges (the program's
own A7 finding: "mutation + self-reporting, not mutation + selection"). These checks cannot be
argued with, cannot be persuaded by a well-written rationale, and return the same answer to
every seat.

    python attacks/preflight.py --selftest      # positive control: every check fires on a
                                                # planted defect and stays silent on clean data
    python attacks/preflight.py --probes        # run every EXECUTABLE probe in the registry
    python attacks/preflight.py --ledgers DIR   # dead-field + frame census over a ledger dir

Exit 1 = at least one check failed. Wire it: .git/hooks/pre-commit.

Charon (kill authority), 2026-08-24.
"""
import argparse
import collections
import glob
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Finding:
    def __init__(self, check, ok, detail):
        self.check, self.ok, self.detail = check, ok, detail

    def __str__(self):
        return f"  [{'PASS' if self.ok else 'FAIL'}] {self.check}: {self.detail}"


# --------------------------------------------------------------------------- C1 dead field

def dead_field(rows, fields):
    """A gate input that NO row carries. The gate is not strict — it is inert.

    Kill it caught (2026-08-23): `drip_coldband` computed
    `truncation_rate = mean(r.get("completion_tokens") or 0 >= MAX_TOK)` over rows whose writer
    never emitted `completion_tokens`. The rate was identically 0.0000 by construction and the
    gate could not fail. Reported as a passing measurement for a full day.

    The rule generalizes past loaders to metrics: a gate whose input is absent must RAISE, never
    return a passing value. `dict.get(k) or 0` is the idiom that hides it.
    """
    rows = list(rows)
    out = []
    for f in fields:
        n = sum(1 for r in rows if isinstance(r, dict) and r.get(f) is not None)
        cov = n / len(rows) if rows else 0.0
        out.append(Finding(
            f"dead_field[{f}]", cov > 0,
            f"coverage {cov:.4f} ({n}/{len(rows)} rows)" if cov > 0 else
            f"ABSENT from all {len(rows)} rows — any gate reading it is inert, not strict"))
    return out


# ------------------------------------------------------------------ C2 degenerate strata

def degenerate_strata(rows, outcome_key, strata_keys, min_n=30, eps=0.02):
    """Is the outcome determined by STRATUM IDENTITY rather than by within-stratum structure?

    Kill it caught (Aporia 150-N, 2026-08-24): `abs_diff_le_N` between a single-digit knot
    invariant and a four-digit conductor cannot hold for any N; against a small float regulator
    it always holds. The outcome variable was measuring whether two catalogues use comparable
    UNITS. That confound silently produced, and then destroyed, an eight-cycle research arc, and
    half of a second agent's population carried it undeclared.

    Mechanical form: group by the stratum key, take each group's outcome rate, and report the
    share of MASS sitting in groups pinned at 0 or 1. High degenerate mass means a model can
    score well by learning the stratum label, and the interesting within-stratum question was
    never posed. This is one groupby. Nobody ran it for a year.
    """
    rows = [r for r in rows if isinstance(r, dict)]
    g = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        key = tuple(str(r.get(k)) for k in strata_keys)
        c = g[key]
        c[0] += bool(r.get(outcome_key))
        c[1] += 1
    big = {k: v for k, v in g.items() if v[1] >= min_n}
    if not big:
        return [Finding("degenerate_strata", True,
                        f"no stratum reached n>={min_n}; check not informative here")]
    tot = sum(v[1] for v in big.values())
    deg = {k: v for k, v in big.items() if v[0] / v[1] < eps or v[0] / v[1] > 1 - eps}
    mass = sum(v[1] for v in deg.values())
    frac = mass / tot
    ex = sorted(deg.items(), key=lambda kv: -kv[1][1])[:3]
    detail = (f"{len(deg)}/{len(big)} strata pinned at 0 or 1, holding {frac:.1%} of mass"
              + (f" — e.g. {[(k, f'{v[0]/v[1]:.3f}', v[1]) for k, v in ex]}" if ex else ""))
    return [Finding(f"degenerate_strata[{outcome_key}|{'+'.join(strata_keys)}]",
                    frac < 0.10, detail)]


# ------------------------------------------------- C3 feature constant within ranking group

def constant_within_group(rows, group_key, feature_key, min_groups=10):
    """A feature used to RANK inside a group must vary inside that group.

    Kill it caught (Diomedes cycle 001, 2026-08-24): `Z_parent` scored AUC exactly 0.5000 across
    every seed. Not a null — the parent-state representation assigns the SAME value to every
    candidate in a state, so it cannot express "a_3 beats a_7" at all. A type error wearing a
    measurement's clothes, and it would read as an honest negative result to any reviewer who
    only saw the number.

    Mechanical form: within-group variance. If a feature is constant in most groups, its
    within-group ranking metric is 0.5 by construction and reporting it as a finding is an error
    regardless of what the number is.
    """
    rows = [r for r in rows if isinstance(r, dict)]
    g = collections.defaultdict(set)
    for r in rows:
        g[str(r.get(group_key))].add(str(r.get(feature_key)))
    if len(g) < min_groups:
        return [Finding(f"constant_within_group[{feature_key}]", True,
                        f"only {len(g)} groups; check not informative")]
    const = sum(1 for v in g.values() if len(v) <= 1)
    frac = const / len(g)
    return [Finding(f"constant_within_group[{feature_key}|by {group_key}]", frac < 0.50,
                    f"constant in {const}/{len(g)} groups ({frac:.1%}) — "
                    + ("cannot rank within a group; any within-group AUC is 0.5 by construction"
                       if frac >= 0.50 else "varies in most groups"))]


# --------------------------------------------------------------------------- C4 frame

def frame(dirpath, patterns):
    """Does the declared file population equal the directory's actual contents?

    Kill it caught (2026-08-24): `theseus/corpus` holds 100 `batch-*.jsonl.gz` and 165
    `batch-*.jsonl`, nearly disjoint, covering different date ranges with different generator
    mixes. One seat globbed only the first, the reference full-corpus scan and a second seat read
    only the second, and numbers from each were quoted beside each other as one corpus.

    Four wrong-population errors landed in this program in one week, by three different agents,
    including one of mine. The shape is always the same: the sampling frame is whatever the glob
    returned, and it is then described as the population. This check makes the residue loud.
    """
    d = pathlib.Path(dirpath)
    if not d.is_dir():
        return [Finding("frame", False, f"{dirpath} is not a directory")]
    allf = {p.name for p in d.iterdir() if p.is_file()}
    matched = set()
    per = {}
    for pat in patterns:
        m = {pathlib.Path(p).name for p in glob.glob(str(d / pat))}
        per[pat] = len(m)
        matched |= m
    residue = allf - matched
    ok = not residue
    return [Finding("frame", ok,
                    f"{per}, matched {len(matched)}/{len(allf)} files" +
                    ("" if ok else f" — {len(residue)} UNMATCHED, e.g. "
                                   f"{sorted(residue)[:2]}; a statistic over the matched set is "
                                   f"not a statistic over this directory"))]


# ------------------------------------------------------------------------ C5 unsourced

def unsourced(verdict_path, ledger_path):
    """Is the aggregate standing on rows that still exist AND are tracked by git?

    Kill it caught (2026-08-23): two committed verdicts had their row ledgers destroyed by
    `git stash -u` + `git stash drop`, because the ledgers were never tracked. For ~14 hours
    every load-bearing number in a rulings request was an assertion with a filename. Recovered
    from unreachable objects; all 13 figures then reproduced exactly.

    Untracked is the whole failure mode: untracked files are what ordinary git hygiene deletes,
    and nothing in a pipeline raises when they go.
    """
    v, l = pathlib.Path(verdict_path), pathlib.Path(ledger_path)
    if not v.exists():
        return [Finding("unsourced", True, f"{v.name}: verdict absent, nothing to source")]
    if not l.exists():
        return [Finding("unsourced", False, f"{v.name}: source ledger MISSING FROM DISK")]
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(l)],
                       cwd=ROOT, capture_output=True)
    tracked = r.returncode == 0
    n = sum(1 for _ in l.open(encoding="utf-8", errors="replace"))
    return [Finding("unsourced", tracked,
                    f"{v.name} <- {l.name} ({n} rows, {'tracked' if tracked else 'UNTRACKED'})"
                    + ("" if tracked else " — one `git clean` from an unsourced verdict"))]


# ---------------------------------------------------------------------------- runners

def run_probes():
    out = []
    for p in sorted(glob.glob(str(ROOT / "attacks/probes/*.py"))):
        name = pathlib.Path(p).stem
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, p], cwd=ROOT, capture_output=True,
                           text=True, env=env)
        tail = (r.stdout or r.stderr or "").strip().splitlines()
        out.append(Finding(f"probe[{name}]", r.returncode == 0,
                           tail[-1][:150] if tail else f"exit {r.returncode}"))
    return out


def selftest():
    """POSITIVE CONTROL. Every check must fire on a planted defect AND stay silent on clean
    data. A meter without a positive control is not a meter — that is constitutional here, and
    this file is not exempt from the rule it enforces."""
    res = []

    clean = [{"completion_tokens": 100, "holds": i % 2, "pair": f"p{i%5}",
              "state": f"s{i%20}", "feat": i} for i in range(400)]
    planted = [{"holds": i % 2, "pair": f"p{i%5}", "state": f"s{i%20}", "feat": i%20}
               for i in range(400)]
    for i, r in enumerate(planted):                 # pin every stratum to 0 or 1
        r["holds"] = 1 if r["pair"] in ("p0", "p1") else 0

    def expect(name, findings, want_fail):
        bad = [f for f in findings if not f.ok]
        got_fail = bool(bad)
        ok = got_fail == want_fail
        res.append(Finding(f"selftest::{name}", ok,
                           ("fired as required" if want_fail else "silent as required")
                           if ok else
                           ("DID NOT FIRE on a planted defect — this check is inert"
                            if want_fail else "FALSE POSITIVE on clean data")))

    expect("dead_field/planted", dead_field(planted, ["completion_tokens"]), True)
    expect("dead_field/clean", dead_field(clean, ["completion_tokens"]), False)
    expect("degenerate/planted", degenerate_strata(planted, "holds", ["pair"]), True)
    expect("degenerate/clean", degenerate_strata(clean, "holds", ["pair"]), False)
    expect("constant/planted",
           constant_within_group([{"state": f"s{i%20}", "z": i % 20} for i in range(400)],
                                 "state", "z"), True)
    expect("constant/clean", constant_within_group(clean, "state", "feat"), False)
    return res


BASELINE = ROOT / "attacks/known_failing.json"


def ratchet(findings):
    """Block on REGRESSIONS, not on the backlog — and never let the backlog grow quietly.

    A gate that blocks every seat on day one is a gate every seat disables on day one. So a
    probe that already fails is recorded here with an owner and does not block; a probe that
    passes today must keep passing. Two things are therefore errors: a NEW failure, and a
    baseline entry that has started passing (the ratchet tightens, and a stale entry would let
    a real defect hide behind a name that is no longer accurate).
    """
    known = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    out, bad = [], 0
    for f in findings:
        if f.ok and f.check in known:
            out.append(Finding(f.check, False,
                               f"NOW PASSES but is still listed in known_failing.json "
                               f"(owner: {known[f.check].get('owner','?')}) — remove the entry; "
                               f"the ratchet only tightens"))
            bad += 1
        elif not f.ok and f.check in known:
            out.append(Finding(f.check + " [known]", True,
                               f"known-open, owner {known[f.check].get('owner','?')}: "
                               f"{known[f.check].get('note','')[:80]}"))
        else:
            out.append(f)
            bad += 0 if f.ok else 1
    return out, bad


def report(findings, header):
    print(f"\n{header}")
    for f in findings:
        print(f)
    return sum(1 for f in findings if not f.ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probes", action="store_true")
    ap.add_argument("--frame", nargs="+", metavar=("DIR", "PATTERN"))
    a = ap.parse_args()
    bad = 0
    if a.selftest:
        bad += report(selftest(), "POSITIVE CONTROL (each check vs a planted defect)")
    if a.probes:
        f, n = ratchet(run_probes())
        report(f, "REGISTRY PROBES (baseline-ratcheted)")
        bad += n
    if a.frame:
        bad += report(frame(a.frame[0], a.frame[1:]), "FRAME")
    if not (a.selftest or a.probes or a.frame):
        bad += report(selftest(), "POSITIVE CONTROL (each check vs a planted defect)")
        f, n = ratchet(run_probes())
        report(f, "REGISTRY PROBES (baseline-ratcheted)")
        bad += n
    print(f"\n{'ADMISSIBLE' if not bad else f'{bad} CHECK(S) FAILED'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
