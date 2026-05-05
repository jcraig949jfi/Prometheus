"""3D diffeomorphism — explore homoclinic-tangency / heterodimensional
neighborhood of a Smale-horseshoe-like map embedded in R^3.

Map: f(x, y, z) = (a*x*(1-x), y + alpha*sin(2*pi*x), b*z + gamma*y),
a 3D extension of a 1D logistic map with a coupled "tangency parameter"
alpha and an expanding direction b > 1.

Goal: perturb f in a small neighborhood and check whether the perturbed
system is hyperbolic (uniform separation of stable / unstable) versus
exhibits homoclinic tangency or heterodimensional cycle. Density-of-
hyperbolicity (Palis) predicts that in any neighborhood we find one
or the other.

Concrete check: along a 1-parameter family f_eps with alpha varying,
at each parameter compute the Lyapunov spectrum on N=10000 random
orbit points and check (a) whether the spectrum is uniformly bounded
away from zero (hyperbolic candidate) or (b) approaches zero (tangency
candidate).
"""
import json
import time
import numpy as np


def f(state, a=3.7, alpha=0.3, b=1.4, gamma=0.1):
    x, y, z = state
    nx = a * x * (1 - x) % 1.0  # mod 1 to keep bounded
    ny = (y + alpha * np.sin(2 * np.pi * x)) % 1.0
    nz = (b * z + gamma * y) % 1.0
    return np.array([nx, ny, nz])


def jacobian(state, a=3.7, alpha=0.3, b=1.4, gamma=0.1):
    x, y, z = state
    return np.array([
        [a * (1 - 2 * x), 0.0, 0.0],
        [2 * np.pi * alpha * np.cos(2 * np.pi * x), 1.0, 0.0],
        [0.0, gamma, b],
    ])


def lyap_spectrum(alpha, n_burn=2000, n_iter=10000, a=3.7, b=1.4, gamma=0.1, seed=0):
    rng = np.random.default_rng(seed)
    state = rng.uniform(0.05, 0.95, 3)
    for _ in range(n_burn):
        state = f(state, a=a, alpha=alpha, b=b, gamma=gamma)
    # QR decomposition method
    Q = np.eye(3)
    log_norms = np.zeros(3)
    for _ in range(n_iter):
        J = jacobian(state, a=a, alpha=alpha, b=b, gamma=gamma)
        M = J @ Q
        Q, R = np.linalg.qr(M)
        log_norms += np.log(np.abs(np.diag(R)) + 1e-30)
        state = f(state, a=a, alpha=alpha, b=b, gamma=gamma)
    return sorted(log_norms / n_iter, reverse=True)


def angle_stable_unstable(alpha, n_burn=2000, n_iter=5000, a=3.7, b=1.4, gamma=0.1, seed=0):
    """Estimate minimum angle between stable and unstable subspaces
    along an orbit (a tangency-canary). Uses iterated Jacobian to
    distinguish expanding from contracting directions, then minimum
    angle between them.
    """
    rng = np.random.default_rng(seed)
    state = rng.uniform(0.05, 0.95, 3)
    for _ in range(n_burn):
        state = f(state, a=a, alpha=alpha, b=b, gamma=gamma)
    angles = []
    Q = np.eye(3)
    for _ in range(n_iter):
        J = jacobian(state, a=a, alpha=alpha, b=b, gamma=gamma)
        # SVD gives expanding / contracting axes
        U, S, Vt = np.linalg.svd(J)
        # angle between row-1 of Vt (most contracting input direction) and last column of U (most expanding output direction)
        u_dir = U[:, 0]  # most expanding
        v_dir = Vt[-1]   # most contracting
        cos = abs(np.dot(u_dir, v_dir))
        angle = np.arccos(min(1.0, max(-1.0, cos)))
        angles.append(angle)
        state = f(state, a=a, alpha=alpha, b=b, gamma=gamma)
    return min(angles), float(np.mean(angles)), float(np.percentile(angles, 5))


if __name__ == "__main__":
    t0 = time.time()
    alphas = np.linspace(0.0, 0.6, 13)
    results = []
    for alpha in alphas:
        spec = lyap_spectrum(alpha, n_iter=5000, seed=0)
        ang_min, ang_mean, ang_p5 = angle_stable_unstable(alpha, n_iter=3000, seed=0)
        record = {
            "alpha": float(alpha),
            "lyapunov_spectrum": [float(s) for s in spec],
            "angle_min_rad": float(ang_min),
            "angle_p5_rad": float(ang_p5),
            "angle_mean_rad": float(ang_mean),
            "smallest_lyap_modulus": float(min(abs(s) for s in spec)),
        }
        results.append(record)
        print(f"alpha={alpha:.3f}  Lyap={[f'{s:+.3f}' for s in spec]}  ang_min={ang_min:.3f}  ang_p5={ang_p5:.3f}")

    elapsed = time.time() - t0
    payload = {"elapsed_sec": elapsed, "results": results}
    with open("D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/_scratch_B/palis_results.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nDone in {elapsed:.1f}s")
