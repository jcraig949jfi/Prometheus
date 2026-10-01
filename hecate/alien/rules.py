"""Neutral, exact rule text for the revealed-law task (T7). No mechanism
names, no conventional variable names: positions are p0, p1, ...; tables are
printed in full. Every rule is fully specified: a reader can simulate it.
"""

from __future__ import annotations


def _poly(coef, a, b):
    terms = []
    for i, j, c in coef:
        t = f"{c}"
        if i:
            t += f"*{a}^{i}" if i > 1 else f"*{a}"
        if j:
            t += f"*{b}^{j}" if j > 1 else f"*{b}"
        terms.append(t)
    return " + ".join(terms)


def describe(p) -> str:
    fam, k = p["family"], p.get("kind")
    if fam == "tab":
        if k == "tab_local":
            lines = ["All arithmetic is mod 5. For each position i compute an increment "
                     "d_i = T_i[p_i][p_{n(i)}] with n = " + str(p["nb"]) + " and tables:"]
            for i, T in enumerate(p["D"]):
                lines.append(f"  T_{i} = {T}   (row = value of p_{i}, column = value of p_{p['nb'][i]})")
            if p.get("mode") in ("lin", "cyc"):
                c, w = p["comp"], p["w"]
                tgt = 0 if p["mode"] == "lin" else 1
                lines.append(f"Then REPLACE d_{c} by the unique value in 0..4 with "
                             f"sum_i w_i*d_i = {tgt} (mod 5), where w = {w}.")
            lines.append("New state: p_i + d_i (mod 5) for every i.")
            return "\n".join(lines)
        if k == "tab_rev":
            lines = [f"All arithmetic is mod 5. Update positions one at a time in the order {p['order']}, "
                     "each using the current (possibly already updated) values: "
                     "p_i := p_i + U_i[p_{n(i)}] with n = " + str(p["nb"]) + " and"]
            for i, U in enumerate(p["D"]):
                lines.append(f"  U_{i} = {U}")
            return "\n".join(lines)
        if k == "odometer":
            return ("Add 1 to p0 (mod 5). If p0 became 0, add 1 to p1 (mod 5); if p1 became 0, "
                    "add 1 to p2; and so on up to p4.")
        if k == "lfsr":
            return (f"New state is (p1, p2, p3, p4, x) where x = sum_i a_i*p_i mod 5 with a = {p['a']}.")
        if k == "oddeven_sort":
            return ("Compare-and-order pairs (p0,p1) and (p2,p3): if the left value is larger, exchange them. "
                    "Then do the same for (p1,p2) and (p3,p4).")
        if k == "median3":
            return ("Every position becomes the middle value (median) of itself and its two ring "
                    "neighbours (p_{i-1}, p_i, p_{i+1}, indices mod 5), all computed from the old state.")
    if fam == "graph":
        links = ", ".join(f"{u}-{v}" for u, v in p["edges"])
        if k in ("graph_flow", "diffusion"):
            if k == "diffusion":
                t = "t = +1 if value(v) > value(u), -1 if value(v) < value(u), else 0"
                tv = "value(v) changes by -t"
            else:
                t = f"t = F[value(u)][value(v)] with F = {p['F']}"
                tv = ("value(v) changes by -t" if "F2" not in p else
                      f"value(v) changes by t2 = F2[value(u)][value(v)] with F2 = {p['F2']}")
            return (f"Links in this order: {links}. Process links one by one, using current values. "
                    f"For link u-v: {t}; value(u) changes by +t and {tv}, but only if both "
                    "results stay within 0..3 (otherwise the link does nothing).")
        if k == "graph_attr":
            return (f"Links: {links}. Every site x becomes G[value(x)][S mod 4], where S is the sum of "
                    f"the values of the sites linked to x (old state), with G = {p['G']}.")
        if k == "bfs":
            return (f"Links: {links}. Site 0 becomes 0. Every other site becomes the minimum of its own value "
                    "and (1 + the value of each linked site), capped at 3 (old state used).")
        if k == "plurality":
            return (f"Links: {links}. Each site looks at its own value and the values of linked sites; it "
                    "keeps its value if that value is among the most frequent, else takes the smallest "
                    "most-frequent value (old state used).")
        if k == "threshold":
            return (f"Links: {links}. A site with at least one linked site of value >= 2 increases by 1 "
                    "(max 3); otherwise it decreases by 1 (min 0) (old state used).")
    if fam == "rewrite":
        L = "WXYZ"
        rules = "; ".join(f"{L[a]}{L[b]} -> {L[c]}{L[d]}" for (a, b), (c, d) in p["rules"])
        return ("Scan positions from left to right. At the first position where some rule applies "
                "(trying rules in the listed order at each position), replace that pair and stop; if no "
                f"rule applies anywhere, the string is unchanged. Rules: {rules}.")
    if fam == "vm":
        out = ["The state is (c, a0, a1, a2), c in 0..5, a in 0..6, arithmetic mod 7. "
               "Execute instruction number c from the list below; unless it says otherwise, "
               "c then becomes c+1 (mod 6)."]
        for i, ins in enumerate(p["program"]):
            op = ins[0]
            if op == "mix":
                _, a, b, z, g, k1, kz = ins
                out.append(f"  {i}: t = H[a{b}] with H = {g}; a{a} += {k1}*t; a{z} -= {kz}*t")
            elif op == "aff":
                _, a, b, z, k1, k2, e = ins
                out.append(f"  {i}: a{a} = {k1}*a{b} + {k2}*a{z} + {e}")
            elif op == "tab":
                _, a, b, T = ins
                out.append(f"  {i}: a{a} = T[a{b}] with T = {T}")
            elif op == "jz":
                out.append(f"  {i}: if a{ins[1]} == 0 then c = {ins[2]}")
            elif op == "jnz":
                out.append(f"  {i}: if a{ins[1]} != 0 then c = {ins[2]}")
            elif op == "jmp":
                out.append(f"  {i}: c = {ins[1]}")
        return "\n".join(out)
    if fam == "map":
        if k == "poly_sym":
            return (f"Arithmetic mod 31. New state (g(p0,p1), g(p1,p0)) where g(a,b) = {_poly(p['g'], 'a', 'b')}.")
        if k == "poly_free":
            return (f"Arithmetic mod 31. New state (g1(p0,p1), g2(p0,p1)) where g1(a,b) = "
                    f"{_poly(p['g1'], 'a', 'b')} and g2(a,b) = {_poly(p['g2'], 'a', 'b')}.")
        if k == "shear":
            return (f"Arithmetic mod 31. First p0 := p0 + h1(p1) with h1(b) = {_poly(p['h1'], 'b', 'x')}; "
                    f"then p1 := p1 + h2(p0) using the new p0, with h2(a) = {_poly(p['h2'], 'a', 'x')}.")
        if k == "rot90":
            return "Arithmetic mod 31. New state (-p1, p0)."
        if k == "cat":
            return "Arithmetic mod 31. New state (2*p0 + p1, p0 + p1)."
        if k == "predprey":
            return ("Integers, floor division. p0' = p0 + floor(p0*(12 - p1)/12), p1' = p1 + floor(p1*(p0 - 12)/12), "
                    "each clipped to 0..30.")
        if k == "phase_sync":
            return ("Values on a circle of 31. Each position moves one step toward the other along the "
                    "shorter way round (no move if equal; ties go upward).")
    raise ValueError(f"no description for {fam} {k}")
