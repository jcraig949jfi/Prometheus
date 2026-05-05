"""
P3 / Kakeya: discrete 2D construction + box-counting dimension as
calibration anchor, plus 3D tube-incidence count as a quantitative
view of the Wolff-style obstruction.

In dim 2 the Kakeya conjecture is proved (dim = 2).  We expect a discrete
approximation of a Kakeya-like construction with K directions to have
box-counting dimension trending to 2 as K -> infinity.

In dim 3 the conjecture is OPEN; the Wolff hairbrush argument gives
lower bound 5/2.  This script does NOT push that bound.  It produces
a tube-incidence histogram on a 3D grid as a quantitative trace of
the structure that the Wolff argument exploits.
"""
import numpy as np

rng = np.random.default_rng(20260505)

# ---------- 2D part ----------
def kakeya_2d_grid(N, K):
    """Rasterize K unit segments in K directions on N x N grid.

    Each segment has length ~ N/2 (in pixels), direction theta_k = pi * k / K.
    Translate each segment to a position chosen to spread coverage.
    """
    grid = np.zeros((N, N), dtype=bool)
    cx, cy = N / 2, N / 2
    seg_len = N / 2 - 2
    n_pts = int(seg_len * 4)
    for k in range(K):
        theta = np.pi * k / K
        # offset each segment perpendicular to its direction to spread
        off = (k % 5 - 2) * (N / 12)
        ox = -np.sin(theta) * off
        oy = np.cos(theta) * off
        ts = np.linspace(-seg_len / 2, seg_len / 2, n_pts)
        xs = cx + ox + np.cos(theta) * ts
        ys = cy + oy + np.sin(theta) * ts
        ix = np.clip(np.floor(xs).astype(int), 0, N - 1)
        iy = np.clip(np.floor(ys).astype(int), 0, N - 1)
        grid[ix, iy] = True
    return grid

def box_count_dim(grid, scales):
    """Box-counting dimension estimate from log N(eps) vs log(1/eps) slope."""
    N = grid.shape[0]
    counts = []
    for s in scales:
        if N % s != 0:
            continue
        b = N // s
        # downsample by max-pool
        reshaped = grid.reshape(b, s, b, s)
        boxes = reshaped.any(axis=(1, 3))
        counts.append((s, boxes.sum()))
    log_inv_eps = np.log([N / s for s, _ in counts])
    log_n = np.log([n for _, n in counts])
    slope, intercept = np.polyfit(log_inv_eps, log_n, 1)
    return slope, counts

print("=== 2D Kakeya-ish construction, box-counting ===")
N = 256
scales = [1, 2, 4, 8, 16, 32, 64]
for K in [4, 8, 16, 32, 64, 128, 256]:
    grid = kakeya_2d_grid(N, K)
    measure = grid.sum() / grid.size
    slope, counts = box_count_dim(grid, scales)
    print(f"K={K:4d}  measure(fraction covered)={measure:.4f}  box-count dim={slope:.4f}")

# ---------- 3D part ----------
def random_directions_s2(K, rng):
    """K directions roughly uniform on S^2."""
    z = rng.uniform(-1, 1, K)
    phi = rng.uniform(0, 2 * np.pi, K)
    rho = np.sqrt(1 - z**2)
    return np.stack([rho * np.cos(phi), rho * np.sin(phi), z], axis=1)

def tube_incidence_3d(K, N_grid=64, delta=2):
    """Place K tubes (axis-aligned with random direction, centered) on N^3
    grid, tube radius `delta` cells.  Count multiplicities."""
    counts = np.zeros((N_grid, N_grid, N_grid), dtype=np.int32)
    dirs = random_directions_s2(K, rng)
    cx = cy = cz = N_grid / 2
    seg_len = N_grid / 2 - 2
    n_pts = int(seg_len * 4)
    ts = np.linspace(-seg_len / 2, seg_len / 2, n_pts)
    for d in dirs:
        # also offset perpendicular for spread
        # build orthonormal frame
        a = d
        if abs(a[2]) < 0.9:
            b = np.cross(a, [0, 0, 1])
        else:
            b = np.cross(a, [1, 0, 0])
        b /= np.linalg.norm(b)
        c = np.cross(a, b)
        ox, oy, oz = b * rng.uniform(-N_grid / 8, N_grid / 8) + c * rng.uniform(-N_grid / 8, N_grid / 8)
        xs = cx + ox + a[0] * ts
        ys = cy + oy + a[1] * ts
        zs = cz + oz + a[2] * ts
        ix = np.clip(np.floor(xs).astype(int), 0, N_grid - 1)
        iy = np.clip(np.floor(ys).astype(int), 0, N_grid - 1)
        iz = np.clip(np.floor(zs).astype(int), 0, N_grid - 1)
        # thicken by delta in each direction
        for ddx in range(-delta, delta + 1):
            for ddy in range(-delta, delta + 1):
                for ddz in range(-delta, delta + 1):
                    if ddx*ddx + ddy*ddy + ddz*ddz <= delta*delta:
                        ix2 = np.clip(ix + ddx, 0, N_grid - 1)
                        iy2 = np.clip(iy + ddy, 0, N_grid - 1)
                        iz2 = np.clip(iz + ddz, 0, N_grid - 1)
                        counts[ix2, iy2, iz2] += 1
    return counts

print()
print("=== 3D tube-incidence on 64^3 grid, delta=2 ===")
for K in [50, 100, 200, 400]:
    counts = tube_incidence_3d(K, N_grid=64, delta=2)
    occupied = (counts > 0).sum()
    total = counts.sum()
    overlap = total / max(occupied, 1)
    fraction_covered = occupied / counts.size
    # Wolff hairbrush: at a single point the multiplicity bound restricts dim
    # max occupancy
    max_occ = counts.max()
    high_occ = (counts >= 5).sum()
    print(f"K={K:4d}  cells_covered={occupied:6d} ({fraction_covered:.4f})  "
          f"avg_overlap={overlap:.3f}  max_mult={max_occ:3d}  cells_with_mult>=5={high_occ}")
