"""F4: exact backtracking search for permutation-automaton trackers of RP (prereg s5.2 F4).

A tracker with n register states, window W: M_t = pi_{u_t}(M_{t-1}), u_t = (x_{t-W+1..t}) padded
with '#' before time 1; decoder psi(M_t, u_t) must equal the true parity p_t on every history of
length <= d (all histories have positive probability for 0 < q < 1, 0 < a < 1, so q and a do not
change the constraint set; the search is run once per (W, d) and reported for q in {.1, .3}).
Each pi_u is a partial injective map extended to a permutation (any partial injection extends).
Symmetry breaking: a new image is an already-used state or the single next fresh state.
Configurations (M, context, p) are expanded once at their minimal depth (a later visit has a
smaller remaining budget, hence a subset of the constraints).
"""
import sys
import time

SYMS = (0, 1, 2)  # 0, 1, R


class Capped(Exception):
    pass


def upd(p, x):
    return 0 if x == 2 else (p ^ 1 if x == 1 else p)


def tracker_exists(n, W, d, deadline):
    pad = (3,) * (W - 1)
    pi = {}       # (u, M) -> M'
    img = {}      # u -> set of used images
    psi = {}      # (M', u) -> p
    used = [1]    # number of states in use (state 0 = initial)
    queue = [(0, pad, 0, 0)]
    visited = {(0, pad, 0)}
    trail = []
    counter = [0]

    def undo(to_trail, to_q):
        while len(trail) > to_trail:
            e = trail.pop()
            if e[0] == "pi":
                _, key, v = e
                del pi[key]
                img[key[0]].discard(v)
            elif e[0] == "psi":
                del psi[e[1]]
            elif e[0] == "vis":
                visited.discard(e[1])
            elif e[0] == "used":
                used[0] -= 1
        del queue[to_q:]

    def rec(qi, xi):
        counter[0] += 1
        if (counter[0] & 1023) == 0 and time.process_time() > deadline:
            raise Capped()
        while qi < len(queue):
            M, ctx, p, dep = queue[qi]
            if dep >= d:
                qi += 1
                xi = 0
                continue
            while xi < 3:
                x = SYMS[xi]
                u = ctx + (x,) if W > 1 else (x,)
                key = (u, M)
                if key not in pi:
                    s_img = img.setdefault(u, set())
                    cands = [v for v in range(used[0]) if v not in s_img]
                    if used[0] < n:
                        cands.append(used[0])
                    for v in cands:
                        tl, ql = len(trail), len(queue)
                        pi[key] = v
                        s_img.add(v)
                        trail.append(("pi", key, v))
                        if v == used[0]:
                            used[0] += 1
                            trail.append(("used",))
                        if rec(qi, xi):
                            return True
                        undo(tl, ql)
                    return False
                M2 = pi[key]
                p2 = upd(p, x)
                k2 = (M2, u)
                if k2 in psi:
                    if psi[k2] != p2:
                        return False
                else:
                    psi[k2] = p2
                    trail.append(("psi", k2))
                ctx2 = u[1:] if W > 1 else ()
                c2 = (M2, ctx2, p2)
                if c2 not in visited:
                    visited.add(c2)
                    trail.append(("vis", c2))
                    queue.append((M2, ctx2, p2, dep + 1))
                xi += 1
            qi += 1
            xi = 0
        return True

    return rec(0, 0), counter[0]


def search_cell(W, d, cap_seconds, nmax=32):
    sys.setrecursionlimit(100000)
    t0 = time.process_time()
    deadline = t0 + cap_seconds
    out = {"W": W, "d": d, "cap_s": cap_seconds, "tried": []}
    for n in range(2, nmax + 1):
        try:
            ok, nodes = tracker_exists(n, W, d, deadline)
        except Capped:
            out["status"] = "CAPPED"
            out["last_excluded_n"] = n - 1
            out["cpu_s"] = time.process_time() - t0
            return out
        out["tried"].append((n, ok, nodes))
        if ok:
            out["status"] = "FOUND"
            out["n_min"] = n
            out["cpu_s"] = time.process_time() - t0
            return out
    out["status"] = "NOT_FOUND"
    out["last_excluded_n"] = nmax
    out["cpu_s"] = time.process_time() - t0
    return out


if __name__ == "__main__":
    W, d, cap = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    print(search_cell(W, d, cap))
