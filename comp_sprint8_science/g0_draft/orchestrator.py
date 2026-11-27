def solve(api, lib, budget):
    floor = 60000
    P0 = api["init_parities"]
    best = lib.g0_full_search(api, P0, floor, 0.95)
    api["submit_best"](best, "g0_final")
    return best
