"""
Hadamard matrix construction attack.

H is Hadamard of order n iff H is n×n with entries +/-1 and H H^T = n I.

Sylvester construction: orders 2^k for all k.
Paley I: order p+1 where p prime ≡ 3 mod 4.
Paley II: order 2(p+1) where p prime ≡ 1 mod 4.
Williamson-type: order 4t for t with four matching ±1 sequences (Williamson 1944).
Turyn-type: order 4(2k+1) via Williamson-Turyn.

Demonstrate: build Sylvester (orders 2, 4, 8, 16, 32). Verify orthogonality.
Build Paley I for small primes p ≡ 3 mod 4: p = 3, 7, 11, 19, 23. Orders
4, 8, 12, 20, 24. Verify.

Smallest open orders historically:
- 1893–1933: 92, 116, 156, 172, 184, 188, 232, 236, 260, 268 ...
- Paley/Sylvester resolved many. Williamson + variants resolved many more.
- 1993: 428 was open. 2005: 668 resolved by Kharaghani-Tayfeh-Rezaie.
- The current frontier of "smallest open n where H_{4n} not yet constructed"
  was 668 then 716; per the batch prompt, smallest open updated regularly.
- (We don't claim a current frontier without checking; we report what we
  can construct here and which classical orders are known.)
"""
import numpy as np


def sylvester(k):
    """Sylvester Hadamard of order 2^k."""
    H = np.array([[1]])
    for _ in range(k):
        H = np.block([[H, H], [H, -H]])
    return H


def is_hadamard(H):
    n = H.shape[0]
    if H.shape != (n, n):
        return False
    if not np.all(np.isin(H, [1, -1])):
        return False
    return np.array_equal(H @ H.T, n * np.eye(n, dtype=int))


def quadratic_residues(p):
    """Return set of quadratic residues mod p (excluding 0)."""
    return {(x * x) % p for x in range(1, p)}


def chi(a, p, qr):
    """Legendre symbol-like: 0 if a==0, 1 if QR, -1 otherwise."""
    a = a % p
    if a == 0:
        return 0
    return 1 if a in qr else -1


def paley_I(p):
    """Paley type I: p prime, p ≡ 3 mod 4. Construct H of order p+1.
    Form: H = [[1, 1...1], [1, S+I]] where S_{ij} = chi(i-j, p) for i,j in F_p.
    Wait, the classical Paley I:
      Q = (q_{ij}) with q_{ij} = chi(i-j) for i, j in F_p
      For p ≡ 3 mod 4, Q is skew, Q^T = -Q.
      H = I_{p+1} + [[0, e^T], [-e, Q]] where e = (1,...,1)^T... messy.
    Easier: define
      H[0,0] = 1, H[0, j+1] = 1 for j=0..p-1
      H[i+1, 0] = -1 for i=0..p-1
      H[i+1, j+1] = chi(j-i) for i != j, and chi gives 0 only at i==j; set
        H[i+1, i+1] = 1.
    For p ≡ 3 mod 4, this gives a Hadamard matrix of order p+1.
    """
    assert p % 4 == 3
    qr = quadratic_residues(p)
    n = p + 1
    H = np.zeros((n, n), dtype=int)
    H[0, 0] = 1
    for j in range(p):
        H[0, j + 1] = 1
        H[j + 1, 0] = -1
    for i in range(p):
        for j in range(p):
            if i == j:
                H[i + 1, j + 1] = 1
            else:
                H[i + 1, j + 1] = chi(j - i, p, qr)
    return H


def main():
    print("Sylvester orders 2..32:")
    for k in range(1, 6):
        H = sylvester(k)
        ok = is_hadamard(H)
        print(f"  order {2**k:>3}: Hadamard={ok}")
    print()
    print("Paley I for primes p = 3 (mod 4), gives orders 4, 8, 12, 20, 24, 32, 44, 48, 60, ...")
    primes_3mod4 = [3, 7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83]
    for p in primes_3mod4:
        H = paley_I(p)
        ok = is_hadamard(H)
        order = p + 1
        print(f"  p={p:>3} -> order {order:>3}: Hadamard={ok}")
    print()
    # combinatorial gap: orders divisible by 4 not covered by Sylvester or Paley I.
    sylvester_orders = {2, 4, 8, 16, 32, 64, 128, 256, 512, 1024}
    paley_orders = {p + 1 for p in primes_3mod4 + [103, 107, 127, 131, 139, 151, 163, 167]
                    if all(p % q for q in range(2, int(p**0.5) + 1))}
    print("Orders 4..200 divisible by 4 not produced by Sylvester or Paley I:")
    missing = []
    for n in range(4, 201, 4):
        if n in sylvester_orders or n in paley_orders:
            continue
        missing.append(n)
    print(f"  count: {len(missing)}")
    print(f"  list: {missing}")


if __name__ == "__main__":
    main()
