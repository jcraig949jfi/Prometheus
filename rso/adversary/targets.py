"""Registered known-answer targets (C-019-T011). Every target is exercised on a SCRATCH COPY or an in-memory copy of evidence
from an earlier generation; no frozen file is opened for writing. A target is
    TARGETS[name] = {campaign, summary, source, variants: [(attack, variant_id, fn() -> core.Result)], not_applicable: {attack: why}}
and every attack must be either run or excused with a reason (core.run_variants refuses otherwise). To register a new
campaign's target see README.md "Registering a target".

    z80_completeness     C-017  rso.completeness.z80.verify_set on the six committed confirmatory shards (in memory)
    aether_confirm       C-018  rso.aether.confirm.analyse on a temp copy of rso/aether/runs/CONFIRM, with the native replay,
                                warm-snapshot and tree-replay stubs answering from the ORIGINAL committed runs (the pinned
                                native execution is not re-run: that is the Cadmus/Hestia D1 audit, not this kit)
    qualify_falsifiable  C-016/C-017  rso.qualify.falsifiable on miniatures of the historical defects
                                (rso/qualify/tests/test_falsifiable.py:21-92)
    reach_d1_analyze     C-013  rso.reach.analyze.analyze on the committed D1 ledger (rso/reach/runs/D1)
"""
import contextlib
import copy
import glob
import gzip
import json
import os
import shutil
import tempfile

from rso.adversary import attacks as X, core as K
from rso.registry.registry import ROOT

_CACHE = {}


def _once(key, make):
    if key not in _CACHE:
        _CACHE[key] = make()
    return _CACHE[key]


# ------------------------------------------------------------------------------------------------ C-017 Z80 completeness
def _z80():
    def make():
        from rso.completeness import z80 as Z
        man = Z.committed_manifest()
        return Z, man, Z.load_shards(Z.shard_paths()), Z.current_sources(man)
    return _once("z80", make)


def _z80_verdict(attacked, original, limitation=None):
    Z, man, _, src = _z80()
    res = Z.verify_set(man, attacked, src)
    kinds = sorted(res.kinds())
    note = "%s missing=%s kinds=%s" % (res.status, res.missing, kinds)
    return K.judge(res.licenses_verdict, note, X.fingerprint(attacked) != X.fingerprint(original), limitation)


def _z80_drop(i):
    def run():
        _, _, shards, _ = _z80()
        return _z80_verdict(X.drop(shards, i), shards)
    return run


def _z80_duplicate_shard():
    _, _, shards, _ = _z80()
    return _z80_verdict(X.duplicate(shards, src=1, dst=5), shards)        # six shards presented; CONFIRM.1-6 twice, 5-6 gone


def _z80_duplicate_row():
    _, _, shards, _ = _z80()
    out = copy.deepcopy(shards)
    out[0]["rows"] = X.duplicate(shards[0]["rows"], src=0, dst=-1)        # same row count, one row overwritten by another
    return _z80_verdict(out, shards)


def _z80_rewrite():
    Z, _, shards, _ = _z80()
    out = copy.deepcopy(shards)

    def rewrite(sh):
        sh[0]["rows"][0]["n_ENDO"] += 1                                   # a derived count in the first row

    def rebind(sh):
        sh[0]["meta"]["rows_sha256"] = Z.native_digest(sh[0]["rows"])    # the writer's own digest is made consistent again
    out = X.rewrite_derived(shards, rewrite, rebind)
    return _z80_verdict(out, shards)


def _z80_scrub():
    _, _, shards, _ = _z80()
    out = copy.deepcopy(shards)
    out[0]["rows"][0] = X.scrub_answer(shards[0]["rows"][0], ["gt"])      # the ground-truth label of one row
    return _z80_verdict(out, shards)


# ------------------------------------------------------------------------------------------------ C-018 Aether confirm
@contextlib.contextmanager
def _memo_decode():
    """Aether's content decoder (Aether/V2B/REACH01/R1/r1_reduce.decode via rso.aether.evaluate.decode) is a pure function of
    the stored features and takes ~17 s per call; memoise it on the features' fingerprint so repeated analyses of scratch
    copies whose features are unchanged cost seconds. Restored on exit; nothing is written."""
    from rso.aether import evaluate as E
    orig = E.decode
    memo = _CACHE.setdefault("decode_memo", {})

    def memoised(feats, null=False):
        key = (X.fingerprint(feats), null)
        if key not in memo:
            memo[key] = orig(feats, null=null)
        return copy.deepcopy(memo[key])
    E.decode = memoised
    try:
        yield
    finally:
        E.decode = orig


class _Aether:
    """A scratch copy of the committed CONFIRM runs plus the oracle stubs that answer from the untouched originals."""

    def __init__(self):
        from rso.aether import adapter as A, confirm as C
        self.A, self.C = A, C
        self.orig = C.RUNS
        self.units = {}
        self.dir = None

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="adversary_aether_")
        shutil.copytree(self.orig, self.dir, dirs_exist_ok=True)
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.dir, ignore_errors=True)

    # -- the original (oracle) side
    def stored(self, law, k, *_a, **_k):
        if (law, k) not in self.units:
            for sid in sorted(os.listdir(self.orig)):
                p = os.path.join(self.orig, sid, "native_%s_%d" % (law, k))
                if os.path.exists(p + ".json"):
                    self.units[(law, k)] = self.A.load_unit(p)
                    break
        return self.units[(law, k)]

    def snapshot(self, law, k, n, warm):
        m, a = self.stored(law, k)
        return list(a["snap"]), 0, m["origin"]

    def tree(self, law, k, n, warm, H):
        m, _ = self.stored(law, k)
        return {"tree": m["tree"], "origin": m["origin"], "warm_digest": m["aether"]["warm_digest"]}

    # -- the scratch side
    def shard_files(self):
        return sorted(glob.glob(os.path.join(self.dir, "*.shard.json")))

    def shard(self, sid):
        with open(os.path.join(self.dir, sid + ".shard.json"), encoding="utf-8") as f:
            return json.load(f)

    def shard_of(self, k):
        for p in self.shard_files():
            sid = os.path.basename(p)[:-len(".shard.json")]
            if any(r["seed"] == k for r in self.shard(sid)["rows"]):
                return sid
        raise KeyError(k)

    def write_shard(self, sid, rows):
        with open(os.path.join(self.dir, sid + ".shard.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.C.make_shard(sid, rows), f, sort_keys=True, indent=1)

    def replace_unit(self, k, meta, arrays):
        """Write (meta, arrays) as seed k's unit and make the shard row and shard meta consistent with it (the producer's
        rewrite: every simple invariant, every hash, bound again)."""
        from rso.completeness import manifest as M
        sid = self.shard_of(k)
        saved = self.A.save_unit(os.path.join(self.dir, sid, "native_RX_%d" % k), meta, arrays)
        rows = self.shard(sid)["rows"]
        for r in rows:
            if r["seed"] == k:
                r["arrays_sha256"], r["meta_sha256"] = saved["arrays_sha256"], M.digest(saved)
        self.write_shard(sid, rows)

    def analyse(self):
        got = []
        with _memo_decode():
            rc = K.call(self.C.analyse, runs=self.dir, replay=self.stored, snapshot=self.snapshot, tree_replay=self.tree,
                        freeze_check=lambda: [], emit=got.append)
        return rc, got[0]

    def first_seeds(self):
        return {self.shard(os.path.basename(p)[:-len(".shard.json")])["rows"][0]["seed"] for p in self.shard_files()}


def _aether_classes(out):
    return {(name, r["seed"]): r["cls"] for name, law in out["laws"].items() for r in law["rows"]}


def _aether_baseline():
    def make():
        with _Aether() as ae:
            rc, out = ae.analyse()
            assert rc == 0, out.get("problems") or out["completeness"]
            return _aether_classes(out)
    return _once("aether_baseline", make)


def _aether_note(rc, out):
    if rc == 3:
        c = out["completeness"]
        return "INCOMPLETE missing=%s" % c["missing"]
    if rc == 4:
        c = out.get("completeness", {})
        why = out.get("problems") or [f["kind"] + " " + str(f.get("shard")) for f in c.get("findings", [])] or [out.get("disposition")]
        return "REFUSED (%s) %s" % (out.get("disposition", c.get("status")), "; ".join(str(w) for w in why[:3]))
    return "verdict printed (rc 0)"


def _aether_verdict(ae, before_fp, limitation=None, seed=None):
    rc, out = ae.analyse()
    fired = _tree_state(ae) != before_fp
    accepted = rc == 0
    note = _aether_note(rc, out)
    if accepted and seed is not None:
        was, now = _aether_baseline().get(("RX", seed)), _aether_classes(out).get(("RX", seed))
        note = "verdict printed; unit %s class %s -> %s; no check failed" % (seed, was, now)
    return K.judge(accepted, note, fired, limitation)


def _tree_state(ae):
    return X.fingerprint([[os.path.relpath(p, ae.dir), open(p, "rb").read()] for p in sorted(
        [p for p in glob.glob(os.path.join(ae.dir, "**", "*.*"), recursive=True) if os.path.isfile(p)])])


def _aether_drop_shard():
    with _Aether() as ae:
        before = _tree_state(ae)
        files = ae.shard_files()
        os.remove((set(files) - set(X.drop(files, 1))).pop())
        return _aether_verdict(ae, before)


def _aether_drop_law():
    with _Aether() as ae:
        before = _tree_state(ae)
        for p in [p for p in ae.shard_files() if os.path.basename(p).startswith("V1.")]:
            os.remove(p)
        return _aether_verdict(ae, before)


def _aether_duplicate():
    with _Aether() as ae:
        before = _tree_state(ae)
        sid = "RX.0"
        rows = ae.shard(sid)["rows"]
        out = X.duplicate(rows, src=0, dst=1)                              # unit 8192's row overwrites unit 8193's
        for ext in (".json", ".npz"):
            shutil.copyfile(os.path.join(ae.dir, sid, "native_RX_%d%s" % (rows[0]["seed"], ext)),
                            os.path.join(ae.dir, sid, "native_RX_%d%s" % (rows[1]["seed"], ext)))
        out[1] = dict(out[1], seed=rows[1]["seed"])                        # the row keeps its own seed label, the bytes are 8192's
        ae.write_shard(sid, out)
        return _aether_verdict(ae, before)


def _aether_clamp(seed, limitation):
    def run():
        with _Aether() as ae:
            before = _tree_state(ae)
            sampled = seed in ae.first_seeds()
            meta, arrays = ae.A.load_unit(os.path.join(ae.dir, ae.shard_of(seed), "native_RX_%d" % seed))
            from rso.aether import evaluate as E
            _, _, targets = E._sites(meta)

            def rewrite(u):                                                # the non-ancestor clamp now removes every target
                for s in targets:
                    u["arrays"]["ftick_cutN"][s] = -1

            def rebind(u):
                u["meta"]["arrays_sha256"] = ae.A.arrays_sha256(u["arrays"])
            new = X.rewrite_derived({"meta": meta, "arrays": arrays}, rewrite, rebind)
            ae.replace_unit(seed, new["meta"], new["arrays"])
            return _aether_verdict(ae, before, limitation=None if sampled else limitation, seed=seed)
    return run


def _aether_scrub(mode, fields, edit=None):
    def run():
        with _Aether() as ae:
            before = _tree_state(ae)
            seed = 8201
            meta, arrays = ae.A.load_unit(os.path.join(ae.dir, ae.shard_of(seed), "native_RX_%d" % seed))
            ae.replace_unit(seed, X.scrub_answer(meta, fields, mode=mode), arrays)
            return _aether_verdict(ae, before)
    return run


# ------------------------------------------------------------------------------------------------ C-016 / C-017 falsifiability
def _origin_cases():
    return [({"origin": "INSERTED"}, "INSERTED")] * 240 + [({"origin": "ARISEN"}, "ARISEN")] * 24      # test_falsifiable.py:41-50


def _loose_rule(preds, truths):                                       # test_falsifiable.py:8-12 exact_rule(33): 33 errors allowed
    return sum(p != t for p, t in zip(preds, truths)) <= 33


def _tight_rule(preds, truths):                                       # test_falsifiable.py:14-19 per_class_rule(3)
    return all(sum(p != t for p, t in zip(preds, truths) if t == c) <= 3 for c in set(truths))


def _audit_note(rec):
    return "audit ok=%s; constant_passes=%s; cannot_discriminate=%s; oracle_fails=%s; reads_answer=%s; near_miss_wrong=%s" % (
        rec["ok"], rec["constant_passes"], rec["cannot_discriminate"], rec["oracle_fails"], rec["reads_answer"],
        rec["near_miss_wrong"])


_NEAR_MISS = [({"origin": "ARISEN"}, "ARISEN", "a minority-class ARISEN row")]


def _constant(rule):
    def run():
        from rso.qualify import falsifiable as F
        cases = _origin_cases()
        honest = lambda x: x["origin"]
        const = X.constant_detector("INSERTED")
        fired = [honest(x) for x, _ in cases] != [const(x) for x, _ in cases]
        rec = F.audit("origin-detector", const, rule, cases, ("INSERTED", "ARISEN"), must_discriminate=("ARISEN",),
                      near_misses=_NEAR_MISS)
        return K.judge(rec["ok"], _audit_note(rec), fired)
    return run


_TABLE = {"H_ENDO": "ENDO", "H_EXT": "EXT", "RECON": "ENV", "CDIST": "ENV"}                    # test_falsifiable.py:56


def _scrub_recipe():
    from rso.qualify import falsifiable as F
    cases = [({"arm": a, "bytes": i}, t) for i, (a, t) in enumerate(_TABLE.items())]
    lookup = lambda x: _TABLE.get(x["arm"], "OTHER")                                              # the recipe LOOKUP TABLE
    scrub = lambda x: X.scrub_answer(x, ["arm"], mode="corrupt")
    fired = all(scrub(x) != x for x, _ in cases)
    idx = F.reads_answer(lookup, cases, scrub)
    rec = F.audit("recipe-lookup", lookup, lambda p, t: list(p) == list(t), cases, ("ENDO", "EXT", "ENV"), scrub=scrub,
                  near_misses=[({"arm": "RECON", "bytes": 2}, "ENV", "a recipe-keyed row")])
    return K.judge(rec["ok"], "reads_answer flagged cases %s; %s" % (idx, _audit_note(rec)), fired)


def _drop_near_misses():
    from rso.qualify import falsifiable as F
    cases = [({"v": 0}, "A"), ({"v": 1}, "B")]
    det = lambda x: "AB"[x["v"]]
    kept = [({"v": 1}, "B", "looks like A")]
    attacked = X.drop(kept, 0)                                                                    # no near-miss registered any more
    rec = K.call(F.audit, "sound-control", det, lambda p, t: list(p) == list(t), cases, ("A", "B"), must_discriminate=("A", "B"),
                  scrub=lambda x: dict(x), near_misses=attacked)
    return K.judge(rec["ok"], _audit_note(rec), X.fingerprint(attacked) != X.fingerprint(kept))


# ------------------------------------------------------------------------------------------------ C-013 D1 analyzer
def _d1():
    from rso.reach import analyze as AN
    rows, meta = AN.load(os.path.join(ROOT, "rso", "reach", "runs", "D1"))
    return AN, rows, meta


def _d1_drop():
    AN, rows, meta = _d1()
    out = AN.analyze(X.drop(rows, 0), meta)                                                       # one cell of round 0
    base = AN.analyze(rows, meta)
    return K.judge(out["status"] == "ANALYZED", "status %s after the drop (%s before); rounds_completed %s -> %s" % (
        out["status"], base["status"], base["rounds_completed"], out["rounds_completed"]), out != base)


def _d1_tamper(rows, how):
    i = next(i for i, r in enumerate(rows) if r["discovery"])
    new = copy.deepcopy(rows)
    if how == "contradict":
        new[i]["certificate"] = dict(new[i]["certificate"], certified=False, oracle_agrees=False)   # components say: no discovery
    else:
        del new[i]["certificate"]
    return new


def _d1_variant(how):
    def run():
        from rso.qualify import falsifiable as F
        AN, rows, meta = _d1()
        tamper = lambda rs: _d1_tamper(rs, how)
        unchanged = F.trusts_derived(lambda rs: AN.analyze(rs, meta), rows, tamper)
        return K.judge(unchanged, "analyze output %s after the certificate was %s while row['discovery'] stayed True" % (
            "UNCHANGED" if unchanged else "changed", "contradicted" if how == "contradict" else "removed"),
            X.fingerprint(tamper(rows)) != X.fingerprint(rows), "C013-D1-trusts-derived")
    return run


TARGETS = {
    "z80_completeness": {
        "campaign": "C-017", "source": "rso/completeness/verify.py:79 (verify); rso/completeness/z80.py:86 (verify_set)",
        "summary": "six committed Z80 confirmatory shards through rso.completeness verify()",
        "variants": ([("DROP", "shard-%d" % i, _z80_drop(i)) for i in range(6)]
                     + [("DUPLICATE", "shard", _z80_duplicate_shard), ("DUPLICATE", "row", _z80_duplicate_row),
                        ("REWRITE_DERIVED", "n_ENDO+rebound-meta", _z80_rewrite), ("SCRUB_ANSWER", "gt-removed", _z80_scrub)]),
        "not_applicable": {"CONSTANT": "verify() checks presence, bytes, counts and seed partitions; it contains no detector "
                                       "to replace with a constant"},
    },
    "aether_confirm": {
        "campaign": "C-018", "source": "rso/aether/confirm.py:169 (analyse); rso/aether/RESULT.md:28 (R1c)",
        "summary": "64 committed Aether confirmatory units through confirm.analyse (scratch copy, oracle stubs)",
        "variants": [("DROP", "shard", _aether_drop_shard), ("DROP", "law-V1", _aether_drop_law),
                     ("DUPLICATE", "unit-8192-over-8193", _aether_duplicate),
                     ("REWRITE_DERIVED", "clamp-non-sampled-8201", _aether_clamp(8201, "C018-R1c")),
                     ("REWRITE_DERIVED", "clamp-sampled-8228", _aether_clamp(8228, "C018-R1c")),
                     ("SCRUB_ANSWER", "tree-removed", _aether_scrub("remove", ["tree"])),
                     ("SCRUB_ANSWER", "B-corrupted", _aether_scrub("corrupt", ["B"]))],
        "not_applicable": {"CONSTANT": "confirm.analyse has no detector under attack; Aether's content decoder is audited in "
                                       "rso/aether/qual/FALSIFIABILITY_AUDIT.json with rso.qualify (CONSTANT is that target's)"},
    },
    "qualify_falsifiable": {
        "campaign": "C-016/C-017", "source": "rso/qualify/falsifiable.py:22-74; rso/qualify/tests/test_falsifiable.py:41-72",
        "summary": "miniatures of the historical control defects through rso.qualify.falsifiable.audit",
        "variants": [("CONSTANT", "always-INSERTED vs loose rule", _constant(_loose_rule)),
                     ("CONSTANT", "always-INSERTED vs tight rule", _constant(_tight_rule)),
                     ("SCRUB_ANSWER", "recipe-table-arm-corrupted", _scrub_recipe),
                     ("DROP", "near-miss-set", _drop_near_misses)],
        "not_applicable": {"DUPLICATE": "audit() takes plain cases and has no count or identity contract to violate",
                           "REWRITE_DERIVED": "no derived evidence: the audit's inputs are the cases (the D1 derived-field "
                                              "case is target reach_d1_analyze)"},
    },
    "reach_d1_analyze": {
        "campaign": "C-013", "source": "rso/reach/analyze.py:39-100; rso/qualify/falsifiable.py:49 (trusts_derived)",
        "summary": "270 committed D1 ledger rows through rso.reach.analyze.analyze",
        "variants": [("DROP", "cell-of-round-0", _d1_drop),
                     ("REWRITE_DERIVED", "certificate-contradicted", _d1_variant("contradict")),
                     ("SCRUB_ANSWER", "certificate-removed", _d1_variant("remove"))],
        "not_applicable": {"DUPLICATE": "not exercised: a duplicated lineage inside one (arm, d) cell is a different question "
                                        "(row identity), see README 'Surfaces not exercised'",
                           "CONSTANT": "analyze() contains no detector; the certifier is a separate component (rso/reach/certify.py)"},
    },
}
