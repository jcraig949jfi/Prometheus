"""Independent verification of the recovered EvCA rule tables.

Convention under test (from the Table 1 caption of the EvCA review):
  expand each hex digit (first row then second row) to binary; the output bits
  are in lexicographic order starting from the all-0s neighbourhood at the
  LEFTMOST bit of the 128-bit string.
Empirically determined by the recovery agent, re-tested here: the leftmost
neighbour (cell i-3) is the most significant bit of the neighbourhood index.
"""
import numpy as np

N = 149
R = 3


def hex_to_table(h):
    h = h.replace(" ", "").lower()
    assert len(h) == 32, (len(h), h)
    bits = bin(int(h, 16))[2:].zfill(128)
    return np.array([int(b) for b in bits], dtype=np.uint8)


def majority_table():
    """maj from first principles: output 1 iff popcount >= 4 of the 7 cells."""
    out = []
    for idx in range(128):
        nb = [(idx >> (6 - j)) & 1 for j in range(7)]
        out.append(1 if sum(nb) >= 4 else 0)
    return np.array(out, dtype=np.uint8)


def gkl_table():
    """GKL from its definition.
    If the cell is 0, its new state is the majority of cells {i, i-1, i-3}.
    If the cell is 1, its new state is the majority of cells {i, i+1, i+3}.
    Neighbourhood index bits are cells i-3 .. i+3, MSB = i-3.
    """
    out = []
    for idx in range(128):
        nb = [(idx >> (6 - j)) & 1 for j in range(7)]  # nb[0]=i-3 ... nb[6]=i+3
        c = nb[3]
        if c == 0:
            trio = [nb[3], nb[2], nb[0]]      # i, i-1, i-3
        else:
            trio = [nb[3], nb[4], nb[6]]      # i, i+1, i+3
        out.append(1 if sum(trio) >= 2 else 0)
    return np.array(out, dtype=np.uint8)


def table_to_hex(tab):
    return "%032x" % int("".join(str(int(b)) for b in tab), 2)


def step(state, table):
    """state: (n, N) uint8 -> next state."""
    idx = np.zeros(state.shape, dtype=np.int32)
    for j, off in enumerate(range(-R, R + 1)):
        idx |= np.roll(state, -off, axis=1).astype(np.int32) << (6 - j)
    return table[idx]


def performance(table, n_ics=10000, steps=300, N=N, seed=0):
    """Unbiased ICs: each cell iid uniform. Correct iff the lattice reaches the
    uniform state matching the majority of the IC."""
    rng = np.random.default_rng(seed)
    state = (rng.random((n_ics, N)) < 0.5).astype(np.uint8)
    dens = state.sum(axis=1)
    target = (dens > N // 2).astype(np.uint8)   # N odd so no ties
    for _ in range(steps):
        state = step(state, table)
    s = state.sum(axis=1)
    reached_all1 = (s == N)
    reached_all0 = (s == 0)
    correct = np.where(target == 1, reached_all1, reached_all0)
    return correct.mean()


RULES = {
    # name: (hex, published P149, P599, P999, source)
    "maj_review":   ("000101170117177f0117177f177f7fff", 0.000, 0.000, 0.000, "review Table 1"),
    "maj_evemcomp": ("000101170117177701171777177f7fff", 0.000, 0.000, 0.000, "EvEmComp Table 1 (suspected typo)"),
    "exp":          ("0505408305c90101200b0efb94c7cff7", 0.652, 0.515, 0.503, "review + EvEmComp"),
    "par":          ("0504058705000f77037755837bffb77f", 0.769, 0.725, 0.714, "review + EvEmComp"),
    "particle1":    ("10000224411702311155f57dd734bffff"[:32], 0.742, 0.718, 0.701, "EvEmComp only"),
    "particle2":    ("031001001fa00013331f9fff5975ffff", 0.755, 0.696, 0.670, "EvEmComp only"),
    "GKL":          ("005f005f005f005f005fff5f005fff5f", 0.816, 0.766, 0.757, "EvEmComp Table 1"),
}
# fix particle1: the reported string is 8 groups of 8 -> 32 hex digits
RULES["particle1"] = ("10000224" "41170231" "155f57dd" "734bffff", 0.742, 0.718, 0.701, "EvEmComp only")

print("=" * 78)
print("STEP 1 -- derive maj and GKL from first principles, compare to published hex")
print("=" * 78)
maj = majority_table()
gkl = gkl_table()
print("maj  derived :", table_to_hex(maj))
print("maj  review  :", RULES["maj_review"][0], "MATCH" if table_to_hex(maj) == RULES["maj_review"][0] else "MISMATCH")
print("maj  EvEmComp:", RULES["maj_evemcomp"][0], "MATCH" if table_to_hex(maj) == RULES["maj_evemcomp"][0] else "MISMATCH <-- typo claim")
print("GKL  derived :", table_to_hex(gkl))
print("GKL  EvEmComp:", RULES["GKL"][0], "MATCH" if table_to_hex(gkl) == RULES["GKL"][0] else "MISMATCH")

# locate the differing nibble between the two maj strings
a, b = RULES["maj_review"][0], RULES["maj_evemcomp"][0]
diffs = [(i, a[i], b[i]) for i in range(32) if a[i] != b[i]]
print("\nmaj review vs EvEmComp differing hex positions:", diffs)
for i, ca, cb in diffs:
    lo, hi = i * 4, i * 4 + 4
    print(f"  nibble {i} covers neighbourhood indices {lo}..{hi-1}")
    for k in range(lo, hi):
        nb = [(k >> (6 - j)) & 1 for j in range(7)]
        print(f"    idx {k:3d} nbhd {''.join(map(str,nb))} popcount {sum(nb)} -> majority says {1 if sum(nb)>=4 else 0}")

print()
print("=" * 78)
print("STEP 2 -- simulate every rule on 10,000 unbiased ICs at N=149")
print("=" * 78)
print(f"{'rule':<12} {'published':>10} {'measured':>10} {'diff':>8}   source")
for name, (h, p149, p599, p999, src) in RULES.items():
    tab = hex_to_table(h)
    m = performance(tab, n_ics=10000, steps=300, N=149, seed=12345)
    print(f"{name:<12} {p149:>10.3f} {m:>10.3f} {m-p149:>+8.3f}   {src}")

print()
print("=" * 78)
print("STEP 3 -- the discriminating test: naive (wrong) row pairing")
print("=" * 78)
print("If the two hex rows are mis-paired across rules, exp and par should score ~0.000.")
wrong_exp = "0505408305c90101" + "037755837bffb77f"   # exp row1 + par row2
wrong_par = "0504058705000f77" + "200b0efb94c7cff7"   # par row1 + exp row2
for nm, h in (("exp_wrongpair", wrong_exp), ("par_wrongpair", wrong_par)):
    m = performance(hex_to_table(h), n_ics=2000, steps=300, seed=7)
    print(f"  {nm:<16} measured P149 = {m:.3f}")

print()
print("=" * 78)
print("STEP 4 -- particle2 anomaly: does performance rise with N?")
print("=" * 78)
for nm in ("par", "particle1", "particle2", "GKL"):
    h, p149, p599, p999, src = RULES[nm]
    tab = hex_to_table(h)
    row = []
    for NN, steps in ((149, 300), (599, 1200), (999, 2000)):
        m = performance(tab, n_ics=1000, steps=steps, N=NN, seed=99)
        row.append(m)
    print(f"  {nm:<10} measured {row[0]:.3f} {row[1]:.3f} {row[2]:.3f}   published {p149:.3f} {p599:.3f} {p999:.3f}")
