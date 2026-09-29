I wrote the replication code, but I could not run it, so I have no empirical numbers. Bash is blocked in this session (don't-ask mode), and a subagent was blocked the same way. Everything below is exact analysis only. I did not open any Ensorain file, so I have made no comparison with their results.

Deliverables are in /home/jcraig/fabric-work/worker.ubu002/attempts/att-32409eb521dc/out/: suff_replica.py (the code) and REPORT.txt (this report). Running `python3 suff_replica.py` should take well under 1 CPU-minute and would give the table and settle C2 and C3.

```
C1  CONFIRMED (analytic, exact).
    STAT(3) does exactly the same operations as the W2 Bayes predictor:
    p=0.5 for t<3, then the same KT counts on the same true context.
    The excess is exactly 0.0 for every seed, not just 0 up to rounding.

C2  NOT TESTED (no run). Analytic support only.
    Each seed's data are drawn exactly from the order-3 Jeffreys (Beta(.5,.5))
    mixture m3, so the expected excess of STAT(k) is KL(m3 || mk), which is >= 0.
    A rough estimate that assumes equal context splits gives
    k=4 ~.006, k=6 ~.033, k=8 ~.094 (from I(n) ~ 0.5 log2 n - 0.40).
    Uneven context frequencies push these down, so the reported
    .004/.017/.039 is plausible but not verified.

C3  PARTIAL.
    "No k reaches Bayes": CONFIRMED (analytic).
    Any context that contains a 0 pins the hidden state exactly. Only the
    all-ones context 1^k leaves it ambiguous. With (A,B) mass updated by
    (A,B) -> (B, A/2) per trailing 1, the excess with infinite data is
      P(1^k) * [h(q_k/2) - q_k]:
      k:        0      1      2      3      4      6      8
      floor   .2516  .2075  .1258  .1038  .0629  .0315  .0157
      reported .252   .211   .131   .110   .075   .060   .075
    For k<=3, the reported values sit just above this floor, by about the
    expected finite-sample KT cost.
    For k=6 and 8 the gaps are ~.029 and ~.059. That is about 4-6 bits per
    context, which fits KT regret on roughly 20 to 55 contexts.
    An interior optimum near k=6 is therefore plausible, but it is NOT
    numerically verified.

C4  CONFIRMED (analytic).
    After the first 0 the forward filter knows the state exactly, so the
    expected loss per symbol is P(A) * 1 bit = 2/3. I did not run the
    T=60000 check; its expected sampling sd is ~.003.
```

The code, as written to suff_replica.py:
```
import math, random
L2 = math.log(2)
def nll(p1, x):
    p = p1 if x == 1 else 1.0 - p1
    return -math.log(p) / L2
def gen_w2(rng, T):
    theta = [rng.betavariate(0.5, 0.5) for _ in range(8)]
    xs = [rng.randrange(2) for _ in range(3)]
    while len(xs) < T:
        c = xs[-3]*4 + xs[-2]*2 + xs[-1]
        xs.append(1 if rng.random() < theta[c] else 0)
    return xs
def gen_even(rng, T):
    s = 'A' if rng.random() < 2/3 else 'B'; xs = []
    for _ in range(T):
        if s == 'A':
            if rng.random() < 0.5: xs.append(0)
            else: xs.append(1); s = 'B'
        else: xs.append(1); s = 'A'
    return xs
def bayes_w2(xs):
    c0 = [0]*8; c1 = [0]*8; out = []
    for t, x in enumerate(xs):
        if t < 3: p = 0.5
        else:
            c = xs[t-3]*4 + xs[t-2]*2 + xs[t-1]
            p = (c1[c] + 0.5) / (c0[c] + c1[c] + 1)
            if x: c1[c] += 1
            else: c0[c] += 1
        out.append(nll(p, x))
    return out
def bayes_even(xs):
    pA = 2/3; out = []
    for x in xs:
        out.append(nll(0.5*pA + (1 - pA), x))
        if x == 0: pA = 1.0
        else:
            a = 1 - pA; b = 0.5*pA      # B-1->A ; A-1->B
            pA = a / (a + b)
    return out
def stat(xs, k):
    cnt = {}; out = []
    for t, x in enumerate(xs):
        if t < k: p = 0.5
        else:
            ctx = tuple(xs[t-k:t]); c0, c1 = cnt.get(ctx, (0, 0))
            p = (c1 + 0.5) / (c0 + c1 + 1)
            cnt[ctx] = (c0 + (x == 0), c1 + (x == 1))
        out.append(nll(p, x))
    return out
KS = [0,1,2,3,4,6,8]; T = 4000; SEEDS = range(1, 17); res = {}
for w, gen, bay in [('W2', gen_w2, bayes_w2), ('Even', gen_even, bayes_even)]:
    for k in KS: res[(w,k)] = []
    for s in SEEDS:
        xs = gen(random.Random(s), T); b = sum(bay(xs)) / T
        for k in KS: res[(w,k)].append(sum(stat(xs, k)) / T - b)
print('world  ' + ''.join('%10s' % ('k=%d' % k) for k in KS))
for w in ['W2', 'Even']:
    print('%-6s ' % w + ''.join('%10.5f' % (sum(res[(w,k)])/16) for k in KS))
print('W2 k=3 max |excess| over seeds: %.3e' % max(abs(v) for v in res[('W2',3)]))
for w in ['W2', 'Even']:
    print(w, 'min/max over seeds:', ' '.join('k%d:[%.4f,%.4f]' % (k, min(res[(w,k)]), max(res[(w,k)])) for k in KS))
for s in [1, 2, 3]:
    xs = gen_even(random.Random(s), 60000); b = bayes_even(xs)
    print('Even T=60000 seed %d: Bayes log-loss last half = %.5f (2/3=%.5f)' % (s, sum(b[30000:])/30000, 2/3))
```

The spec does not say how to handle these points, so these are my choices:
- **W2 random draws:** the 8 thetas are drawn from the seeded generator before the first 3 symbols.
- **Bayes for t<3:** the W2 Bayes predictor predicts 0.5 for the first 3 symbols.
- **Even random draws:** the starting state uses one draw from the same seeded generator.

If Ensorain made different choices, the per-seed values will differ, but the 16-seed means should agree within noise.