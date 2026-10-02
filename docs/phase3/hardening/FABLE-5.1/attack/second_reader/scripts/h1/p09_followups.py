"""Follow-ups."""
from drv import *
from exactbin import tge, tle
R, DEMAND, TRAIN, SEEDS, BLOCKS, PAIRS = retain1, meta.DEMAND, meta.TRAIN, meta.SEEDS, meta.BLOCKS, meta.PAIRS
seq, cell, run_receipt, SOURCE = registration, meta.cell, meta.run_receipt, meta.SOURCE

print("--- 1. the listed G8 escape with a recorder that keeps two bits of the clock (in memory only)")


class Recorder2(R.Recorder):
    def step(self, obs):
        if obs.kind in ("DISTRACT", "PROBE"):
            self.seen.append((obs.value, obs.clock & 3, obs.mark))
        if obs.kind == "PROBE":
            return 0


orig = torture.Recorder
print("     as shipped (clock & 1): bit1 leak ->", torture.demand_closure(DEMAND, TRAIN, leak_clock="bit1").verdict)
torture.Recorder = Recorder2
r = torture.demand_closure(DEMAND, TRAIN, leak_clock="bit1")
print("     recorder keeps clock & 3: bit1 leak ->", r.verdict, "| TABLE", r.detail["TABLE"], "| sound world ->",
      torture.demand_closure(DEMAND, TRAIN).verdict)
torture.Recorder = orig

print("--- 2. the interchange ruler on the weak positive")
follows = total = 0
for seed in PAIRS:
    for donor_bit in (0, 1):
        for sham in (False, True):
            recipient_bit = donor_bit if sham else 1 - donor_bit
            box = []
            R.World().episode(R.FadingRegister(), seed, force_bit=donor_bit, interrupt={3: lambda org: box.append(org.capture())})
            got = R.World().episode(R.FadingRegister(), seed, force_bit=recipient_bit,
                                    interrupt={3: lambda org: org.restore(box[0])})["answer"]
            total += 1
            follows += got == donor_bit
print("     recipient follows the donor in %d of %d trials -> interchange says %s; class exclusion says %s (%d of 64)" % (
    follows, total, rulers.interchange_ruler(R.FadingRegister, PAIRS), rulers.exclusion_ruler(R.FadingRegister, SEEDS),
    R.score(R.FadingRegister, SEEDS)))
print("     G5 with the weak positive entered as a fifth physics' positive:",
      meta.neutral("INTERCHANGE", "SHARED", dict(R.PANEL, FADING=(R.FadingRegister, R.RegisterImpostor))).verdict)

print("--- 3. positives on all nine blocks")
for ph, (pos, imp) in sorted(R.PANEL.items()):
    print("     %-9s %s" % (ph, [R.score(pos, b) for b in [SEEDS] + BLOCKS]))

print("--- 4. a class whose true rate is inside the G8 margin, under the 64-episode ruler")
for num, den in ((1, 2), (27, 50), (273, 500), (11, 20), (3, 5)):
    print("     rate %.3f: P(score >= 51 of 64) = %.3g ; P(G8 calls it WITHIN at 2,048) = %.3f" % (
        num / den, float(tge(64, 51, (num, den))), float(tle(2048, 1119, (num, den)) - tle(2048, 928, (num, den)))))

print("--- 5. seed containers")
for name, c in (("design_seeds=(1,2,3) tuple", cell(design_seeds=(1, 2, 3))), ("registered_seeds a tuple of 24", cell(registered_seeds=tuple(range(5000, 5024)))),
                ("registered_seeds=() empty tuple", cell(registered_seeds=())), ("registered_seeds=[] empty list", cell(registered_seeds=[]))):
    r = seq.check_cell(c)
    print("     %-36s -> %s %s" % (name, r.verdict, r.reason[:70]))

print("--- 6. fields of a receipt the gate does not read")
r = seq.check_receipt(cell(), run_receipt(count=13, outcome="HOLDS"), SOURCE)
print("     a receipt that reports HOLDS for a count of 13 (the registered table says INDETERMINATE) ->", r.verdict)
r = seq.check_receipt(cell(), run_receipt(count=30, outcome="HOLDS", units=40), SOURCE)
print("     a receipt that reports 30 passes of 40 units on a 24-unit table ->", r.verdict)
r = seq.check_receipt(cell(known_answers=None, verdict_table=None), run_receipt(), SOURCE)
print("     a receipt checked against a cell that G1.cell would block ->", r.verdict)

print("--- 7. G3 on other choices of the main block")
for i, blk in enumerate(BLOCKS[:8]):
    others = [SEEDS] + [b for j, b in enumerate(BLOCKS) if j != i]
    r = rulers.exclusion_gate(rulers.exclusion_ruler, R.PANEL, blk, R.FadingRegister, others)
    if r.verdict != PASS:
        print("     main block %d: %s %s" % (i + 1, r.verdict, r.reason[:100]))
print("     sound panel on each of the 8 other blocks as the main block: done")

print("--- 8. attainability: the third registered outcome")
t = meta.table()
print("     outcomes registered:", t["outcomes"], "; known answers registered:", sorted(cell()["known_answers"]))
EOF_MARKER = None
