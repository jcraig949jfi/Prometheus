"""CRUCIBLE-B runner. Executes exactly PREREG_C_B.md section B: mined exact generator subsequences (from FIT oracle
paths) vs random macros with the same length multiset, as extra actions for kernel-aware search in the frozen T_7
harness. No distance model. Usage: python -m alien_circuitry.nursery.crucibles.crucible_b
"""
from __future__ import annotations
import collections, json, os, random, time
import numpy as np
from ...ac01d.corpus import build
from ...ac01d.evaluate import Context, write_result
from ...ac01d.baselines import hc, bootstrap_hc
from ...universe.metrics import Searcher
from ...gate2.navigation2 import Cost

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
K_MACROS = 6; LENGTHS = (2, 3, 4); N_FIT_PROBLEMS = 2000; FIT_SEED = 20260912; RANDOM_SEED = 20260913; N_RANDOM_DRAWS = 3; GEN = 3


def oracle_path(S: Searcher, D, succ_table, s, j):
    """Action sequence of the frozen oracle descent (D-1 successor with lowest out-degree, then action index)."""
    path = []; v = s; d0 = int(D[s, j])
    for _ in range(d0):
        best = None
        for a in range(GEN):
            u = int(succ_table[v, a])
            if u != v and D[u, j] == D[v, j] - 1 and (best is None or S.od[u] < S.od[best[1]]): best = (a, u)
        path.append(best[0]); v = best[1]
    return path


def mine_macros(paths):
    counts = collections.Counter()
    for p in paths:
        for L in LENGTHS:
            for i in range(len(p) - L + 1): counts[tuple(p[i:i + L])] += 1
    ranked = [m for m, _ in counts.most_common()]
    chosen = []
    for m in ranked:
        if any(m == c[:len(m)] or m == c[-len(m):] or c == m[:len(c)] or c == m[-len(c):] for c in chosen): continue
        chosen.append(m)
        if len(chosen) == K_MACROS: break
    return chosen, counts


def random_macros(lengths, exclude, seed):
    rng = random.Random(seed); out = []
    while len(out) < len(lengths):
        L = lengths[len(out)]; m = tuple(rng.randrange(GEN) for _ in range(L))
        if m in exclude or m in out: continue
        out.append(m)
    return out


class MacroWorld:
    """Wraps the frozen observer with an enlarged action set: generators + macros. Macro application is charged its
    length in transitions; path length counts generator steps."""
    def __init__(self, ctx: Context, macros):
        self.ctx = ctx; self.macros = list(macros); self.succ = ctx.M["succ"]; self.obs = ctx.obs; self.rank = ctx.rank; self.kmask = ctx.kmask; self.targets = ctx.targets

    def apply(self, s, m):
        v = s
        for a in m: v = int(self.succ[v, a])
        return v

    def children(self, s):
        """(child, generator_cost, path_steps, is_macro) for every action; no-op results excluded as in the distinct graph."""
        out = []
        for a in range(GEN):
            u = int(self.succ[s, a])
            if u != s: out.append((u, 1, 1, 0))
        for m in self.macros:
            u = self.apply(s, m)
            if u != s: out.append((u, len(m), len(m), 1))
        return out

    def dead(self, s, t): return s != t and (self.rank[s] < self.rank[t] or (self.kmask[s] & ~self.kmask[t]) != 0)

    def key(self, u, j, idx, is_macro):
        t = self.targets[j]
        if u == t: return (0, 0, 0, idx)
        if self.dead(u, t): return (2, 0, 0, idx)
        return (1, int(self.rank[u]) - int(self.rank[t]), is_macro, idx)  # macros after generators at equal key (frozen)

    def dfs(self, s0, j, Dcol, budget=40000):
        t = self.targets[j]; exp = exm = 0; visited = {s0}; traps = 0
        def kids(s):
            nonlocal exp, exm
            ch = self.children(s); exp += 1; exm += sum(c[1] for c in ch)
            keyed = sorted(((self.key(u, j, i, im), u, steps) for i, (u, cost, steps, im) in enumerate(ch)))
            return [(u, steps) for k, u, steps in keyed if k[0] != 2]
        if s0 == t: return {"solved": True, "path_len": 0, "excess": 0, "exp": 0, "exm": 0, "traps": 0}
        stack = [(s0, kids(s0), 0, 0)]; d0 = int(Dcol[s0])
        while stack:
            s, ch, i, depth = stack[-1]
            if i >= len(ch): stack.pop(); continue
            stack[-1] = (s, ch, i + 1, depth); u, steps = ch[i]
            if u in visited: continue
            visited.add(u)
            if Dcol[s] >= 0 and Dcol[u] < 0: traps += 1
            if u == t: return {"solved": True, "path_len": depth + steps, "excess": depth + steps - d0, "exp": exp, "exm": exm, "traps": traps}
            if exp > budget: break
            stack.append((u, kids(u), 0, depth + steps))
        return {"solved": False, "path_len": -1, "excess": -1, "exp": exp, "exm": exm, "traps": traps}

    def gbfs(self, s0, j, Dcol, budget=40000):
        import heapq
        t = self.targets[j]; exp = exm = 0; seen = {s0}; n = 0; traps = 0
        if s0 == t: return {"solved": True, "path_len": 0, "excess": 0, "exp": 0, "exm": 0, "traps": 0}
        heap = [((0,), 0, s0, 0)]; d0 = int(Dcol[s0])
        while heap:
            k, _, s, depth = heapq.heappop(heap); ch = self.children(s); exp += 1; exm += sum(c[1] for c in ch)
            for i, (u, cost, steps, im) in enumerate(ch):
                if u in seen: continue
                kk = self.key(u, j, i, im)
                if kk[0] == 2: continue
                seen.add(u); n += 1
                if Dcol[s] >= 0 and Dcol[u] < 0: traps += 1
                if u == t: return {"solved": True, "path_len": depth + steps, "excess": depth + steps - d0, "exp": exp, "exm": exm, "traps": traps}
                heapq.heappush(heap, (kk, n, u, depth + steps))
            if exp > budget: break
        return {"solved": False, "path_len": -1, "excess": -1, "exp": exp, "exm": exm, "traps": traps}


def evaluate(ctx, macros, name):
    D = ctx.U["D"]; out = {"name": name, "macros": [list(m) for m in macros], "sets": {}}
    W = MacroWorld(ctx, macros)
    for set_name in ("HELD_STATES", "HELD_TARGETS", "HELD_BOTH"):
        pl = ctx.probs[set_name]; ref = ctx.references(set_name); O = ref["oracle"]; kd = ref["KA-DFS"]
        res = {}
        for kind, fn in (("DFS", W.dfs), ("GBFS", W.gbfs)):
            R = [fn(s, j, D[:, j]) for s, j, d in pl]
            solved = np.array([r["solved"] for r in R]); tr = np.array([r["exm"] for r in R], float); st = np.array([r["exp"] for r in R], float)
            e = {"solve_rate": float(solved.mean()), "failures": int((~solved).sum()), "mean_transitions": float(tr.mean()), "mean_states": float(st.mean()),
                 "mean_excess": float(np.mean([r["excess"] for r in R if r["solved"]])) if solved.any() else None, "traps_taken": float(np.mean([r["traps"] for r in R]))}
            if solved.all():
                e["HC_D_transitions"] = hc(tr, O[:, 1], kd["trans"]); e["HC_D_transitions_CI95"] = bootstrap_hc(tr, O[:, 1], kd["trans"])
                e["HC_D_states"] = hc(st, O[:, 0], kd["states"])
            res[kind] = e
        res["references"] = {"oracle_transitions": float(O[:, 1].mean()), "KA-DFS_transitions": float(kd["trans"].mean()), "KA-DFS_excess": kd["excess"], "KA-GBFS_transitions": float(ref["KA-GBFS"]["trans"].mean()), "KA-GBFS_excess": ref["KA-GBFS"]["excess"]}
        out["sets"][set_name] = res
    return out


def run():
    t0 = time.perf_counter(); ctx = Context(per_set=300); U, M = ctx.U, ctx.M; D = U["D"]; S = ctx.S; succ = M["succ"]
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0) & (D >= 5); Sx, Jx = np.nonzero(fit)
    rng = np.random.default_rng(FIT_SEED); sel = rng.choice(len(Sx), N_FIT_PROBLEMS, replace=False)
    paths = [oracle_path(S, D, succ, int(Sx[i]), int(Jx[i])) for i in sel]
    mined, counts = mine_macros(paths)
    lengths = [len(m) for m in mined]
    out = {"prereg": "alien_circuitry/nursery/crucibles/PREREG_C_B.md @ d3b9533", "fit_problems": N_FIT_PROBLEMS, "fit_seed": FIT_SEED, "mined_macros": [list(m) for m in mined],
           "mined_counts": [counts[m] for m in mined], "top_20_subsequences": [[list(m), c] for m, c in counts.most_common(20)], "generator_names": list(U["gens"].keys()),
           "mean_fit_path_len": float(np.mean([len(p) for p in paths])), "arms": {}}
    out["arms"]["no_macros"] = evaluate(ctx, [], "no macros (KA only, sanity)")
    out["arms"]["mined"] = evaluate(ctx, mined, "mined macros")
    for d in range(N_RANDOM_DRAWS):
        rm = random_macros(lengths, set(mined), RANDOM_SEED + d); out["arms"][f"random_{d}"] = evaluate(ctx, rm, f"random macros draw {d}")
    # verdict per prereg
    def hcd(arm, s, kind="GBFS"): return out["arms"][arm]["sets"][s][kind].get("HC_D_transitions")
    def ci(arm, s, kind="GBFS"): return out["arms"][arm]["sets"][s][kind].get("HC_D_transitions_CI95")
    verdict = {}
    for kind in ("DFS", "GBFS"):
        ok_all = True; detail = {}
        for s in ("HELD_TARGETS", "HELD_BOTH"):
            m = hcd("mined", s, kind); r = [hcd(f"random_{d}", s, kind) for d in range(N_RANDOM_DRAWS)]
            if m is None or any(x is None for x in r): detail[s] = "failures present"; ok_all = False; continue
            rmean = float(np.mean(r)); c = ci("mined", s, kind); half = (c[1] - c[0]) / 2 if c else 1.0
            beats = (m - rmean) > half; detail[s] = {"mined": m, "random_mean": rmean, "random_draws": r, "ci_half_width": half, "beats_random_by_more_than_CI": beats}
            ok_all = ok_all and beats and m > 0
        if not ok_all: v = "B-KILL"
        elif all(detail[s]["mined"] >= 0.20 for s in ("HELD_TARGETS", "HELD_BOTH")): v = "B-PASS"
        else: v = "B-WEAK"
        verdict[kind] = {"verdict": v, "detail": detail}
    out["verdict"] = verdict; out["seconds"] = round(time.perf_counter() - t0, 1)
    p = write_result(out, "CRUCIBLE_B_macros"); print(p)
    print(json.dumps({"mined": out["mined_macros"], "counts": out["mined_counts"], "verdict": verdict}, indent=1, default=float))
    for arm, ev in out["arms"].items():
        for s, e in ev["sets"].items():
            for kind in ("DFS", "GBFS"):
                x = e[kind]; print(f"{arm:10} {s:12} {kind:4} solve {x['solve_rate']:.3f} fail {x['failures']} trans {x['mean_transitions']:.1f} excess {x['mean_excess']} HC_D {x.get('HC_D_transitions')}")
    return out


if __name__ == "__main__":
    run()
