"""BEL-RD-72 reviewer Q4: the two components of budget coupling, manipulated SEPARATELY (static, deterministic; no world).
    python3 budget_split.py OUT.json
Specimens (EXPLORATORY, post-hoc after the first grid showed no exhaustion failures in COPY_FIRST):
  COPY_FIRST         copier (LD S,0; LD T,64; LD C,c; LDIR) then IN; INC; OUT   (input read AFTER the copy)
  IN_FIRST_OUT_LAST  IN; copier; INC; OUT                                       (input read BEFORE, output AFTER the copy)
  COMPUTE_FIRST      IN; INC; OUT then the copier
  EVOLVED_W4_00735   the BEL-48H M6 specimen with its LD C operand set to c (ECHO)
For every copy length c = 0..255 (0 = a 256-byte copy: the NOP-knockout value) and budget in (192, 256, 384, 1024, 4096): competent? and FUNC? Plus, per c, whether the
copy reaches the I/O area (64 + c > 0xE0): EXHAUSTION predicts failure that vanishes with budget; DAMAGE predicts failure
at c > 160 that does NOT vanish with budget and spares the architecture that reads its input before copying."""
import json, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from belinst import Func
from prometheus.z80atlas import vm, tasks, coupling_campaign as CC
from prometheus.z80atlas.world import Config
L = 64


W4_00735 = bytes.fromhex("07000e4003401552c95eac410b1bcc3551cb30007bff99f1dd281c6aeaa9eaf56fb285031c09780c563d3e8d21379a93e16aee0c7bf52aed44fe16ea34153a22")


def specimens(c):
    """name -> (tape, task). W4_00735 = the BEL-48H M6 specimen (ECHO; IN at byte 3, LD C at 4-5, LDIR at 6, OUT at 11)."""
    cp = bytes([vm.LD_S_n, 0, vm.LD_T_n, L, vm.LD_C_n, c, vm.LDIR])
    pad = lambda b: bytes(b) + bytes(L - len(b))
    ev = bytearray(W4_00735); ev[5] = c
    return {"COPY_FIRST": (pad(cp + bytes([vm.IN_A, vm.INC_A, vm.OUT_A, vm.HALT])), "INC"),
            "IN_FIRST_OUT_LAST": (pad(bytes([vm.IN_A]) + cp + bytes([vm.INC_A, vm.OUT_A, vm.HALT])), "INC"),
            "COMPUTE_FIRST": (pad(bytes([vm.IN_A, vm.INC_A, vm.OUT_A]) + cp + bytes([vm.HALT])), "INC"),
            "EVOLVED_W4_00735": (bytes(ev), "ECHO")}


def main(outp):
    out = {}
    for B in (192, 256, 384, 512, 1024, 4096):
        d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", budget=B); cfg = Config(**d); f = Func(cfg)
        for c in range(0, 256):
            for arch, (t, tk) in specimens(c).items():
                comp = tasks.verify_exact(t, L, tasks.Task(tk), "ABR", budget=B)
                out.setdefault(arch, {}).setdefault(str(B), {})[c] = [comp, f(t)]
    summ = {}
    for arch, byB in out.items():
        for B, row in byB.items():
            lo = [c for c in range(1, 161) if not row[c][0]]; hi = [c for c in range(161, 256) if not row[c][0]]
            summ["%s|%s" % (arch, B)] = {"competence_fail_c<=160": len(lo), "competence_fail_c>160": len(hi), "of": [160, 95],
                                         "func_c": [c for c in range(1, 256) if row[c][1]], "c0_256byte_copy": row[0]}
    json.dump({"grid": out, "summary": summ}, open(outp, "w"))
    for k, v in summ.items():
        print(k, v["competence_fail_c<=160"], v["competence_fail_c>160"], "FUNC at c=", v["func_c"][:3], "..", len(v["func_c"]))


if __name__ == "__main__":
    main(sys.argv[1])
