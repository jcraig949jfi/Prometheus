"""W2-44 t5: (a) the CRW_1 design across frames: for every frame s, P_s + {JPNC at founder pos 61, operand low byte =
absolute side-0 address of the frame's LDIR (52+s)%64 (| 0x80 variant)} and the unconditional JP (C3) variant;
(b) founder-frame single/double-byte analogues: F+{43:81} (CNR_s22 route), F+{59:ED,60:B0} (CRW_78/XH2N chained LDIR),
F+{61:D2,62:34}; (c) dependence on the partner's byte 0 (chained LDIR re-reads src L := partner byte 0) using
random-genome partners and bank partners with byte 0 forced; (d) one-bit neighbourhood of the CRW_1 core: fraction of
the 512 one-bit mutants that keep the two-sided phenotype; (e) the in-world precursor states of CRW_1 (e33 creation).
python -B t5_family.py -> t5_family.json"""
import json, random, time
from common44 import *  # noqa
t0 = time.process_time()
out = {}
P300 = PAN[:300]


def mk(base, muts):
    g = bytearray(base)
    for p, v in muts.items():
        g[p % 64] = v
    return bytes(g)


def short(a):
    return {k: a[k] for k in ("keep_s0", "keep_s1", "conv_s0", "conv_s1", "m_base")}


# (a) frame family
fam = {}
for s in range(64):
    P = rot_of(F, s)
    ld = (52 + s) % 64
    row = {"P": short(A(P, P300)), "ldir_abs": ld}
    for nm, op, lo in (("JPNC", 0xD2, ld), ("JPNC|80", 0xD2, ld | 0x80), ("JP", 0xC3, ld)):
        x = mk(P, {61 + s: op, 62 + s: lo})
        row[nm] = short(A(x, P300))
    fam[s] = row
out["frame_family"] = fam
print("frame family (s: P m, JPNC conv0/conv1/m, JP conv0/conv1/m)")
for s, row in fam.items():
    print(s, row["P"]["m_base"], [row["JPNC"][k] for k in ("conv_s0", "conv_s1", "keep_s1", "m_base")],
          [row["JP"][k] for k in ("conv_s0", "conv_s1", "keep_s1", "m_base")], flush=True)
# (b) founder-frame analogues (full panel)
FA = {"F": F, "F+43:81": mk(F, {43: 0x81}), "F+59:ED,60:B0": mk(F, {59: 0xED, 60: 0xB0}),
      "F+61:D2,62:34": mk(F, {61: 0xD2, 62: 0x34}), "F+61:C3,62:34": mk(F, {61: 0xC3, 62: 0x34}),
      "F+44:AC": mk(F, {44: 0xAC}), "F+43:C3,44:AC": mk(F, {43: 0xC3, 44: 0xAC}),
      "P46": rot_of(F, 46), "P46+43:D2,44:A2(CRW1core)": mk(rot_of(F, 46), {43: 0xD2, 44: 0xA2}),
      "P46+30:5E": mk(rot_of(F, 46), {30: 0x5E}), "P62+41:81": mk(rot_of(F, 62), {41: 0x81})}
out["founder_frame_analogues"] = {k: {**A(v), "ldir_s0": conv_ldirs(v, 0, lim=100), "ldir_s1": conv_ldirs(v, 1, lim=100)} for k, v in FA.items()}
for k in FA:
    a = out["founder_frame_analogues"][k]
    print(k, short(a), a["ldir_s0"]["conv_ldir"], a["ldir_s1"]["conv_ldir"], flush=True)
# (c) partner byte-0 dependence
rng = random.Random("W2-44-c")
RP = [(bytes(rng.randrange(256) for _ in range(64)), C.ZERO, None, rng.randrange(2)) for _ in range(400)]
byte0 = collections.Counter(y[0] for y, cy, cx, s in PAN)
out["panel_partner_byte0_top"] = {"%02x" % k: v for k, v in byte0.most_common(6)}
dep = {}
for k in ("F", "F+44:AC", "F+43:C3,44:AC", "F+43:81", "F+59:ED,60:B0", "P46+43:D2,44:A2(CRW1core)"):
    x = FA[k]
    rnd = short(A(x, RP))
    forced = {}
    for b0 in (0x00, 0x80, 0x05, 0x40):
        pan2 = [(bytes([b0]) + y[1:], cy, cx, s) for y, cy, cx, s in P300]
        forced["%02x" % b0] = short(A(x, pan2))
    dep[k] = {"random_partners_ZERO": rnd, "bank_partner_byte0_forced": forced}
    print(k, "random", rnd, "forced", {b: (v["conv_s0"], v["conv_s1"]) for b, v in forced.items()}, flush=True)
out["partner_byte0"] = dep
# (d) one-bit neighbourhood of CRW_1 core and of C3+AC, AC
nb = {}
for k in ("P46+43:D2,44:A2(CRW1core)", "F+43:C3,44:AC", "F+44:AC", "F"):
    x = FA[k]
    cnt = collections.Counter()
    ms = []
    for j in range(64):
        for bit in range(8):
            y = bytearray(x); y[j] ^= 1 << bit
            a = A(bytes(y), PAN[:120])
            two = a["conv_s0"] >= 0.8 and a["conv_s1"] >= 0.6
            s0 = a["conv_s0"] >= 0.8
            s1 = a["conv_s1"] >= 0.6
            cnt["two-sided" if two else ("side0" if s0 else ("side1" if s1 else "none"))] += 1
            ms.append(a["m_base"])
    nb[k] = {"classes": dict(cnt), "mean_m": round(sum(ms) / len(ms), 3)}
    print(k, nb[k], flush=True)
out["one_bit_neighbourhood"] = nb
# (e) precursor states of CRW_1 (W2-35 s1_out e33 i112 creation, and the e33 created genome)
ev = [e for e in json.loads((W2 / "W2-35_rotation_leak" / "s1_out" / "CRW_1.json").read_text())["events"]
      if e["e"] == 33 and e["i"] == 112]
pre = {}
for e in ev:
    for key in ("g", "partner_g", "victim_old_g"):
        x = bytes.fromhex(e[key])
        pre["e33v%d_%s" % (e["vside"], key)] = {"frame": list(frame(x)), **short(A(x))}
x = bytes.fromhex([e for e in ev if e["vside"] == 0][0]["g"])
y = bytearray(x); y[44] = 0xA2
pre["e33_created_with_44=a2"] = {"frame": list(frame(bytes(y))), **short(A(bytes(y)))}
out["crw1_precursors"] = pre
for k, v in pre.items():
    print(k, v)
out["_cpu_s"] = round(time.process_time() - t0, 1)
(HERE / "t5_family.json").write_text(json.dumps(out, indent=1))
print("cpu", out["_cpu_s"])
