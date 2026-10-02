"""G3.exclusion, G4.entry, G5.neutrality."""
from drv import *
R, SEEDS, BLOCKS, PAIRS = retain1, meta.SEEDS, meta.BLOCKS, meta.PAIRS
p_ok = dict(R.PANEL)

def show(name, thunk):
    try:
        r = thunk()
        print("%-86s -> %s %s" % (name, r.verdict, ("| " + r.reason[:170]) if r.reason else ""))
    except Exception as e:
        print("%-86s -> RAISES %s: %s" % (name, type(e).__name__, str(e)[:100]))

print("--- the panel: impostor scores per block (block 0 = SEEDS)")
for ph, (pos, imp) in sorted(R.PANEL.items()):
    print("  %-9s positive %d  impostor %s" % (ph, R.score(pos, SEEDS), [R.score(imp, b) for b in [SEEDS] + BLOCKS]))
print("  weak positive", R.score(R.FadingRegister, SEEDS), "on the 8 further blocks:", [R.score(R.FadingRegister, b) for b in BLOCKS])
same = all(R.score(R.RegisterImpostor, b) == R.score(R.PacketImpostor, b) == R.score(R.LatticeImpostor, b) for b in [SEEDS] + BLOCKS)
print("  REGISTER, PACKET and LATTICE impostors give one series on all nine blocks:", same)
# per-episode identity
w = R.World()
eq = 0
for s in SEEDS:
    a = [R.World().episode(c(), s)["answer"] for c in (R.RegisterImpostor, R.PacketImpostor, R.LatticeImpostor)]
    eq += a[0] == a[1] == a[2]
print("  the three give the same answer in %d of %d episodes" % (eq, len(SEEDS)))

print("--- the bracket and what sets each end")
b = meta.bracket()
print("  bracket:", b["lowest"], b["highest"], "impostor scores", b["impostor_scores"])
pos = [R.score(p, SEEDS) for p, _ in R.PANEL.values()]
weak = R.score(R.FadingRegister, SEEDS)
imp = [R.score(i, block) for _, i in R.PANEL.values() for block in [SEEDS] + BLOCKS]
def okset(pos_scores, imp_scores, exact_rate=True):
    return [bb / 100 for bb in range(1, 100)
            if all(stats.classify(s, 64, bb / 100, rulers.ALPHA, rulers.P_WEAKEST, exact_rate) == "EXCLUDES" for s in pos_scores)
            and all(stats.classify(s, 64, bb / 100, rulers.ALPHA, rulers.P_WEAKEST, exact_rate) == "AT_BOUND" for s in imp_scores)]
full = okset(pos + [weak], imp)
print("  full panel:", min(full), max(full), "contiguous", full == [x / 100 for x in range(round(min(full) * 100), round(max(full) * 100) + 1)])
nw = okset(pos, imp)
print("  WITHOUT the weak positive:", min(nw), max(nw))
ob = okset(pos + [weak], [R.score(i, SEEDS) for _, i in R.PANEL.values()])
print("  with the weak positive and block 0 only:", min(ob), max(ob))
ni = okset(pos + [weak], imp, exact_rate=False)
print("  full panel, INVERTED rule off:", min(ni), max(ni))
for bb in (0.68, 0.69, 0.70, 0.71, 0.72):
    hi = stats.critical_k(64, bb, 1e-6); low = stats.lower_critical(64, bb, 1e-6)
    print("  bound %.2f: yes needs >= %s, INVERTED at <= %s; weak positive %d -> %s; lowest impostor %d -> %s" % (
        bb, hi, low, weak, stats.classify(weak, 64, bb, 1e-6, 15 / 16), min(imp), stats.classify(min(imp), 64, bb, 1e-6, 15 / 16)))
print("  impostor block-scores <= 26:", sorted(s for s in imp if s <= 26), " >= 39:", sorted(s for s in imp if s >= 39))

print("--- G3 broken cases")
show("X1 bound 0.25, the eight 'further blocks' are the first block again", lambda: meta.exclusion(rulers.make_exclusion_ruler(0.25), blocks=[SEEDS] * 8))
show("X1b bound 0.25 with the registered blocks (the registered mutant)", lambda: meta.exclusion(rulers.make_exclusion_ruler(0.25)))
show("X2 bound 0.70, the weak positive is a perfect positive", lambda: meta.exclusion(rulers.make_exclusion_ruler(0.70), weak=R.Register, blocks=[SEEDS] * 8))
def two_answer(make, seeds):          # no undecided band, no inverted answer: everything under 51 is NEGATIVE
    return "POSITIVE" if R.score(make, seeds) >= 51 else "NEGATIVE"
show("X3 a ruler with two answers only (yes at >= 51, otherwise no)", lambda: meta.exclusion(two_answer))
print("     that ruler on an inverter (score 0):", two_answer(R.Inverter, SEEDS), "; on a 49-of-64 scorer:", two_answer(R.scripted(49), SEEDS))
names = {c.__name__ for pair in R.PANEL.values() for c in pair} | {"FadingRegister"}
answers = {"Register": "POSITIVE", "Attractor": "POSITIVE", "PacketRing": "POSITIVE", "Lattice": "POSITIVE", "FadingRegister": "POSITIVE"}
def memo(make, seeds):                # reads the organism's name and runs nothing
    return answers.get(make.__name__, "NEGATIVE")
show("X4 a ruler that looks the panel's names up and runs no episode", lambda: meta.exclusion(memo))
show("X5 weak positive = a constant fixture scripted to score 61 (not an organism)", lambda: meta.exclusion(weak=R.scripted(61)))

print("--- G4")
show("N1 positive right in its first 64 episodes only (scripted(64))", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(R.scripted(64), R.RegisterImpostor))))
s64 = R.scripted(64); print("     that positive on 64 + 64 episodes:", R.score(s64, SEEDS), R.score(s64, BLOCKS[0]))
show("N2 impostor is a constant answerer (not a matched machine)", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(R.Register, R.Constant))))
show("N3 SOUND: the same sound pair supplied as factories", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(lambda: R.Register(), lambda: R.RegisterImpostor()))))
import functools
show("N3b SOUND: supplied as functools.partial", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(functools.partial(R.Register), functools.partial(R.RegisterImpostor)))))
show("N4 impostor that scores in the undecided band", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(R.Register, R.scripted(49)))))
show("N5 the weak positive as the designed positive", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(R.FadingRegister, R.RegisterImpostor))))
for i, blk in enumerate(BLOCKS):
    r = rulers.entry_gate("ATTRACTOR", R.PANEL, blk)
    if r.verdict != PASS:
        print("     SOUND attractor pair on further block %d: %s %s" % (i + 1, r.verdict, r.reason[:100]))
print("     entry on each physics x each of the 9 blocks:", {ph: [rulers.entry_gate(ph, R.PANEL, blk).verdict for blk in [SEEDS] + BLOCKS] for ph in R.PANEL})

print("--- G5")
show("U1 a ruler that looks up the panel by class name, declared SHARED", lambda: meta.neutral("MEMO", "SHARED", ruler=memo))
show("U2 interchange, SHARED, on 1 pair of seeds", lambda: meta.neutral("INTERCHANGE", "SHARED", seeds=PAIRS[:1]))
show("U3 interchange, SHARED, with no seeds at all", lambda: meta.neutral("INTERCHANGE", "SHARED", seeds=[]))
show("U3b register-swap, SHARED, with no seeds at all", lambda: meta.neutral("REGISTER_SWAP", "SHARED", seeds=[]))
show("U4 declared scope as the string 'shared' (lower case)", lambda: meta.neutral("CLASS_EXCLUSION", "shared"))
show("U5 interchange SHARED; ATTRACTOR 'impostor' is a positive whose restore does nothing",
     lambda: meta.neutral("INTERCHANGE", "SHARED", dict(p_ok, ATTRACTOR=(R.Attractor, R.AttractorStaleRestore))))
print("     that 'impostor' under class exclusion:", rulers.exclusion_ruler(R.AttractorStaleRestore, SEEDS), R.score(R.AttractorStaleRestore, SEEDS))
show("U6 class exclusion SHARED on three physics that are one machine + ... (4 real + 20 with no known answer)",
     lambda: meta.neutral("CLASS_EXCLUSION", "SHARED", dict(p_ok, **{"X%d" % i: (None, None) for i in range(20)})))
