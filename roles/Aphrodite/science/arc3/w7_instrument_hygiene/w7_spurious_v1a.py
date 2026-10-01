"""W7: score every ORIGINAL W2 4M first hit in W7_SPURIOUS.json with T4 v1 and
the v1a draft (direct scoring, validated in W7_DIRECT_VALIDATION.json), and
classify why v1 rejects it. Writes W7_SPURIOUS_V1A.json. Single core, ~1 min."""
import json
from w7_common import *              # noqa: F401,F403
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402

a18.worker_init()
by = {r["name"]: r for r in rows("A19")}
d = json.loads((HERE / "W7_SPURIOUS.json").read_text())
out = []
for x in d:
    r = by[x["name"]]
    T4.use_provider(prov_of(r))
    w = ("fold", r["init"], r["body"], r["final"])
    p = tuple(x["orig_prog"])
    s1 = T4A.direct_score(p, r["name"], w, "v1")
    sa = T4A.direct_score(p, r["name"], w, "v1a")
    fails = {k: len(v) for k, v in s1["fails"].items()}
    ce_q = sorted({m for _L, m in s1["fails"]["ce"]})
    out.append({"name": x["name"], "cell": x["cell"], "kind": x["kind"], "prog": list(p), "v1": s1["qualified"],
                "v1a": sa["qualified"], "v1_fail_counts": fails, "v1_ce_fail_queries": ce_q[:6],
                "extra_examples_to_reject": x["extra_examples_to_reject"],
                "v1a_acc": sa["acc"]})
    print(x["kind"], x["name"], x["cell"], s1["qualified"], sa["qualified"], fails, ce_q[:6], x["extra_examples_to_reject"])
(HERE / "W7_SPURIOUS_V1A.json").write_text(json.dumps(out, indent=1))
