# Exhaustive check: total stopping time (steps to reach 1) for every n in [1,5489].
# Exact integer arithmetic only; no floating point anywhere.
N = 5489
BOUND = 238  # claim: every n in [1,N] reaches 1 in FEWER THAN 238 steps, i.e. steps <= 237

memo = {1: 0}
def steps(n):
    path = []
    m = n
    while m not in memo:
        path.append(m)
        m = m // 2 if m % 2 == 0 else 3 * m + 1
    s = memo[m]
    for v in reversed(path):
        s += 1
        memo[v] = s
    return memo[n]

worst = []
violations = []
for n in range(1, N + 1):
    s = steps(n)
    worst.append((s, n))
    if s >= BOUND:
        violations.append((n, s))

worst.sort(reverse=True)
print("range checked: [1, %d]  (exhaustive, %d integers)" % (N, N))
print("max steps:", worst[0][0], "at n =", worst[0][1])
print("top 8 (steps, n):", worst[:8])
print("count with steps >= %d:" % BOUND, len(violations))
print("violations:", violations[:10])
# also the sub-claims that are checkable
print("s3 n^3==n mod 6 for 1..2000:", all(pow(n,3,6)==n%6 for n in range(1,2001)))
print("s4 n^2>=2n for 2..2000:", all(n*n>=2*n for n in range(2,2001)))
print("s6 5^3-5 ==120:", 5**3-5 == 120)
print("s7 exists n<=2000 with n^2>2000:", any(n*n>2000 for n in range(1,2001)))
print("s5 forward (4|n -> n(n+1)/2 even) holds:", all((n*(n+1)//2)%2==0 for n in range(1,2001) if n%4==0))
cex = [n for n in range(1,2001) if (n*(n+1)//2)%2==0 and n%4!=0]
print("s5 CONVERSE counterexamples (n(n+1)/2 even but 4 does not divide n), first 10:", cex[:10], "count:", len(cex))
