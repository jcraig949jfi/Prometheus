"""Positive controls: hand-built copiers with KNOWN self-location sources, run through the identical
transplant battery (selfloc.job), so each class is shown able to fire. Dense VM rules apply to ED forms too.
Expected (declared in this docstring before running):
  C_LOCATOR       SELF; DE = HL + 64 computed; LDIR          -> LOCATOR, STATE_FREE
  C_TAPE          LD HL,0; LD DE,64; LD BC,64; LDIR           -> TAPE_ANCHORED, STATE_FREE
  C_ZERO_BOTH     E = E + 64 (from fresh zeros), HL fresh, LDIR -> STATE_ANCHORED (D32_PTRSHIFT), not STATE_FREE
  C_ZERO_HL_IMM_E LD E,64; LDIR (HL fresh 0)                   -> TAPE_ANCHORED (mixed: immediate dest), not STATE_FREE
-> controls.json
"""
import json
import pathlib

import selfloc

HERE = pathlib.Path(__file__).resolve().parent
PROGS = {
    "C_LOCATOR": "ED32 7D C640 5F 54 EDB0 76",
    "C_TAPE": "210000 114000 014000 EDB0 76",
    "C_ZERO_BOTH": "7B C640 5F EDB0 76",
    "C_ZERO_HL_IMM_E": "1E40 EDB0 76",
}


def main():
    import analyze
    out = {}
    for name, src in PROGS.items():
        g = bytes.fromhex(src.replace(" ", "")).ljust(64, b"\x00")
        e = {"hex": g.hex(), "vm": "DENSE", "cell": "7ae3", "origin_run": "control/" + name, "nocopy_donor": None,
             "self_dep": None, "rate_full": None, "rate_noself": None}
        r = selfloc.job(e)
        cls, flags, n_off = analyze.classify(r)
        out[name] = {"src": src, "home": r["home"], "cls": cls, "flags": flags, "n_off": n_off,
                     "ss_rates": r["ss_rates"], "rates": r["rates"]}
        print(name, cls, n_off, flags, r["ss_rates"])
    (HERE / "controls.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
