"""W2-17 a9: single-byte founder variants at the substitutions seen in in-world side-0 chains (a8 diffs):
which single changes alone switch 7ae3 to side-0 copying? K2 method (a5.k2), NP=30, copy errors off."""
import json, pathlib, random, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = [sys.argv[0], "30"]
import a5_k2_morphs as A  # noqa: E402
C = A.C
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
rng = random.Random("W2-17-a9")
subs = [(37, 0x00), (37, 0x81), (37, 0x85), (37, 0xA1), (44, 0xAC), (44, 0xCC), (0, 0x40), (40, 0x04), (54, 0xEE),
        (50, 0xA2), (6, 0x00), (2, 0x40), (48, 0xA0), (59, 0x78)]
out = {}
for p, v in subs:
    g = bytearray(F); g[p] = v
    m = A.k2(r, bytes(g), rng)
    out["%d:%02x>%02x" % (p, F[p], v)] = m
    R, Z = m["RAND"], m["ZERO"]
    print("%d:%02x>%02x" % (p, F[p], v), "RAND c0 %.2f c1 %.2f k0 %.2f k1 %.2f mB %.2f mA %.2f | ZERO c0 %.2f c1 %.2f mB %.2f" %
          (R["conv0"], R["conv1"], R["keep0"], R["keep1"], R["m_base"], R["m_atomic"], Z["conv0"], Z["conv1"], Z["m_base"]))
(HERE / "a9_switch_sites.json").write_text(json.dumps(out, indent=1))
