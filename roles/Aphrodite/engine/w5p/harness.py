"""Beta-02-compatible job wrapper for the W5P donor (mirrors engine/v2b/b02._donor).

Import order matters and is fixed here: b02 is imported FIRST, so t51_natural sets A18_TAG=T51 and ESCROW=30k before
a18 is first imported (cell labels and escrow are then exactly Beta-01/02's).

job = (tag, rule, width, seed, fams, panel, start_entries or None[, opts])
  rule in {"g0"/"I0", "g0x", "g10", "g11"} (b02.RULES semantics) ; opts: dict of donor_w5p keyword options
  (promote, meter, extra_promoted). Returns b02._donor's row + the "w5p" block.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
from . import _paths  # noqa: E402,F401
import b02  # noqa: E402  (must precede any a18 import)
from . import donor as D  # noqa: E402


def init_worker():
    b02.T.init_worker()


def run(job):
    tag, rule, width, s, fams, panel, start = job[:7]
    opts = job[7] if len(job) > 7 else {}
    b02.T.init_worker()
    import a17
    import a18
    import a18_c1
    assert a18.TAG == "T51", "a18 imported before t51_natural: cell labels would differ (TAG=%s)" % a18.TAG
    a17.R_VAL = a18_c1.R_VAL_C1
    genome, exclude = D.RULES[rule]
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    args = ("LIN%d" % s, "P", s, fl, specs, panel, True) + ((start,) if start is not None else ())
    r = D.donor_w5p(genome, args, exclude=exclude, **opts)
    return {"tag": tag, "rule": rule, "width": width, "seed": s, "selected": r["selected"],
            "selected_schema": r["selected_schema"], "selected_origin": r["selected_origin"],
            "selected_entries": r["selected_entries"], "n_observed": r["n_observed"], "n_derived": r["n_derived"],
            "classes": r["classes"], "seconds": r["seconds"], "memorise_selected": r["selected"] == "MEMORISE",
            "meta_charges": r["meta_charges"], "w5p": r["w5p"]}
