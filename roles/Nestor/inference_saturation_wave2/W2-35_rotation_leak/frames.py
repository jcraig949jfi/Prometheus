"""W2-35 shared: frame (ring-rotation) of a 64-byte half relative to the 7ae3 implant.
rot(g, s) = #{i : g[(i+s) % 64] == imp[i]}  (W2-17 a3 convention: implant byte i sits at g position i+s).
frame(g) -> (best_s, best_count, count_at_0); candidate shifts by 3-mer votes (all 64 implant 3-mers are unique),
then exact counts. A 'rotated' half: best_s != 0 and best_count >= T (T = 16 primary, 32 sensitivity)."""
import sys, pathlib, json
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
C9 = W2.parent / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world  # noqa: E402
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
_man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
_b = next(b for b in _man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
ARM = next(a for a in _b["arms"] if a["arm"] == "B_reimplant_actual")
IMP = bytes.fromhex(ARM["kwargs"]["implant_hex"])
N = 64
IDX3 = {bytes(IMP[(i + j) % N] for j in range(3)): i for i in range(N)}
assert len(IDX3) == N


def rot(g, s, ref=IMP):
    return sum(g[(i + s) % N] == ref[i] for i in range(N))


def frame(g, ref=None):
    if ref is not None and ref != IMP:
        best = max(((rot(g, s, ref), s) for s in range(N)), key=lambda t: (t[0], -t[1]))
        return best[1], best[0], rot(g, 0, ref)
    votes = {}
    for j in range(N):
        i = IDX3.get(bytes(g[(j + k) % N] for k in range(3)))
        if i is not None:
            s = (j - i) % N
            votes[s] = votes.get(s, 0) + 1
    c0 = rot(g, 0)
    best = (c0, 0)
    for s, v in votes.items():
        if s and v >= 2:
            c = rot(g, s)
            if c > best[0]:
                best = (c, s)
    return best[1], best[0], c0
