"""Generate the pilot pool: 20 KNOWN, 40 ALIEN_LAWFUL, 40 MATCHED_NOISE.

Aliens are random compact rules drawn with a structural bias, KEPT ONLY IF
their planted property verifies exhaustively and they pass the analogue
check (not affine; < 0.5 agreement with every known template of the same
family on the same state space; not near-identity; not near-constant).
Nulls are KEPT ONLY IF the matched alien's planted property FAILS on them.
"""

from __future__ import annotations

import numpy as np

from hecate.alien import verify as V
from hecate.alien.systems import all_states, dims_of, step

P = 31


# ---- property specs: {"type": ..., args} evaluated by check_prop ----------

def check_prop(p, prop, tbl=None):
    t = prop["type"]
    tbl = tbl or V.table(p)
    if t == "conserved_linear":
        return V.conserved_linear(p, prop["w"], prop["mod"], 0, tbl)
    if t == "cyclic_linear":
        return V.conserved_linear(p, prop["w"], prop["mod"], 1, tbl)
    if t == "conserved_weights":
        w, mod = prop["w"], prop["mod"]
        tt, states, _ = tbl
        return all(sum(w[v] for v in s) % mod == sum(w[v] for v in states[tt[i]]) % mod
                   for i, s in enumerate(states))
    if t == "bijective":
        return V.bijective(p, tbl)
    if t == "all_orbits_fixed":
        ob = V.orbit_structure(p, tbl)
        return set(ob["periods"]) == {1} and ob["max_transient"] <= prop["max_transient"]
    if t == "has_cycle":
        return max(V.orbit_structure(p, tbl)["periods"]) >= prop["min_period"]
    if t == "long_cycle":
        return max(V.orbit_structure(p, tbl)["periods"]) >= prop["min_period"]
    if t == "commutes_swap":
        M = prop.get("M")
        if M is None:
            sig = lambda s: (s[1], s[0])
        else:
            Mi, mod = np.array(prop["Minv"]), prop["mod"]
            Mm = np.array(M)
            sig = lambda s: tuple(int(v) for v in (Mm @ np.array(
                [int(u) for u in (Mi @ np.array(s)) % mod][::-1])) % mod)
        return V.commutes_with(p, sig, tbl)
    if t == "diagonal_invariant":
        return V.invariant_set(p, lambda s: s[0] == s[1], tbl)
    raise ValueError(t)


# ---- helpers ----------------------------------------------------------------

def rand_graph(rng):
    n = 6
    order = rng.permutation(n)
    edges = set()
    for k in range(1, n):
        u, v = int(order[k]), int(order[rng.randint(0, k)])
        edges.add((min(u, v), max(u, v)))
    while len(edges) < 8:
        u, v = rng.choice(n, 2, replace=False)
        edges.add((int(min(u, v)), int(max(u, v))))
    return [list(e) for e in sorted(edges)]


def rand_poly(rng, nterms, maxdeg, two_var=True):
    terms = set()
    while len(terms) < nterms:
        i = rng.randint(0, maxdeg + 1)
        j = rng.randint(0, maxdeg + 1 - i) if two_var else 0
        if i + j >= 1:
            terms.add((i, j))
    return [[i, j, int(rng.randint(1, P))] for i, j in sorted(terms)]


def inv_matrix_mod(M, mod):
    """Inverse of an integer matrix mod a prime, or None."""
    n = len(M)
    A = [list(map(int, r)) + [int(i == j) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        piv = next((r for r in range(c, n) if A[r][c] % mod), None)
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        iv = pow(A[c][c], -1, mod)
        A[c] = [(v * iv) % mod for v in A[c]]
        for r in range(n):
            if r != c and A[r][c]:
                f = A[r][c]
                A[r] = [(a - f * b) % mod for a, b in zip(A[r], A[c])]
    return [row[n:] for row in A]


# ---- KNOWN ------------------------------------------------------------------

def known_pool(rng):
    out = []
    out += [{"family": "tab", "kind": "odometer"},
            {"family": "tab", "kind": "lfsr", "a": [int(v) for v in rng.randint(1, 5, 5)]},
            {"family": "tab", "kind": "oddeven_sort"},
            {"family": "tab", "kind": "median3"}]
    for k in ("diffusion", "bfs", "plurality", "threshold"):
        out.append({"family": "graph", "kind": k, "edges": rand_graph(rng)})
    blank = 3
    out.append({"family": "rewrite", "kind": "sort",
                "rules": [[[a, b], [b, a]] for a in range(4) for b in range(4) if a > b]})
    out.append({"family": "rewrite", "kind": "paircancel",
                "rules": [[[x, x], [blank, blank]] for x in range(3)] +
                         [[[blank, x], [x, blank]] for x in range(3)]})
    out.append({"family": "rewrite", "kind": "bracket",
                "rules": [[[0, 1], [blank, blank]]] + [[[blank, x], [x, blank]] for x in range(3)]})
    out.append({"family": "rewrite", "kind": "gravity",
                "rules": [[[2, x], [x, 2]] for x in (0, 1, 3)]})
    nop = ["aff", 2, 2, 2, 1, 0, 0]
    out.append({"family": "vm", "kind": "counter", "program": [
        ["aff", 0, 0, 0, 1, 0, 1], ["jnz", 0, 0], ["aff", 1, 1, 1, 1, 0, 1],
        ["jnz", 1, 0], ["aff", 2, 2, 2, 1, 0, 1], ["jmp", 0]]})
    out.append({"family": "vm", "kind": "fib", "program": [
        ["aff", 2, 0, 1, 1, 1, 0], ["aff", 0, 1, 1, 1, 0, 0], ["aff", 1, 2, 2, 1, 0, 0],
        ["jmp", 0], nop, nop]})
    out.append({"family": "vm", "kind": "mul_acc", "program": [
        ["jz", 1, 4], ["aff", 2, 2, 0, 1, 1, 0], ["aff", 1, 1, 1, 1, 0, 6], ["jmp", 0],
        ["jmp", 4], nop]})
    out.append({"family": "vm", "kind": "swap", "program": [
        ["aff", 0, 0, 1, 1, 1, 0], ["aff", 1, 0, 1, 1, 6, 0], ["aff", 0, 0, 1, 1, 6, 0],
        ["jmp", 0], nop, nop]})
    for k in ("rot90", "cat", "predprey", "phase_sync"):
        out.append({"family": "map", "kind": k})
    return out


# ---- ALIEN generators (return params, planted props, analogue note) --------

def g_tab_local(rng, mode, zero_p=0.4):
    n = 5
    D = [[[0 if rng.rand() < zero_p else int(rng.randint(1, 5)) for _ in range(5)]
          for _ in range(5)] for _ in range(n)]
    nb = [int((i + rng.randint(1, n)) % n) for i in range(n)]
    c = int(rng.randint(0, n))
    w = [int(v) for v in rng.randint(0, 5, n)]
    w[c] = int(rng.randint(1, 5))
    if sum(1 for v in w if v) < 3:
        w[(c + 1) % n] = int(rng.randint(1, 5))
        w[(c + 2) % n] = int(rng.randint(1, 5))
    p = {"family": "tab", "kind": "tab_local", "D": D, "nb": nb, "comp": c, "mode": mode, "w": w}
    if mode == "lin":
        props = [{"type": "conserved_linear", "w": w, "mod": 5}]
    elif mode == "cyc":
        props = [{"type": "cyclic_linear", "w": w, "mod": 5}]
    else:
        props = [{"type": "all_orbits_fixed", "max_transient": 20}]
    return p, props, "construction class: table-driven local update (+ linear compensation term)"


def g_tab_rev(rng):
    n = 5
    D = [[int(v) for v in rng.randint(0, 5, 5)] for _ in range(n)]
    nb = [int((i + rng.randint(1, n)) % n) for i in range(n)]
    order = [int(v) for v in rng.permutation(n)]
    return ({"family": "tab", "kind": "tab_rev", "D": D, "nb": nb, "order": order},
            [{"type": "bijective"}],
            "construction class: sequential invertible shears (reversible-update family)")


def g_graph_flow(rng):
    F = [[0] * 4 for _ in range(4)]
    for a in range(4):
        for b in range(a + 1, 4):
            v = int(rng.randint(-1, 2))
            F[a][b], F[b][a] = v, -v
    return ({"family": "graph", "kind": "graph_flow", "edges": rand_graph(rng), "F": F},
            [{"type": "conserved_linear", "w": [1] * 6, "mod": 1000}],
            "construction class: pairwise conservative exchange with a random exchange table")


def g_graph_attr(rng):
    G = [[int(v) for v in rng.randint(0, 4, 4)] for _ in range(4)]
    return ({"family": "graph", "kind": "graph_attr", "edges": rand_graph(rng), "G": G},
            [{"type": "all_orbits_fixed", "max_transient": 20}],
            "construction class: random table of (own value, neighbour sum mod 4)")


def g_rewrite(rng, variant):
    k = int(rng.choice([3, 4]))
    w = [int(v) for v in rng.randint(0, k, 4)]
    if len(set(w)) < 2:
        w[0] = (w[1] + 1) % k
    rules = []
    tries = 0
    while len(rules) < int(rng.randint(3, 6)) and tries < 500:
        tries += 1
        a, b, c, d = (int(v) for v in rng.randint(0, 4, 4))
        if (a, b) == (c, d) or any(r[0] == [a, b] for r in rules):
            continue
        if (w[a] + w[b]) % k == (w[c] + w[d]) % k:
            rules.append([[a, b], [c, d]])
    props = [{"type": "conserved_weights", "w": w, "mod": k}]
    props.append({"type": "all_orbits_fixed", "max_transient": 30, "primary": False} if variant == "term"
                 else {"type": "has_cycle", "min_period": 2, "primary": False})
    return ({"family": "rewrite", "kind": "rewrite", "rules": rules}, props,
            "construction class: random length-preserving 2-symbol rewrite rules")


def g_vm(rng, variant):
    w = [int(v) for v in rng.randint(1, 7, 3)]
    prog = []
    for _ in range(6):
        u = rng.rand()
        if variant == "lin":
            if u < 0.25:
                prog.append([str(rng.choice(["jz", "jnz"])), int(rng.randint(0, 3)), int(rng.randint(0, 6))])
            else:
                a, z = (int(v) for v in rng.choice(3, 2, replace=False))
                b = int(rng.randint(0, 3))
                g = [int(v) for v in rng.randint(0, 7, 7)]
                kk = int(rng.randint(1, 7))
                kz = (kk * w[a] * pow(w[z], -1, 7)) % 7
                prog.append(["mix", a, b, z, g, kk, kz])
        else:
            if u < 0.2:
                prog.append([str(rng.choice(["jz", "jnz"])), int(rng.randint(0, 3)), int(rng.randint(0, 6))])
            elif u < 0.6:
                prog.append(["aff", int(rng.randint(0, 3)), int(rng.randint(0, 3)),
                             int(rng.randint(0, 3)), int(rng.randint(1, 7)),
                             int(rng.randint(0, 7)), int(rng.randint(0, 7))])
            else:
                prog.append(["tab", int(rng.randint(0, 3)), int(rng.randint(0, 3)),
                             [int(v) for v in rng.permutation(7)]])
    p = {"family": "vm", "kind": "vm_" + variant, "program": prog}
    if variant == "lin":
        return p, [{"type": "conserved_linear", "w": [0] + w, "mod": 7}], \
            "construction class: random instruction table with compensated register updates"
    return p, [{"type": "long_cycle", "min_period": 60}], \
        "construction class: random instruction table (affine and table ops, conditional jumps)"


def g_map_sym(rng):
    return ({"family": "map", "kind": "poly_sym", "g": rand_poly(rng, 4, 3)},
            [{"type": "commutes_swap"}, {"type": "diagonal_invariant"}],
            "construction class: symmetrised random polynomial map mod 31")


def g_map_shear(rng):
    return ({"family": "map", "kind": "shear", "h1": rand_poly(rng, 3, 3, False),
             "h2": rand_poly(rng, 3, 3, False)},
            [{"type": "bijective"}],
            "construction class: composed polynomial shears mod 31 (standard-map/Henon-type family)")


def linmix(rng, base, props, mod, n):
    while True:
        M = [[int(v) for v in rng.randint(0, mod, n)] for _ in range(n)]
        Minv = inv_matrix_mod(M, mod)
        if Minv is not None and sum(1 for r in M for v in r if v) >= n * n - 1:
            break
    p = {"family": base["family"], "wrap": "linmix", "base": base, "M": M, "Minv": Minv, "mod": mod}
    out = []
    for pr in props:
        pr = dict(pr)
        if pr["type"] in ("conserved_linear", "cyclic_linear"):
            pr["w"] = [int(v) for v in (np.array(pr["w"]) @ np.array(Minv)) % mod]
        elif pr["type"] == "commutes_swap":
            pr.update(M=M, Minv=Minv, mod=mod)
        elif pr["type"] == "diagonal_invariant":
            continue
        out.append(pr)
    return p, out


# ---- NULL generators ---------------------------------------------------------

def destroy(rng, alien):
    k = alien["kind"]
    q = dict(alien)
    if k == "tab_local":
        q["mode"] = None
    elif k == "tab_rev":
        q = {"family": "tab", "kind": "tab_local", "comp": 0, "mode": None, "w": [1] * 5,
             "D": [[list(map(int, rng.randint(0, 5, 5))) for _ in range(5)] for _ in range(5)],
             "nb": alien["nb"]}
    elif k == "graph_flow":
        q["F"] = [[int(v) for v in rng.randint(-1, 2, 4)] for _ in range(4)]
        q["F2"] = [[int(v) for v in rng.randint(-1, 2, 4)] for _ in range(4)]
    elif k == "graph_attr":
        q["G"] = [[int(v) for v in rng.randint(0, 4, 4)] for _ in range(4)]
    elif k == "rewrite":
        q["rules"] = [[r[0], [int(v) for v in rng.randint(0, 4, 2)]] for r in alien["rules"]]
    elif k == "vm_lin":
        q["program"] = [ins if ins[0] != "mix" else ins[:6] + [int(rng.randint(0, 7))]
                        for ins in alien["program"]]
    elif k in ("poly_sym", "shear"):
        q = {"family": "map", "kind": "poly_free", "g1": rand_poly(rng, 4, 3), "g2": rand_poly(rng, 4, 3)}
    else:
        raise ValueError(k)
    return q


# ---- analogue check ---------------------------------------------------------

def analogue_ok(p, known_same_family, tbl):
    fam = p["family"]
    if fam in ("tab", "map") and V.is_affine(p, 5 if fam == "tab" else P, tbl):
        return False, "affine"
    ob = V.orbit_structure(p, tbl)
    if ob["fixed_fraction"] > 0.6:
        return False, "near-identity"
    if len(set(tbl[0].tolist())) / len(tbl[0]) < 0.02:
        return False, "near-constant"
    for kn in known_same_family:
        kq = dict(kn)
        if fam == "graph":
            kq["edges"] = (p.get("base") or p)["edges"] if "edges" in (p.get("base") or p) else kn["edges"]
        a = float(np.mean(tbl[0] == V.table(kq)[0]))
        if a >= 0.5:
            return False, f"agrees {a:.2f} with known {kn['kind']}"
    return True, "no template agreement >= 0.5; not affine; not near-identity/constant"
