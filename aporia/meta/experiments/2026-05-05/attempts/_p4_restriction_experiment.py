"""
P4 / Restriction (Stein) conjecture: numerical extension operator on
S^1 (n=2) and S^2 (n=3) to verify Tomas-Stein scaling and probe the
gap to the conjectured endpoint.

In n=2: Stein-Tomas endpoint is (p, q) = (2, 6). Full Stein conjecture
(q > 4, p adjusted) is known (Fefferman 1970 / Carleson-Sjolin).

In n=3: Stein-Tomas endpoint is (p, q) = (2, 4). Full conjecture
(q > 3, p adjusted) is OPEN.

This script computes E(g) for g = indicator of a delta-arc / delta-cap,
and measures ||E g||_{L^q} for several q.  It reports the empirical
scaling with delta and compares to the known/conjectured threshold.
"""
import numpy as np

# ---------- n = 2 (control) ----------
def extension_2d(arc_width, n_arc=400, R=40.0, N_grid=200):
    """E(g)(x) = int_{S^1} g(theta) exp(i x . (cos theta, sin theta)) dtheta,
    g = indicator of arc of width arc_width centered at theta=0."""
    thetas = np.linspace(-arc_width / 2, arc_width / 2, n_arc)
    dtheta = arc_width / n_arc
    xs = np.linspace(-R, R, N_grid)
    ys = np.linspace(-R, R, N_grid)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    E = np.zeros((N_grid, N_grid), dtype=complex)
    for t in thetas:
        E += np.exp(1j * (X * np.cos(t) + Y * np.sin(t)))
    E *= dtheta
    cell_area = (2 * R / N_grid) ** 2
    norms = {}
    for q in [2, 3, 4, 5, 6, 8]:
        norms[q] = (np.sum(np.abs(E)**q) * cell_area) ** (1 / q)
    g_l2 = np.sqrt(arc_width)
    g_lp = {p: arc_width ** (1/p) for p in [1, 2, 4]}  # ||1_{arc}||_{L^p(S^1)} = (arc_width)^(1/p)
    return norms, g_l2, g_lp

# ---------- n = 3 (open regime) ----------
def extension_3d(cap_radius, n_cap=400, R=20.0, N_grid=80):
    """E(g)(x) = int_{S^2} g(omega) exp(i x . omega) dsigma(omega),
    g = indicator of spherical cap of polar angle cap_radius around north pole.
    Use uniform sampling of cap via (z, phi) parametrization."""
    z = np.linspace(np.cos(cap_radius), 1.0, n_cap)  # cos(polar) ranges from cos(r) to 1
    phi = np.linspace(0, 2 * np.pi, n_cap, endpoint=False)
    Z, PHI = np.meshgrid(z, phi, indexing='ij')
    rho = np.sqrt(1 - Z**2)
    OX = (rho * np.cos(PHI)).ravel()
    OY = (rho * np.sin(PHI)).ravel()
    OZ = Z.ravel()
    weight = (1 - np.cos(cap_radius)) / n_cap * (2 * np.pi / n_cap)  # area element

    xs = np.linspace(-R, R, N_grid)
    ys = np.linspace(-R, R, N_grid)
    zs = np.linspace(-R, R, N_grid)
    X, Y, ZG = np.meshgrid(xs, ys, zs, indexing='ij')
    E = np.zeros((N_grid, N_grid, N_grid), dtype=complex)
    # vectorize over directions in batches
    batch = 200
    for i in range(0, len(OX), batch):
        ox = OX[i:i+batch]
        oy = OY[i:i+batch]
        oz = OZ[i:i+batch]
        phase = (X[..., None] * ox + Y[..., None] * oy + ZG[..., None] * oz)
        E += np.exp(1j * phase).sum(axis=-1)
    E *= weight
    cell_vol = (2 * R / N_grid) ** 3
    norms = {}
    for q in [2, 3, 4, 5, 6]:
        norms[q] = (np.sum(np.abs(E)**q) * cell_vol) ** (1 / q)
    cap_area = 2 * np.pi * (1 - np.cos(cap_radius))
    g_lp = {p: cap_area ** (1/p) for p in [1, 2, 4]}
    return norms, g_lp

print("=== n=2: extension of indicator of arc on S^1 ===")
print("Stein-Tomas endpoint in 2D: (p,q) = (2,6).  Full conjecture: q > 4.")
print()
deltas_2d = [np.pi, np.pi/2, np.pi/4, np.pi/8, np.pi/16]
print(f"{'arc_width':>12} {'L2(g)':>8} {'q=2':>10} {'q=3':>10} {'q=4':>10} {'q=5':>10} {'q=6':>10} {'q=8':>10}")
for d in deltas_2d:
    norms, g_l2, _ = extension_2d(d)
    print(f"{d:>12.5f} {g_l2:>8.4f} "
          f"{norms[2]:>10.4f} {norms[3]:>10.4f} {norms[4]:>10.4f} "
          f"{norms[5]:>10.4f} {norms[6]:>10.4f} {norms[8]:>10.4f}")

# Tomas-Stein ratio: ||E g||_{L^6} / ||g||_{L^2}, should be bounded
print()
print("Tomas-Stein ratio  ||E g||_{L^6} / ||g||_{L^2}  (should be bounded by absolute constant):")
for d in deltas_2d:
    norms, g_l2, _ = extension_2d(d)
    ratio = norms[6] / g_l2
    print(f"  arc={d:.5f}  ratio={ratio:.4f}")

print()
print("=== n=3: extension of indicator of cap on S^2 ===")
print("Stein-Tomas endpoint in 3D: (p,q) = (2,4).  Full conjecture: q > 3 (OPEN).")
print()
deltas_3d = [1.0, 0.5, 0.25, 0.125]
print(f"{'cap_radius':>12} {'L2(g)':>8} {'q=2':>10} {'q=3':>10} {'q=4':>10} {'q=5':>10} {'q=6':>10}")
for d in deltas_3d:
    norms, g_lp = extension_3d(d, n_cap=80, R=15.0, N_grid=60)
    g_l2 = g_lp[2]
    print(f"{d:>12.4f} {g_l2:>8.4f} "
          f"{norms[2]:>10.4f} {norms[3]:>10.4f} {norms[4]:>10.4f} "
          f"{norms[5]:>10.4f} {norms[6]:>10.4f}")

print()
print("3D Tomas-Stein ratio  ||E g||_{L^4} / ||g||_{L^2}  (should be bounded):")
for d in deltas_3d:
    norms, g_lp = extension_3d(d, n_cap=80, R=15.0, N_grid=60)
    ratio = norms[4] / g_lp[2]
    print(f"  cap_radius={d:.4f}  ratio={ratio:.4f}")
