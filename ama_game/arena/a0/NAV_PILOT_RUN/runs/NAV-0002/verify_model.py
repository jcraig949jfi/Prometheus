"""Cross-check the recovered model f(n) = 8 f(n-1) + 997 f(n-2) (mod 1009)
against held-out metered samples at n=100, 337, 600, then report the local scan."""
import json
P, A, B = 1009, 8, 997
s = {1: 10, 2: 44}
for n in range(3, 601):
    s[n] = (A * s[n-1] + B * s[n-2]) % P

held_out = {100: 312, 337: 713, 600: 89}   # independent metered sample() results
for n, v in held_out.items():
    print(f"n={n}: predicted={s[n]} observed={v} match={s[n]==v}")

hits = [n for n in range(1, 601) if s[n] == 848]
print("n in [1,600] with f(n) mod 1009 == 848:", hits, "count:", len(hits))
print("distinct residues attained on [1,600]:", len(set(s.values())))
print("848 attained anywhere in [1,600]:", 848 in set(s.values()))

# period of the state (f(n-1), f(n)) mod 1009, computed locally (no meter cost)
seen, st, per = {}, (s[1], s[2]), None
n = 2
while n < 20000:
    if st in seen:
        per = n - seen[st]
        break
    seen[st] = n
    nxt = (A * st[1] + B * st[0]) % P
    st = (st[1], nxt); n += 1
print("state period:", per)

# is 848 hit anywhere in a full period (i.e. is the gate vacuous or real)?
st, hit_full, k = (s[1], s[2]), None, 2
for i in range(per or 20000):
    if st[1] == 848:
        hit_full = k; break
    st = (st[1], (A*st[1] + B*st[0]) % P); k += 1
print("first n over the FULL period with f(n)==848:", hit_full)

json.dump({"model": {"a": A, "b": B, "c": 0, "modulus": P, "f1": 10, "f2": 44},
           "held_out_checks": {str(k): {"predicted": s[k], "observed": v} for k, v in held_out.items()},
           "hits_848_in_1_600": hits,
           "state_period": per,
           "first_848_over_full_period": hit_full,
           "values_1_to_600": [s[n] for n in range(1, 601)]},
          open("model_scan.json", "w"), indent=1)
