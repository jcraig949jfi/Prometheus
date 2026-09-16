"""The rejected-scaffolding control (R18) with its own controls.

Pure: strip_accommodations removes exactly the accommodation tokens and nothing structural
(-O2, -I, -l, -m32, harness paths stay); CFLAGS='...' is rewritten in place.
Docker (skipped without docker): a synthetic body whose build needs -lm -- NOT an accommodation,
never stripped -- and carries a decorative -w: verdict NOT_REQUIRED (positive: the detector
says decorative when it is). A synthetic body that genuinely needs -fpermissive to compile:
verdict REQUIRED (cheat: the detector cannot be fooled into calling required scaffolding
decorative). A recipe whose own build fails: UNDECIDED, never REQUIRED.
"""
from __future__ import annotations

import io
import json
import tarfile

import pytest

from techne.fossils import record, scaffold_control as sc, vault, worlds

DOCKER = worlds.docker_available()


def test_strip_keeps_structure_and_removes_accommodations():
    s, r = sc.strip_accommodations("make -s CFLAGS='-O1 -fcommon -std=gnu89 -w' 2>&1 | tail -1")
    assert s.startswith("make -s CFLAGS='-O1' 2>&1") and sorted(r) == ["-fcommon", "-std=gnu89", "-w"]
    s, r = sc.strip_accommodations("gcc -w -std=gnu89 -o $BODY/rs rs.c -lm")
    assert s == "gcc -o $BODY/rs rs.c -lm" and sorted(r) == ["-std=gnu89", "-w"]
    s, r = sc.strip_accommodations("gcc -m32 -O2 -I$HARNESS -o x x.c")
    assert r == [] and s == "gcc -m32 -O2 -I$HARNESS -o x x.c"
    s, r = sc.strip_accommodations("make -s CFLAGS='-O2 -w -include cstring -fpermissive' 2>&1")
    assert "-include" not in s and "-fpermissive" not in s and "CFLAGS='-O2'" in s
    s, r = sc.strip_accommodations("make -s ADDONS=-fcommon 2>&1 | tail -3")
    assert r == ["ADDONS=-fcommon"] and "ADDONS" not in s


def _tar_bytes(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, data in files.items():
            ti = tarfile.TarInfo(name); ti.size = len(data); ti.mtime = 0
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


@pytest.fixture
def synth(tmp_path, monkeypatch):
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")

    def make(sid, src, build_cmd, run_cmd):
        up = vault.body_dir(sid) / "upstream"
        (up / "tree").mkdir(parents=True)
        (up / "tree" / "p.c").write_bytes(src)
        (up / "x.tar.gz").write_bytes(_tar_bytes({"x/p.c": src}))
        rows = vault.hash_tree(up); vault.write_hashes(sid, rows)
        rec = record.skeleton(sid, canonical_name=sid, lineage="x", era="1990",
                              human_capability_summary={"built_to": "x", "pressure": "y", "success_means": "z"})
        rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows)}
        record.save(rec)
        (vault.specimen_dir(sid) / "recipe.json").write_text(json.dumps({
            "runner": "docker", "image": "prometheus-fossil-c:bookworm", "workdir": "upstream/tree",
            "build": [build_cmd], "runs": [{"name": "run", "cmd": run_cmd, "expect": {"exit": 0, "stdout_contains": ["ok"]}}]}), encoding="utf-8")
        return sid
    return make


NEEDS_LM = b'#include <math.h>\n#include <stdio.h>\nint main(void){printf("ok %f\\n", sqrt(2.0));return 0;}\n'
# valid only with -fpermissive under g++: int* from void* without a cast
NEEDS_PERMISSIVE = b'#include <stdlib.h>\n#include <stdio.h>\nint main(void){int *p = malloc(4); *p = 1; printf("ok %d\\n", *p); free(p); return 0;}\n'


@pytest.mark.skipif(not DOCKER, reason="docker not reachable through WSL")
def test_positive_decorative_flag_is_not_required(synth):
    sid = synth("synth-decorative", NEEDS_LM, "gcc -w -std=gnu89 -o p p.c -lm", "./p")
    r = sc.control(sid, timeout=300)
    assert r["removed"] == ["-w", "-std=gnu89"] or sorted(r["removed"]) == ["-std=gnu89", "-w"]
    assert r["recipe_build_ok"] is True and r["stripped_build_ok"] is True and r["runs_ok"] is True
    assert r["verdict"] == "NOT_REQUIRED"


@pytest.mark.skipif(not DOCKER, reason="docker not reachable through WSL")
def test_cheat_required_flag_is_detected(synth):
    sid = synth("synth-required", NEEDS_PERMISSIVE, "g++ -fpermissive -w -x c++ -o p p.c", "./p")
    r = sc.control(sid, timeout=300)
    assert r["recipe_build_ok"] is True
    assert r["stripped_build_ok"] is False and r["verdict"] == "REQUIRED", r


@pytest.mark.skipif(not DOCKER, reason="docker not reachable through WSL")
def test_broken_recipe_is_undecided_not_required(synth):
    sid = synth("synth-broken", b"this is not C\n", "gcc -w -o p p.c", "./p")
    r = sc.control(sid, timeout=300)
    assert r["recipe_build_ok"] is False and r["verdict"] == "UNDECIDED"
