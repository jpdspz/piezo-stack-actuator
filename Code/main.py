import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from matrix import build_matrix, plot_mode_shape, mu, S, L

def det_omega(omega):
    M = build_matrix(omega)
    sign, logdet = np.linalg.slogdet(M)
    if np.abs(logdet) > 500:
        return sign * np.exp(500)
    return sign * np.exp(logdet)

def find_omega_roots(omega_range, n_points=5000):
    omega_min, omega_max = omega_range
    omegas = np.linspace(omega_min, omega_max, n_points)
    det_vals = np.array([det_omega(w) for w in omegas])

    roots = []
    for i in range(len(omegas) - 1):
        if det_vals[i] * det_vals[i+1] < 0:
            def f(w):
                return det_omega(w)
            try:
                sol = root_scalar(f, bracket=[omegas[i], omegas[i+1]], method='brentq')
                if sol.converged:
                    roots.append(sol.root)
            except:
                roots.append((omegas[i] + omegas[i+1]) / 2)
    return roots

if __name__ == "__main__":
    roots = find_omega_roots((1, 6000), n_points=10000)

    # Store mode shapes for later
    modes_data = []

    print(f"Raízes (frequências naturais) encontradas: {len(roots)}")
    print("     ω (rad/s)        f (Hz)") #       beta_1 (1/m)     beta_1 * L")
    for i, w in enumerate(roots[:10]):
        beta1 = (mu[0] * w**2 / S[0]) ** 0.25
        f = w / (2 * np.pi)
        print(f"{i+1:2d}  {w:10.3f}    {f:10.3f}") #   {beta1:10.6f}    {beta1 * L:10.6f}")

    # Plot mode shapes for the first 5 modes
    plot_filename = "Mode shapes w actuator"
    save_option = True
    show_option = False
    
    for i, w in enumerate(roots[:5]):
        _, _, x, phi = plot_mode_shape(w, mode_index=i+1, save=save_option,
                                 base_filename=plot_filename, plot_number=i+1,
                                 show=show_option)
        modes_data.append((w, x, phi))