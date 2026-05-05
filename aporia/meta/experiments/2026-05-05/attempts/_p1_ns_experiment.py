"""
P1 / Navier-Stokes: BKM-criterion integral on 2D NS as calibration anchor.

2D NS has global-in-time smooth solutions for smooth initial data (folklore;
Leray-Hopf + 2D vorticity transport + L^infty bound on omega).  Compute
integral_0^T ||omega(t)||_infty dt and show it stays bounded -- this is the
machinery the BKM (Beale-Kato-Majda 1984) criterion relies on.

In 3D, BKM says blowup at T iff the same integral diverges as t -> T.  The
open question is whether it CAN diverge for smooth, finite-energy initial
data.  This script does NOT answer that; it generates a 2D control trace
to demonstrate the criterion's quantitative content.
"""
import numpy as np

N = 64
L = 2 * np.pi
nu = 1e-3
T = 2.0
dt = 5e-3
nsteps = int(T / dt)

x = np.linspace(0, L, N, endpoint=False)
y = np.linspace(0, L, N, endpoint=False)
X, Y = np.meshgrid(x, y, indexing='ij')

# Two-vortex Taylor-Green-ish initial vorticity
omega = (np.exp(-((X - np.pi)**2 + (Y - np.pi - 0.5)**2) / 0.2)
         - np.exp(-((X - np.pi)**2 + (Y - np.pi + 0.5)**2) / 0.2))

kx = np.fft.fftfreq(N, d=L/N) * 2 * np.pi
ky = np.fft.fftfreq(N, d=L/N) * 2 * np.pi
KX, KY = np.meshgrid(kx, ky, indexing='ij')
K2 = KX**2 + KY**2
K2[0, 0] = 1.0  # avoid divide-by-zero on zero mode

def rhs(omega):
    omega_hat = np.fft.fft2(omega)
    psi_hat = -omega_hat / K2
    psi_hat[0, 0] = 0
    u_hat = 1j * KY * psi_hat
    v_hat = -1j * KX * psi_hat
    u = np.real(np.fft.ifft2(u_hat))
    v = np.real(np.fft.ifft2(v_hat))
    omega_x = np.real(np.fft.ifft2(1j * KX * omega_hat))
    omega_y = np.real(np.fft.ifft2(1j * KY * omega_hat))
    advection = -(u * omega_x + v * omega_y)
    diffusion_hat = -nu * K2 * omega_hat
    diffusion = np.real(np.fft.ifft2(diffusion_hat))
    return advection + diffusion

# RK2 integration
t = 0.0
times = [t]
linf = [np.max(np.abs(omega))]
energy = []
enstrophy = []

# energy on initial state
omega_hat0 = np.fft.fft2(omega)
psi_hat0 = -omega_hat0 / K2
psi_hat0[0, 0] = 0
u_hat0 = 1j * KY * psi_hat0
v_hat0 = -1j * KX * psi_hat0
u0 = np.real(np.fft.ifft2(u_hat0))
v0 = np.real(np.fft.ifft2(v_hat0))
energy.append(0.5 * np.mean(u0**2 + v0**2))
enstrophy.append(0.5 * np.mean(omega**2))

bkm_integral = 0.0
bkm_trace = [bkm_integral]

for step in range(nsteps):
    k1 = rhs(omega)
    k2 = rhs(omega + dt * k1)
    omega = omega + 0.5 * dt * (k1 + k2)
    t += dt
    times.append(t)
    linf_now = np.max(np.abs(omega))
    linf.append(linf_now)
    bkm_integral += dt * 0.5 * (linf[-1] + linf[-2])
    bkm_trace.append(bkm_integral)
    omega_hat = np.fft.fft2(omega)
    psi_hat = -omega_hat / K2
    psi_hat[0, 0] = 0
    u_hat = 1j * KY * psi_hat
    v_hat = -1j * KX * psi_hat
    u = np.real(np.fft.ifft2(u_hat))
    v = np.real(np.fft.ifft2(v_hat))
    energy.append(0.5 * np.mean(u**2 + v**2))
    enstrophy.append(0.5 * np.mean(omega**2))

print(f"steps              : {nsteps}")
print(f"final time         : {t:.4f}")
print(f"||omega||_inf  start: {linf[0]:.6f}")
print(f"||omega||_inf  final: {linf[-1]:.6f}")
print(f"||omega||_inf  max  : {max(linf):.6f}")
print(f"BKM integral final : {bkm_integral:.6f}")
print(f"energy   start/final: {energy[0]:.6e} / {energy[-1]:.6e}")
print(f"enstroph start/final: {enstrophy[0]:.6e} / {enstrophy[-1]:.6e}")
print(f"energy ratio (final/start): {energy[-1]/energy[0]:.6f}")
print(f"enstrophy ratio          : {enstrophy[-1]/enstrophy[0]:.6f}")

# Sample BKM integral at four checkpoints
checkpoints = [int(0.25 * nsteps), int(0.5 * nsteps), int(0.75 * nsteps), nsteps]
print("\nBKM integral checkpoints:")
for cp in checkpoints:
    print(f"  t={times[cp]:.3f}  integral={bkm_trace[cp]:.6f}  ||omega||_inf={linf[cp]:.6f}")
