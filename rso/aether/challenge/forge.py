"""C-018-T040 forged evidence sets against the FROZEN completeness gate + record checks + analyser (confirm.py analyse).

Genuine units come from natives.py (Pallas's seeds). A forged shard has the right id, the right seed labels, the right
count and internally consistent digests; its rows beyond the first are COPIES of one genuine unit with the seed label
rewritten (arrays identical, arrays_sha256 identical, meta_sha256 recomputed). The design is built with the frozen
rso.completeness.manifest.build in the shape of the frozen design (6 shards: 4 x 12 RX, 2 x 8 V1) but on Pallas's seeds,
because the frozen design's seeds (k = 0x2000+i) may not be executed by this seat.

    build-dup6 <scratch> <out>        6-shard forged set; RX.3's FIRST row is a copy of another genuine unit (0x3002
                                      relabelled 0x3003): the one row the replay sample looks at
    analyse <out> [--stub-replay]     confirm.analyse() with RUNS / DESIGN_PATH / pin pointed at <out>; prints its JSON.
                                      --stub-replay replaces A.native_unit by the stored unit (witnesses whose line is
                                      independent of the replay: E3, E5) and is reported when used
    pin5 <scratch> <out>              5-shard design (V1.1 dropped) written OVER the frozen manifest, FROZEN.json's
                                      design pin and manifest hash rewritten to match, confirm.analyse() run by its real
                                      path (only RUNS redirected), then `freeze.mismatches()`; both files restored byte
                                      for byte and sha256-verified (also `git diff --quiet`)
    e3 <out>                          copy of <out> with one row's arrays_sha256 edited and the shard meta re-digested
    e5 <out>                          copy of <out> without V1.1 (5 of 6 shards presented)
"""
import contextlib
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

from rso.aether import adapter as A, confirm as C, freeze as FZ
from rso.completeness import manifest as M
from rso.registry.registry import ROOT, file_sha

LABEL0 = 0x3100                     # label-only seeds for copies (never executed)
GEN_RX = [0x3000, 0x3001, 0x3002, 0x3003]
GEN_V1 = [0x3000, 0x3001]


def plan6():
    out, lab = [], LABEL0
    for i, g in enumerate(GEN_RX):
        out.append(("RX.%d" % i, "RX", [g] + list(range(lab, lab + 11))))
        lab += 11
    for i, g in enumerate(GEN_V1):
        out.append(("V1.%d" % i, "V1", [g] + list(range(lab, lab + 7))))
        lab += 7
    return out


def genuine_path(scratch, law, k):
    return os.path.join(scratch, "units", "native_%s_%d" % (law, k))


def copy_unit(src, dst, seed):
    meta, arrays = A.load_unit(src)
    meta["seed"] = seed
    return A.save_unit(dst, meta, arrays)


def build(scratch, out, plan, substitute=None):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    specs = []
    for sid, law, ks in plan:
        d = os.path.join(out, sid)
        os.makedirs(d)
        src = genuine_path(scratch, law, (substitute or {}).get(sid, ks[0]))
        rows = []
        for k in ks:
            meta = copy_unit(src, os.path.join(d, "native_%s_%s" % (law, k)), k)
            rows.append({"law": law, "seed": k, "arrays_sha256": meta["arrays_sha256"], "meta_sha256": M.digest(meta)})
        with open(os.path.join(out, sid + ".shard.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(C.make_shard(sid, rows), f, sort_keys=True, indent=1)
        specs.append({"id": sid, "seeds": ks, "arm_counts": {law: len(ks)}, "rows": len(ks), "rows_sha256": "PENDING",
                      "meta_sha256": "PENDING"})
    design = M.build("PALLAS C-018-T040 forged evidence (shape of C-018-T030 v1.0.0; Pallas seeds)", arms=list(C.ARMS),
                     shards=specs, sources=C.current_sources(), row_key_fields=["law"], seed_field="seed", early_stop=None)
    with open(os.path.join(out, "design.manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(design, indent=1, sort_keys=True) + "\n")
    return design


def _stub_replay(out):
    def stub(law, k, **kw):
        p = glob.glob(os.path.join(out, "*", "native_%s_%d.json" % (law, k)))[0][:-5]
        return A.load_unit(p)
    A.native_unit = stub


def analyse(out, design_path=None, stub_replay=False):
    C.RUNS = out
    if design_path is not None:
        with open(design_path, encoding="utf-8") as f:
            design = json.load(f)
        C.DESIGN_PATH = design_path
        C.pinned_design_sha256 = lambda: design["manifest_sha256"]
    if stub_replay:
        _stub_replay(out)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.analyse()
    res = json.loads(buf.getvalue())
    res["rc"], res["replay_stubbed"] = rc, stub_replay
    if "laws" in res:
        for law in res["laws"]:
            res["laws"][law].pop("rows", None)
    return res


def distinct_arrays(out):
    shas = []
    for p in sorted(glob.glob(os.path.join(out, "*.shard.json"))):
        with open(p, encoding="utf-8") as f:
            shas += [r["arrays_sha256"] for r in json.load(f)["rows"]]
    return {"n_rows": len(shas), "n_distinct_arrays_sha256": len(set(shas))}


def pin5(scratch, out):
    design = build(scratch, out, plan6()[:5])
    man, frz = C.DESIGN_PATH, FZ.PATH
    raw_m, raw_f = open(man, "rb").read(), open(frz, "rb").read()
    sha_m, sha_f = hashlib.sha256(raw_m).hexdigest(), hashlib.sha256(raw_f).hexdigest()
    res = {"n_shards_in_forged_design": len(design["shards"]), "forged_design_sha256": design["manifest_sha256"]}
    try:
        with open(man, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(design, indent=1, sort_keys=True) + "\n")
        spec = json.loads(raw_f.decode("utf-8"))
        spec["design_manifest_sha256"] = design["manifest_sha256"]
        spec["files"]["rso/aether/manifests/confirm_design.manifest.json"] = file_sha("rso/aether/manifests/confirm_design.manifest.json", ROOT)
        with open(frz, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(spec, indent=1, sort_keys=True) + "\n")
        res["analyse"] = analyse(out)                     # the real path: pin read from FROZEN.json, design from DESIGN_PATH
        res["freeze_mismatches_while_mutated"] = FZ.mismatches()
    finally:
        open(man, "wb").write(raw_m)
        open(frz, "wb").write(raw_f)
    res["restored_sha256_ok"] = (hashlib.sha256(open(man, "rb").read()).hexdigest() == sha_m and
                                 hashlib.sha256(open(frz, "rb").read()).hexdigest() == sha_f)
    res["git_diff_quiet"] = subprocess.run(["git", "diff", "--quiet", "--", man, frz], cwd=ROOT).returncode == 0
    res["freeze_mismatches_after_restore"] = FZ.mismatches()
    res.update(distinct_arrays(out))
    return res


def e3(out):
    o3 = out + "_e3"
    if os.path.isdir(o3):
        shutil.rmtree(o3)
    shutil.copytree(out, o3)
    p = os.path.join(o3, "RX.1.shard.json")
    with open(p, encoding="utf-8") as f:
        sh = json.load(f)
    sh["rows"][1]["arrays_sha256"] = "f" * 64
    sh["meta"]["rows_sha256"] = M.digest(sh["rows"])
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sh, f, sort_keys=True, indent=1)
    return analyse(o3, os.path.join(o3, "design.manifest.json"), stub_replay=True)


def e5(out):
    o5 = out + "_e5"
    if os.path.isdir(o5):
        shutil.rmtree(o5)
    shutil.copytree(out, o5)
    os.remove(os.path.join(o5, "V1.1.shard.json"))
    return analyse(o5, os.path.join(o5, "design.manifest.json"), stub_replay=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build-dup6":
        d = build(sys.argv[2], sys.argv[3], plan6(), substitute={"RX.3": 0x3002})
        print(json.dumps({"design_sha256": d["manifest_sha256"], **distinct_arrays(sys.argv[3])}, indent=1))
    elif cmd == "analyse":
        out = sys.argv[2]
        r = analyse(out, os.path.join(out, "design.manifest.json"), stub_replay="--stub-replay" in sys.argv)
        r.update(distinct_arrays(out))
        print(json.dumps(r, indent=1, default=str))
    elif cmd == "pin5":
        print(json.dumps(pin5(sys.argv[2], sys.argv[3]), indent=1, default=str))
    elif cmd == "e3":
        print(json.dumps(e3(sys.argv[2]), indent=1, default=str))
    elif cmd == "e5":
        print(json.dumps(e5(sys.argv[2]), indent=1, default=str))
