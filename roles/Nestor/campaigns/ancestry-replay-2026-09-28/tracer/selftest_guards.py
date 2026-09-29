"""Guards required by the operator's post-ARC3 directive (2026-09-28):
(1) PAIRING (s4, the C9-D24 lesson): a counterfactual that changes anything outside its declared intervention is REFUSED
    (NotPaired); a correct one passes; LDIR-enabled masks (RNG-consuming copy noise) are refused as unpaired.
(2) PAINTING / SOURCE DIVERSITY (s6): the diagnostic separates a true copy (K1: 8 loci from 8 distinct sources) from
    painting (K37: 8 loci written from ONE source byte by a loop), with performer/instruction counts."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import interventions as I, npe_fixtures as NF, check_fixtures as CF, run_trace as RT


def div_of(f):
    r = I.Run(CF.pre_of(f))
    final = [r.cell(j) for j in range(NF.N)]
    return RT.diversity(final, r.last, r.voff, NF.N, "b")


def main():
    fx = {f["name"]: f for f in NF.fixtures()}
    pre = CF.pre_of(fx["K1_copy_shifted"])
    ok_good = True
    try:
        c = pre.copy(); c.g[0][3] ^= 1; I.assert_paired(pre, c, {("G", 0)})
    except I.NotPaired:
        ok_good = False
    refused = 0
    for mutate in (lambda c: c.g[1].__setitem__(3, c.g[1][3] ^ 1),          # other genome touched
                   lambda c: setattr(c, "budget", c.budget - 1),            # interaction parameter changed
                   lambda c: setattr(c, "mask", c.mask | 0x20)):            # RNG-consuming LDIR enabled
        c = pre.copy(); c.g[0][3] ^= 1; mutate(c)
        try:
            I.assert_paired(pre, c, {("G", 0)})
        except I.NotPaired:
            refused += 1
    copy = div_of(fx["K1_copy_shifted"])
    code = NF.asm("""
        LD HL, 48
        LD A, (HL)
        LD DE, 8
        LD B, 8
    loop:
        LD (DE), A
        INC DE
        DEC B
        JRNZ loop
        HALT
    """)
    paint = div_of(NF.fx("K37_painting_one_source", NF.A_HALT, NF.half(code, NF.DATA_B), {}))
    res = {"pairing_correct_passes": ok_good, "pairing_violations_refused_3of3": refused == 3,
           "copy_8_loci_8_sources": copy["n_written"] >= 8 and copy["n_distinct_donor_sources"] == 8,
           "painting_8_loci_1_source": paint["n_written"] == 8 and paint["n_distinct_sources"] == 1
                                       and paint["top_source_share"] == 1.0 and paint["n_distinct_store_pcs"] == 1,
           "copy_diag": copy, "paint_diag": paint}
    res["pass"] = all(v for k, v in res.items() if not k.endswith("_diag"))
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parent / "pin"))
    sys.exit(main())
