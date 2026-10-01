"""Summarise q1_trace.pkl: per genome x side, keep-loss authorship, partner entry into the donor half, partner
reaching donor pos 43 / LDIR pos 52, donor LDIR counts/registers, terminator (halt / budget ends inside LDIR)."""
import pickle, collections, json, pathlib
from q1_trace import panel
HERE = pathlib.Path(__file__).resolve().parent
d = pickle.load(open(HERE / "q1_trace.pkl", "rb"))
pan = panel()
n = 64
out = {}


def rel(pc, s):  # position relative to the donor's half, or None if in partner half
    b = s * n
    return pc - b if b <= pc < b + n else None


for name, recs in d.items():
    for s in (0, 1):
        idx = [i for i in range(1000) if pan[i][3] == s]
        pt = 1 - s
        row = collections.Counter()
        dom = collections.Counter()
        ldir_regs = collections.Counter()
        p_ldir = collections.Counter()
        for i in idx:
            q = recs[i]
            P, D = q["path"][pt], q["path"][s]
            ppcs, dpcs = P["pcs"], D["pcs"]
            row["N"] += 1
            row["keep"] += q["keep"]; row["conv"] += q["conv"]
            row["keep_exact"] += q["keep_exact"]; row["conv_exact"] += q["conv_exact"]
            entered = any(rel(p, s) is not None for p in ppcs)
            row["partner_enters_donor_half"] += entered
            if entered:
                e = next(p for p in ppcs if rel(p, s) is not None)
                row["partner_entry_pos_%d" % rel(e, s)] += 1
            row["partner_reaches_pos43"] += (s * n + 43) in ppcs
            row["partner_runs_donor_LDIR52"] += any(l[0] == s * n + 52 for l in P["ldirs"])
            row["partner_jumps_43_to_108"] += any(ppcs[k] == s * n + 43 and ppcs[k + 1] == 108 for k in range(len(ppcs) - 1))
            row["donor_halted"] += D["halted"]
            row["donor_n_ldir_%d" % len(D["ldirs"])] += 1
            if D["ldirs"]:
                pc, src, dst, nn, regs = D["ldirs"][0]
                ldir_regs["first donor LDIR @%d HL=%04x DE=%04x n=%d" % (pc, src, dst, nn)] += 1
            # terminator: last donor step is the LDIR (budget consumed by the count)
            row["donor_budget_ends_in_LDIR"] += bool(D["ldirs"]) and D["ldirs"][-1][0] == dpcs[-1]
            if not q["keep"]:
                a = q["auth"]
                dom[max(a, key=a.get) if a else "none"] += 1
                for pc, src, dst, nn, regs in P["ldirs"]:
                    w = "donor_half" if rel(pc, s) is not None else "partner_half"
                    p_ldir["lost: partner LDIR in %s code @pos%d src=%s dst=%s n=%d" % (
                        w, pc - s * n if w == "donor_half" else pc, "H%d" % (src % 128 >= 64), "%d" % (dst % 128), nn)] += 1
        out["%s_side%d" % (name, s)] = {"counts": dict(sorted(row.items())), "keep_loss_dominant_author": dict(dom),
                                        "first_donor_LDIR": dict(ldir_regs.most_common(6)),
                                        "partner_LDIRs_in_lost_cases": dict(p_ldir.most_common(8))}
(HERE / "q1_summary.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
