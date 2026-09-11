"""ELEN: D-18 inertness proof, verified with the CORRECT representation.

First attempt indexed the 32-char hex STRING as if it were a rule table and
produced nonsense values (4, 5) for a binary output. Recorded as a miss.
The hex is 32 digits = 128 bits = a radius-3 (7-cell) neighbourhood rule.
maj's docstring ("output 1 iff popcount >= 4") is the bit-order calibration.
"""
import sys
sys.path.insert(0, "F:/Prometheus-worktrees/elenchus-baserole")
from herakles.evca.genomes import GENOMES

def unpack(hexstr, msb_first=True):
    n = int(hexstr, 16)
    bits = [(n >> i) & 1 for i in range(128)]        # bits[i] = LSB-indexed
    return bits[::-1] if msb_first else bits

print("=== BIT-ORDER CALIBRATION against maj's stated definition (1 iff popcount>=4) ===")
for msb in (True, False):
    t = unpack(GENOMES["maj"]["hex"], msb)
    ok = all(t[i] == (1 if bin(i).count("1") >= 4 else 0) for i in range(128))
    print(f"  msb_first={msb}: maj matches popcount>=4 ? {ok}")
    if ok:
        ORDER = msb

print("\n=== CLAIM: every rule outputs 0 at every neighbourhood with popcount <= 1 ===")
low = [i for i in range(128) if bin(i).count("1") <= 1]
print("  popcount<=1 indices:", low, "(matches the 8 indices OBSTRUCTION.md names)")
allok = True
for name, rec in GENOMES.items():
    t = unpack(rec["hex"], ORDER)
    vals = [t[i] for i in low]
    ok = all(v == 0 for v in vals)
    allok &= ok
    print(f"  {name:<10} {vals}  {'OK' if ok else 'COUNTEREXAMPLE'}")
print("  ALL SIX RULES ANNIHILATE EVERY popcount<=1 NEIGHBOURHOOD:", allok)

print("\n=== THE MODAL SUB-CLAIM: 'a density classifier MUST annihilate a lone minority cell' ===")
print("Testing whether that is forced, by counting rules that classify density")
print("correctly on the extremes yet PRESERVE a lone live cell.")
lone = 8   # centre-only in a 7-cell neighbourhood, index 0b0001000
print(f"  centre-only neighbourhood index = {lone} (0b{lone:07b})")
for name, rec in GENOMES.items():
    t = unpack(rec["hex"], ORDER)
    print(f"  {name:<10} rule[centre-only]={t[lone]}  rule[all-zero]={t[0]}  rule[all-one]={t[127]}")
print()
print("  A rule with rule[centre-only]=1 and the correct all-zero/all-one fixed")
print("  points is constructible: take maj and flip index 8 to 1. It still maps")
print("  all-zeros to all-zeros and all-ones to all-ones, and it still outputs")
print("  the majority on every neighbourhood of popcount >= 2. It is not a GOOD")
print("  classifier, but the modal claim is about what a density classifier MUST")
print("  do, and one-step annihilation of a lone cell is not entailed by the task.")
t = unpack(GENOMES["maj"]["hex"], ORDER)
t[lone] = 1
viol = [i for i in range(128) if bin(i).count("1") >= 4 and t[i] != 1]
viol += [i for i in range(128) if bin(i).count("1") <= 2 and i != lone and t[i] != 0]
print(f"  constructed variant: still majority-correct outside index 8 ? {len(viol)==0}")
print(f"  fixed points preserved: all-zero->{t[0]}, all-one->{t[127]}")
