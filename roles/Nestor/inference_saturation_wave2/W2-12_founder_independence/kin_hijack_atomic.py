"""W2-12 step 4b: would the side-0 hijack loss survive ATOMIC write-back?

Under ATOMIC (x_atomic / c_atomic runner) a half keeps its pre-interaction genome unless the
interaction was an accepted replication event (predecessor_accepts: fid_other >= 0.9, fid_self < 0.9,
donor wrote >= n/4 bytes outside its half). In a hijack, the 7ae3 context itself copies the partner's
half onto its own, so the partner's writes_other is small and the event should NOT be accepted ->
ATOMIC restores 7ae3. If so, kin protection is a BASE-only benefit and the kin route predicts no
founder interaction under ATOMIC.
Also: per-interaction erosion (bytes of the 7ae3 half changed) with random vs kin partner, both sides.
"""
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kin_hijack as K  # noqa: E402  (module import only builds a Runner object; no world run)

TR = 400


def main():
    out = {}
    for side in (0, 1):
        rng = random.Random(("W2-12b", side).__repr__())
        lost = accepted = 0
        wo_partner = []
        for t in range(TR):
            pb = bytes(rng.randrange(256) for _ in range(K.N))
            ga, gb = (K.G, pb) if side == 0 else (pb, K.G)
            h0, h1, wo = K.interact(ga, gb, K.ZERO, K.ZERO, ("b", side, t).__repr__(), 0.0)
            mine = h0 if side == 0 else h1
            if K.p11.fidelity(mine, K.G) < 0.9:
                lost += 1
                fid_other = K.p11.fidelity(pb, mine)
                fid_self = K.p11.fidelity(K.G, mine)
                partner_wrote = wo[1 - side]
                wo_partner.append(partner_wrote)
                accepted += K.p11.predecessor_accepts(fid_other, fid_self, partner_wrote, K.N)
        out["side%d" % side] = {"trials": TR, "lost_BASE": lost, "of_which_accepted_event(would persist under ATOMIC)": accepted,
                                "partner_writes_other_in_lost(median)": sorted(wo_partner)[len(wo_partner) // 2] if wo_partner else None}
        print(side, out["side%d" % side], flush=True)
    (HERE / "kin_hijack_atomic.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
