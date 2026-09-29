"""Controls-only selftest for holdout D2's firewall machinery. NEVER touches the hidden set or its key.

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2 [--write]

Everything runs on THROWAWAY material in a temp directory outside every repo: a throwaway hidden set made
of PUBLIC worlds of the unchanged holdout-D family (holdout D's DEMO world, its history-free control and
one fixed lattice point), a throwaway key and salt, throwaway prediction packages. Certificates use
reduced sizes (they test plumbing, not science). Each check has an injected-defect negative control that
must make it FAIL. --write saves SELFTEST_D2.json (booleans only) beside this file.
If the real public artifacts (MANIFEST_D2.json, hidden_D2.enc) exist, their PUBLIC consistency is also
checked (spec_id, sha256 of the ciphertext, family source hash) -- without the key.
"""
from __future__ import annotations

import os

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 selftest: set COSMOS_BROKER=1 (broker only)")

import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3_holdout_D import medium
from prometheus.cosmos.c3_holdout_D2 import draw, protocol, runner, sealbox, verify_reveal

HERE = Path(__file__).resolve().parent
PUBLIC_WORLDS = [
    medium.World(V=3, k=4, L=16, D=0.2, v=0.5, p_decay=0.03, kappa=0.1, q=1.0, sigma=0.2,
                 x_in=0, d_patch=4, w_patch=2),                      # holdout D selftest DEMO world
    medium.CONTROL_HISTORY_FREE,                                     # holdout D history-free control
    medium.World(V=2, k=2, L=12, D=0.05, v=0.25, p_decay=0.1, kappa=0.0, q=2.0, sigma=0.05,
                 x_in=0, d_patch=2, w_patch=2),                      # a fixed public lattice point
]
PUBLIC_SEEDS = [1414213562, 1732050807, 2023456789]
SMALL = {"E_train": 200, "E_test": 300, "n_perm": 5}

DUMMY_PREDICTOR = '''
import numpy as np
from prometheus.cosmos.c3.system import rollout
from prometheus.cosmos.c3.task import batch


def predict(system, task, seed):
    rng = np.random.default_rng(seed)
    cues, obs = batch(task, 16, rng)
    r = rollout(system, obs, rng, record=(task.k + 1,))
    mass = float(np.abs(r["states"][task.k + 1]).sum())
    cls = "PASSIVE" if mass > 1e-9 else "NONE"
    return {"class": cls, "intervention": {"class": "NONE", "delta_J": 0.0},
            "note": "selftest dummy", "feature_dim": int(r["features"].shape[1])}
'''

SNOOPER_PREDICTOR = '''
KNOB_WORDS = ("p_decay", "kappa", "d_patch", "w_patch", "x_in", "sigma")


def predict(system, task, seed):
    leak = False
    for a in ("w", "world", "_w", "knobs", "n_sub", "patch", "dt"):
        if hasattr(system, a):
            leak = True
    txt = str(getattr(system, "name", "")) + repr(vars(system)) + repr(dir(system))
    if any(k in txt for k in KNOB_WORDS):
        leak = True
    return {"class": "NONE", "intervention": {"class": "NONE"}, "leak": leak}
'''

OS_IMPORTER = '''
import os


def predict(system, task, seed):
    return {"class": "NONE", "intervention": {"class": "NONE"}, "cwd": os.getcwd()}
'''


def make_package(path: Path, src: str, intervention=None) -> str:
    meta = {"format": runner.PACKAGE_FORMAT, "entry": "predictor.py",
            "adjudication": {"rule": "selftest: none adjudicated"},
            "intervention": intervention or {"knob": "p_decay", "to": 1.0}}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("package.json", json.dumps(meta, sort_keys=True))
        z.writestr("predictor.py", src)
    path.write_bytes(buf.getvalue())
    return sealbox.sha256_hex(buf.getvalue())


def make_throwaway_set(tmp: Path) -> dict:
    fam = sealbox.src_sha_lf(draw.D_DIR / "medium.py")
    nonce = "00" * 32                                                # throwaway, public
    plain = draw.build_plaintext([w.as_dict() for w in PUBLIC_WORLDS], PUBLIC_SEEDS, nonce,
                                 "selftest", 0, fam)
    sd, pd = tmp / "secrets", tmp / "public"
    pd.mkdir(parents=True)
    m = draw.seal(plain, sd, pd, "selftest", len(PUBLIC_WORLDS), fam)
    return {"manifest": pd / draw.MANIFEST_NAME, "enc": pd / draw.ENC_NAME, "key": sd / draw.KEY_NAME,
            "salt": sd / draw.SALT_NAME, "plain": sd / draw.PLAIN_NAME, "m": m}


def new_run(ts, pkg, sha, out, **kw):
    return runner.FirewallRun(ts["manifest"], ts["enc"], kcopy(ts), pkg, sha, out, delete_key=True,
                              certify_kwargs=SMALL, predict_timeout=300, runner_id="selftest", enforce_run_dir=False,
                              secret_paths=(), verify_loaded=False, **kw)


# ------------------------------------------------------------------ check A: end to end
def receipts_ok(path: Path, n: int) -> bool:
    """Chain verifies; open < every prediction < seal < every certify < close; one of each per world;
    no knob-bearing world JSON or run seed appears in the file."""
    ok, recs, _why = runner.verify_receipts(path)
    if not ok:
        return False
    kinds = [r["kind"] for r in recs]
    if kinds.count("predictions_sealed") != 1 or kinds[0] != "open" or kinds[-1] != "close":
        return False
    s = kinds.index("predictions_sealed")
    if sorted(r["body"]["i"] for r in recs[:s] if r["kind"] == "prediction") != list(range(n)):
        return False
    if sorted(r["body"]["i"] for r in recs[s:] if r["kind"] == "certify") != list(range(n)):
        return False
    if any(k == "prediction" for k in kinds[s:]) or any(k == "certify" for k in kinds[:s]):
        return False
    text = path.read_text(encoding="utf-8")
    worlds = [sealbox.canon_bytes(w.as_dict()).decode() for w in PUBLIC_WORLDS]
    if any(w in text for w in worlds) or '"p_decay":' in text:
        return False
    nums = set(re.findall(r"(?<![0-9a-fA-F.])[0-9]+(?![0-9a-fA-F.])", text))
    return not ({str(s) for s in PUBLIC_SEEDS} & nums)


def check_end_to_end(tmp: Path, ts: dict) -> dict:
    pkg = tmp / "dummy.zip"
    sha = make_package(pkg, DUMMY_PREDICTOR)
    out = tmp / "run_e2e"
    run = new_run(ts, pkg, sha, out)
    run.open()
    run.predict_all()
    run.seal_predictions()
    run.certify_all()
    res = run.close()
    rp = out / "receipts.jsonl"
    preds_ok = all(r["body"]["status"] == "OK" for r in run.receipts.records if r["kind"] == "prediction")
    good = bool(receipts_ok(rp, len(PUBLIC_WORLDS)) and preds_ok and res["chain_head"] == run.receipts.head
                and len(res["per_world"]) == len(PUBLIC_WORLDS)
                and all(p["base_class"] in runner.CLASSES for p in res["per_world"]))
    # negative control 1: tamper a certify body on a copy (chain must break)
    lines = rp.read_text(encoding="utf-8").splitlines()
    t1 = tmp / "tampered.jsonl"
    j = next(n for n, l in enumerate(lines) if '"kind":"certify"' in l)
    rec = json.loads(lines[j])
    rec["body"]["base"]["class"] = "FUNCTIONAL" if rec["body"]["base"]["class"] != "FUNCTIONAL" else "NONE"
    lines2 = list(lines)
    lines2[j] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    t1.write_text("\n".join(lines2) + "\n", encoding="utf-8", newline="\n")
    # negative control 2: a correctly re-chained copy that LEAKS a world's knobs
    t2 = tmp / "leaky.jsonl"
    t2.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8", newline="\n")
    recs = [json.loads(l) for l in lines]
    r2 = runner.Receipts.__new__(runner.Receipts)
    r2.path, r2.genesis, r2.records = t2, recs[0]["prev"], recs[:-1]
    r2.append("note", {"world": PUBLIC_WORLDS[0].as_dict()})
    r2.append("close", recs[-1]["body"])
    # negative control 3: certify recorded BEFORE the seal (re-chained, so only ordering is wrong)
    t3 = tmp / "early.jsonl"
    s = next(n for n, r in enumerate(recs) if r["kind"] == "predictions_sealed")
    c = next(n for n, r in enumerate(recs) if r["kind"] == "certify")
    order = recs[:s] + [recs[c]] + [recs[s]] + [r for n, r in enumerate(recs) if n > s and n != c]
    t3.write_text("", encoding="utf-8")
    r3 = runner.Receipts.__new__(runner.Receipts)
    r3.path, r3.genesis, r3.records = t3, recs[0]["prev"], []
    for r in order:
        r3.append(r["kind"], r["body"])
    return {"pass": good,
            "neg_tampered": receipts_ok(t1, len(PUBLIC_WORLDS)),
            "neg_leaky": receipts_ok(t2, len(PUBLIC_WORLDS)),
            "neg_certify_before_seal_in_file": receipts_ok(t3, len(PUBLIC_WORLDS))}


# ------------------------------------------------------------------ check B: hash mismatch refusal
def refuses_bad_package(tmp: Path, ts: dict, tag: str) -> bool:
    pkg = tmp / ("pkg_%s.zip" % tag)
    sha = make_package(pkg, DUMMY_PREDICTOR)
    refusals = 0
    wrong = ("0" if sha[0] != "0" else "1") + sha[1:]
    for n, (p, h) in enumerate([(pkg, wrong), (None, sha)]):
        if p is None:                                             # right hash, one flipped byte in the zip
            b = bytearray(pkg.read_bytes())
            b[len(b) // 2] ^= 0x01
            p = tmp / ("pkg_%s_flipped.zip" % tag)
            p.write_bytes(bytes(b))
        out = tmp / ("run_hash_%s_%d" % (tag, n))
        try:
            new_run(ts, p, h, out).open()
        except runner.PackageHashMismatch:
            refusals += int(not (out / "receipts.jsonl").exists())
        except Exception:                                         # noqa: BLE001 -- any other outcome = no refusal
            pass
    return refusals == 2


def check_hash_mismatch(tmp: Path, ts: dict) -> dict:
    good = refuses_bad_package(tmp, ts, "real")
    orig = runner.load_package

    def defect_loader(zip_path, expected, extract_to, allow_flagged=False):   # injected defect: no hash check
        return orig(zip_path, sealbox.sha256_file(zip_path), extract_to, allow_flagged)
    runner.load_package = defect_loader
    try:
        bad = refuses_bad_package(tmp, ts, "defect")
    finally:
        runner.load_package = orig
    return {"pass": good, "neg": bad}


# ------------------------------------------------------------------ check C: certify-before-predictions
class DefectNoGate(runner.FirewallRun):
    """Injected defect: the order gate is removed and the phase is forced."""
    def _gate(self, i):
        return None

    def certify_world(self, i):
        self.phase = "SEALED"
        return super().certify_world(i)


def refuses_early_certify(tmp: Path, ts: dict, cls, tag: str) -> bool:
    pkg = tmp / ("pkg_order_%s.zip" % tag)
    sha = make_package(pkg, DUMMY_PREDICTOR)
    refused = []
    # C1: certify right after open (no predictions at all)
    r = cls(ts["manifest"], ts["enc"], kcopy(ts), pkg, sha, tmp / ("ord1_" + tag), certify_kwargs=SMALL,
            runner_id="selftest", enforce_run_dir=False, secret_paths=(), verify_loaded=False, delete_key=True)
    r.open()
    try:
        r.certify_world(0)
        refused.append(False)
    except runner.OrderViolation:
        refused.append(True)
    # C2: predictions for all but the last world -> seal and certify both refused
    r = cls(ts["manifest"], ts["enc"], kcopy(ts), pkg, sha, tmp / ("ord2_" + tag), certify_kwargs=SMALL,
            runner_id="selftest", enforce_run_dir=False, secret_paths=(), verify_loaded=False, delete_key=True)
    r.open()
    try:
        for i in range(r.N - 1):
            r.receipts.append("prediction", dict(r._predict_one(i, r.predictor_seed(i)), i=i,
                                                 world_tag=r._tags[i]))
    finally:
        r._stop_worker()
    ok2 = True
    try:
        r.seal_predictions()
        ok2 = False
    except runner.OrderViolation:
        pass
    try:
        r.certify_world(0)
        ok2 = False
    except runner.OrderViolation:
        pass
    refused.append(ok2)
    # C3: full predictions + seal, then one prediction line is deleted ON DISK -> certify refused
    r = cls(ts["manifest"], ts["enc"], kcopy(ts), pkg, sha, tmp / ("ord3_" + tag), certify_kwargs=SMALL,
            runner_id="selftest", enforce_run_dir=False, secret_paths=(), verify_loaded=False, delete_key=True)
    r.open()
    r.predict_all()
    r.seal_predictions()
    lines = r.receipts.path.read_text(encoding="utf-8").splitlines()
    k = next(n for n, l in enumerate(lines) if '"kind":"prediction"' in l)
    r.receipts.path.write_text("\n".join(lines[:k] + lines[k + 1:]) + "\n", encoding="utf-8", newline="\n")
    try:
        r.certify_world(0)
        refused.append(False)
    except runner.OrderViolation:
        refused.append(True)
    return all(refused)


def check_order(tmp: Path, ts: dict) -> dict:
    return {"pass": refuses_early_certify(tmp, ts, runner.FirewallRun, "real"),
            "neg": refuses_early_certify(tmp, ts, DefectNoGate, "defect")}


# ------------------------------------------------------------------ check D: commitment round trip
def check_commitment(tmp: Path, ts: dict) -> dict:
    plain, m, ct = ts["plain"].read_bytes(), ts["m"], ts["enc"].read_bytes()
    salt = sealbox.read_hex_file(ts["salt"], 32)
    key = sealbox.read_hex_file(ts["key"], 32)
    good = verify_reveal.verify(plain, salt, key, m, ct)["all_ok"]
    flip = lambda b: bytes([b[0] ^ 1]) + b[1:]                      # noqa: E731
    negs = {
        "wrong_salt": verify_reveal.verify(plain, flip(salt), key, m, ct)["all_ok"],
        "flipped_plaintext": verify_reveal.verify(plain[:-2] + bytes([plain[-2] ^ 1]) + plain[-1:], salt, key,
                                                  m, ct)["all_ok"],
        "flipped_ciphertext": verify_reveal.verify(plain, salt, key, m, flip(ct))["all_ok"],
        "wrong_key": verify_reveal.verify(plain, salt, flip(key), m, ct)["all_ok"],
        "edited_manifest": verify_reveal.verify(plain, salt, key, dict(m, n_worlds=m["n_worlds"] + 1), ct)["all_ok"],
    }
    # redraw round trip on a throwaway PUBLIC nonce (4 lattice worlds; not the hidden set)
    fam = m["family_src_sha256"]
    nonce = "5e1f7e57" * 8
    w, s, rej = draw.draw_hidden(nonce, 4, draw.exposed_d_worlds())
    p2 = draw.build_plaintext(w, s, nonce, "selftest", rej, fam)
    m2 = draw.seal(p2, tmp / "secrets_redraw", _mk(tmp / "public_redraw"), "selftest", 4, fam)
    ct2 = (tmp / "public_redraw" / draw.ENC_NAME).read_bytes()
    s2 = sealbox.read_hex_file(tmp / "secrets_redraw" / draw.SALT_NAME, 32)
    k2 = sealbox.read_hex_file(tmp / "secrets_redraw" / draw.KEY_NAME, 32)
    redraw_good = verify_reveal.verify(p2, s2, k2, m2, ct2, redraw=True)
    obj = json.loads(p2)
    obj["run_seeds"][0] += 1
    fake = sealbox.canon_bytes(obj)                                  # a consistent but NOT-redrawn set
    redraw_neg = verify_reveal.verify(fake, s2, k2, m2, ct2, redraw=True)["redraw_from_nonce_ok"]
    return {"pass": bool(good and redraw_good["all_ok"] and redraw_good["redraw_from_nonce_ok"]),
            "negs": dict(negs, altered_seed_redraw=redraw_neg)}


def _mk(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


# ------------------------------------------------------------------ check E: predictor isolation + audit
def check_isolation(tmp: Path, ts: dict) -> dict:
    pkg = tmp / "snoop.zip"
    sha = make_package(pkg, SNOOPER_PREDICTOR)
    r = new_run(ts, pkg, sha, tmp / "run_snoop", allow_flagged=True)
    r.open()
    r.predict_all()
    preds = [x["body"] for x in r.receipts.records if x["kind"] == "prediction"]
    good = bool(len(preds) == len(PUBLIC_WORLDS) and all(p["status"] == "OK" for p in preds)
                and not any(p["prediction"]["leak"] for p in preds))
    ns = {}
    exec(compile(SNOOPER_PREDICTOR, "snooper", "exec"), ns)          # injected defect: raw system in-process
    bad = not ns["predict"](medium.ReactiveChannel(PUBLIC_WORLDS[0]), PUBLIC_WORLDS[0].task(), 0)["leak"]
    return {"pass": good, "neg": bad}


def check_audit(tmp: Path, ts: dict) -> dict:
    pkg = tmp / "osimp.zip"
    sha = make_package(pkg, OS_IMPORTER)

    def refused(allow):
        try:
            runner.load_package(pkg, sha, tmp / ("audit_%s" % allow), allow_flagged=allow)
            return False
        except runner.PackageAuditRefusal:
            return True
    return {"pass": refused(False), "neg": refused(True)}


def public_artifacts() -> dict:
    mp_, ep = HERE / draw.MANIFEST_NAME, HERE / draw.ENC_NAME
    if not (mp_.exists() and ep.exists()):
        return {}
    m = json.loads(mp_.read_text(encoding="utf-8"))
    return {"real_manifest_spec_id_ok": sealbox.manifest_spec_id(m) == m["spec_id"],
            "real_ciphertext_sha256_ok": sealbox.sha256_file(ep) == m["ciphertext_sha256"],
            "real_family_src_sha256_ok": sealbox.src_sha_lf(draw.D_DIR / "medium.py") == m["family_src_sha256"],
            "real_n_worlds_ge_128": m["n_worlds"] >= 128}


_KC = [0]


def kcopy(ts):
    """v2: a per-run copy of the THROWAWAY key, deleted by the runner right after reading (delete_key=True), so the
    child isolation probe finds no readable key -- exactly the production path."""
    _KC[0] += 1
    p = Path(ts["key"]).with_name("key_copy_%d.hex" % _KC[0])
    p.write_bytes(Path(ts["key"]).read_bytes())
    return p


class GateStandIn:
    """TEST CODE ONLY. These checks exercise the runner machinery AFTER the protocol gates, with many throwaway
    packages (a real prediction commitment binds exactly one). The real gates -- seal < audit < commitment <
    designation < result seal, stale-audit, host and runner checks -- are exercised end to end, runner included,
    in selftest_protocol.py. The runner CLI has no way to install this stand-in."""
    RunnerNotDesignated = protocol.RunnerNotDesignated
    RunParamsMismatch = protocol.RunParamsMismatch
    DEFAULT_ALLOWLIST = False

    def __init__(self, spec_id: str):
        self.spec_id = spec_id

    def check_gates(self, *a, **k):
        return {"spec_id": self.spec_id, "ref": "selftest-gate-stand-in"}


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="c3D2_selftest_") as t:
        tmp = Path(t)
        assert not runner.inside_git_repo(tmp)
        ts = make_throwaway_set(tmp)
        real_protocol, runner.protocol = runner.protocol, GateStandIn(ts["m"]["spec_id"])
        try:
            a = check_end_to_end(tmp, ts)
            b = check_hash_mismatch(tmp, ts)
            c = check_order(tmp, ts)
            d = check_commitment(tmp, ts)
            e = check_isolation(tmp, ts)
            f = check_audit(tmp, ts)
        finally:
            runner.protocol = real_protocol
    checks = {"runner_end_to_end": a["pass"], "hash_mismatch_refused": b["pass"],
              "certify_before_predictions_refused": c["pass"], "commitment_round_trip": d["pass"],
              "predictor_sees_no_knobs": e["pass"], "audit_refuses_forbidden_import": f["pass"]}
    checks.update(public_artifacts())
    negs = {"runner_end_to_end[tampered_receipt]": a["neg_tampered"],
            "runner_end_to_end[knob_leak_in_receipts]": a["neg_leaky"],
            "runner_end_to_end[certify_before_seal_in_file]": a["neg_certify_before_seal_in_file"],
            "hash_mismatch_refused[DefectNoHashCheck]": b["neg"],
            "certify_before_predictions_refused[DefectNoGate]": c["neg"],
            "predictor_sees_no_knobs[DefectRawSystemInProcess]": e["neg"],
            "audit_refuses_forbidden_import[allow_flagged]": f["neg"]}
    negs.update({"commitment_round_trip[%s]" % k: v for k, v in d["negs"].items()})
    res = {"checks": checks, "negative_controls_must_be_false": negs,
           "hidden_set_or_key_touched": False,
           "all_checks_true": all(checks.values()), "all_negative_controls_false": not any(negs.values())}
    res["selftest_pass"] = bool(res["all_checks_true"] and res["all_negative_controls_false"])
    return res


if __name__ == "__main__":
    out = run()
    txt = json.dumps(out, indent=1, sort_keys=True)
    if "--write" in sys.argv:
        (HERE / "SELFTEST_D2.json").write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(txt)
    sys.exit(0 if out["selftest_pass"] else 1)
