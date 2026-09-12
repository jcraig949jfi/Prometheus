import numpy as np, padasip as pa
np.random.seed(1)
N = 6000; h1 = np.array([0.5, -0.3, 0.2, 0.1]); h2 = np.array([-0.2, 0.4, 0.1, -0.3])
x = np.random.randn(N); X = pa.input_from_history(x, 4)
d = np.concatenate([X[:len(X)//2] @ h1, X[len(X)//2:] @ h2]) + 0.01 * np.random.randn(len(X))
ok = True
for name, f in (("NLMS", pa.filters.FilterNLMS(n=4, mu=0.5, w="zeros")), ("RLS", pa.filters.FilterRLS(n=4, mu=0.99, w="zeros"))):
    y, e, w = f.run(d, X)
    e1 = np.abs(w[len(X)//2 - 1] - h1).max(); e2 = np.abs(w[-1] - h2).max()
    print("%s before-change w=%s err=%.4f | after-change w=%s err=%.4f" % (name, np.round(w[len(X)//2 - 1], 3), e1, np.round(w[-1], 3), e2))
    ok = ok and e1 < 0.02 and e2 < 0.02
print("RESULT", "OK" if ok else "FAIL")
