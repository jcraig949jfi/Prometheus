def solve(api, lib, budget):
    floor = 60000
    best = lib.g2_escape(api, api["init_parities"], floor)
    api["submit_best"](best, "g2_final")
    return best
