"""C-017-T040 witnesses: one small computation per edit, run by run_edits.py under the frozen source and under the mutant in
fresh -B subprocesses. Prints one JSON line. W1 XOR writer (E1), W2 JR-operand tape (E2), W3 synthetic rows with unforged
refusals (E3), W5 input writer (E5). E4 is the harness control (a committed RED mutant) and has no witness."""
import json
import sys

from archaeon.z80atlas import vm
from rso.z80 import analysis, assay, observe, subjects as S
from rso.z80.challenge import subjects_c as C


def tags_of(parent, nbr, inp=(7,)):
    res = vm.execute(parent, nbr, inp, 256, True)
    return observe.endo_tags(res, res["nbr_window"], observe.counterfactual(parent, nbr, inp, 256, True))


def rows_w3():
    out = []
    for gt in ("ENDO", "EXT", "ENV", "INS"):
        for k in range(24):
            out.append(dict(arm=gt + "_ARM", gt=gt, origin_gt="INSERTED", forgery="", cls=gt, origin="INSERTED", refused="",
                            b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
    for k in range(5):                                                    # five UNFORGED ENV records the instrument refused
        out.append(dict(arm="ENV_ARM", gt="ENV", origin_gt="INSERTED", forgery="", cls="REFUSED", origin="", refused="REPLAY_MISMATCH",
                        b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
    for kind in ("LABELS", "PLANT"):
        out.append(dict(arm="F", gt="EXT", origin_gt="INSERTED", forgery=kind, cls="EXT", origin="INSERTED", refused="", source_cls="EXT",
                        source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
    for kind in ("PHYS", "TAPE", "GEN"):
        out.append(dict(arm="F", gt="REFUSED", origin_gt="", forgery=kind, cls="REFUSED", origin="", refused="REPLAY_MISMATCH",
                        source_cls="EXT", source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
    return out


def main(w):
    cases = assay.probe_cases(C.CDIST_SEEDS[0])
    if w == "W1":
        xw = C.XORW(); t = tags_of(xw, xw)
        return dict(witness=w, byte0_tag=t[0], tags=t)
    if w == "W2":
        return dict(witness=w, label=assay.label(C.JROP(), "PPKPP" + "P" * (S.G - 5), None, cases))
    if w == "W3":
        v = analysis.verdict(rows_w3())
        return dict(witness=w, verdict=v["verdict"], env=v["q1"]["ENV"], failed=v["failed"])
    if w == "W5":
        t = tags_of(C.INPW(), bytes(S.G), (7,))
        return dict(witness=w, byte0_tag=t[0], tags=t)
    raise SystemExit("unknown witness " + w)


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), sort_keys=True))
