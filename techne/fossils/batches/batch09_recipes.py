"""Batch 09 recipes + harnesses (2026-09-13). python -m techne.fossils.batches.batch09_recipes
Each runs in the disposable work/ copy; deviations in each recipe's notes."""
from __future__ import annotations

import json
from .. import vault

LANG = "prometheus-fossil-lang:bookworm"
R = {}
H = {}

# ---- avida UNLOCK (charter P1/P5): builds offline from the now-complete body -------------------
# The image already ships cmake/g++/make and libs/apto is preserved IN the body at the commit the
# superproject pins, so this recipe fetches NOTHING from the network -- that is the whole point of
# the P1 repair. AVIDA_DISABLE_BACKTRACE=1 avoids backward-cpp's libbfd probe;
# CMAKE_POLICY_VERSION_MINIMUM=3.5 is needed because the tree's cmake_minimum_required predates
# 2.8.12 and modern CMake refuses it. Neither changes avida's own source.
R["avida"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "toolchain present without apt", "cmd": "cmake --version | head -1; g++ --version | head -1"},
              {"name": "pinned submodule is IN the body (the P1 repair)",
               "cmd": "echo apto=$(find libs/apto -type f | wc -l) backward_cpp=$(find libs/backward-cpp -type f | wc -l); test $(find libs/apto -type f | wc -l) -gt 50"}],
    "build": [{"name": "cmake + make avida (offline; apto from the preserved body)",
               "cmd": "export AVIDA_DISABLE_BACKTRACE=1; mkdir -p cbuild && cd cbuild && "
                      "cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release .. >/tmp/cmake.log 2>&1 && "
                      "make -j4 avida >/tmp/make.log 2>&1; test -x ./bin/avida && echo BUILT || { tail -20 /tmp/make.log; false; }",
               "timeout": 2400}],
    "runs": [{"name": "evolve a population from the hand-written ancestor for 300 updates (self-replication + descent)",
              "cmd": "W=$(pwd); cp -r avida-core/support/config /tmp/run && cd /tmp/run && "
                     "sed -i 's/^u 100000 Exit/u 300 Exit/' events.cfg && "
                     "$W/cbuild/bin/avida -c avida.cfg > /tmp/run.log 2>&1; "
                     "L=$(grep '^UD:' /tmp/run.log | tail -1); echo \"FINAL $L\"; "
                     "O=$(echo \"$L\" | sed 's/.*Orgs: *//;s/ *$//'); G=$(echo \"$L\" | sed 's/.*Gen: *//;s/ .*//'); "
                     "B=$(grep -v '^#' data/count.dat | tail -1 | awk '{print $4}'); echo \"ORGS=$O GEN=$G BIRTHS=$B\"; "
                     "awk -v o=\"$O\" -v g=\"$G\" -v b=\"$B\" 'BEGIN{print (o>100 && g>5 && b>100) ? \"SELF_REPLICATING_POPULATION=yes\" : \"SELF_REPLICATING_POPULATION=no\"}'",
              "expect": {"exit": 0, "stdout_contains": ["SELF_REPLICATING_POPULATION=yes"]}, "timeout": 1200}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: from ONE hand-written ancestor genome (default-heads.org) the population must "
             "self-replicate and show descent -- >100 organisms, mean generation >5, >100 births by "
             "update 300. Observed 1068 orgs, generation 22.96, 808 births. tasks.dat stays all-zero "
             "at 300 updates (the logic-task rewards need far longer runs); that is recorded, not "
             "interpreted. This fossil SEGFAULTED for an entire batch while libs/apto was an empty "
             "directory in the body; it builds and runs only because the submodule is now preserved "
             "at the superproject's pinned commit. Nothing in avida's source was modernised."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid); d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "+harness" if sid in H else "")


if __name__ == "__main__":
    main()
