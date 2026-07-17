import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from matrix import build_matrix, plot_mode_shape, save_mode_shape_data
from utils import load_and_plot_comparison
import time

# Record start time
start_time = time.time()
print(f"Start time: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(start_time))}\n")

# Physical and geometric parameters with actuator
E1 = 2.78e9         # [Pa]
I1 = 7.54e-11       # [m^4]
rho1 = 1050         # [kg/m³]
A1 = 1.0e-4         # [m²]
mu1 = rho1 * A1
S1 = E1 * I1

E2 = 200e9          # [Pa]
I2 = 1.0e-11        # [m^4]
rho2 = 7800         # [kg/m³]
A2 = 3.0e-5         # [m²]
mu2 = rho2 * A2
S2 = E2 * I2

mu_with = [mu1, mu1 + mu2, mu1, mu1, mu1 + mu2, mu1]
S_with  = [S1,  S1 + S2,   S1,  S1,  S1 + S2,   S1]

# Physical and geometric parameters without actuator
mu_without = [mu1] * 6
S_without  = [S1] * 6

# Geometry parameters common to both
L = 0.250                           # [m]
x1 = 0.010                          # [m]
x2 = 0.028                          # [m]
x3 = 0.070                          # [m]
x4 = 0.112                          # [m]
x5 = 0.130                          # [m]
x = [0.0, x1, x2, x3, x4, x5, L]
m_a = 0.140                         # [kg]

# Whether to save and/or show outputs
save_option_individual_plots = False
show_option_individual_plots = False
save_option_comparison_plots = True
show_option_comparison_plots = False
if save_option_comparison_plots == True or show_option_comparison_plots == True:
    save_option_mode_shape_txt = True
elif save_option_comparison_plots == False and show_option_comparison_plots == False:
    save_option_mode_shape_txt = False

def det_omega(omega, S, mu, x, m_a):
    M = build_matrix(omega, S, mu, x, m_a)
    sign, logdet = np.linalg.slogdet(M)
    if np.abs(logdet) > 500:
        return sign * np.exp(500)
    return sign * np.exp(logdet)

def find_omega_roots(omega_range, S, mu, x, m_a, n_points=5000):
    omega_min, omega_max = omega_range
    omegas = np.linspace(omega_min, omega_max, n_points)
    det_vals = np.array([det_omega(w, S, mu, x, m_a) for w in omegas])

    roots = []
    for i in range(len(omegas) - 1):
        if det_vals[i] * det_vals[i+1] < 0:
            def f(w):
                return det_omega(w, S, mu, x, m_a)
            try:
                sol = root_scalar(f, bracket=[omegas[i], omegas[i+1]], method='brentq')
                if sol.converged:
                    roots.append(sol.root)
            except:
                roots.append((omegas[i] + omegas[i+1]) / 2)
    return roots

if __name__ == "__main__":
    # Find roots with actuator
    roots_with = find_omega_roots((1, 6000), S_with, mu_with, x, m_a, n_points=10000)
    
    # Find roots without actuator
    roots_without = find_omega_roots((1, 6000), S_without, mu_without, x, 0, n_points=10000)

    # Print results with actuator
    print("=== With actuator ===")
    print(f"Raízes encontradas: {len(roots_with)}")
    print("     ω (rad/s)        f (Hz)")
    for i, w in enumerate(roots_with[:10]):
        beta1 = (mu_with[0] * w**2 / S_with[0]) ** 0.25
        f = w / (2 * np.pi)
        print(f"{i+1:2d}  {w:10.3f}    {f:10.3f}")

    # Print results without actuator
    print("\n=== Without actuator ===")
    print(f"Raízes encontradas: {len(roots_without)}")
    print("     ω (rad/s)        f (Hz)")
    for i, w in enumerate(roots_without[:10]):
        beta1 = (mu_without[0] * w**2 / S_without[0]) ** 0.25
        f = w / (2 * np.pi)
        print(f"{i+1:2d}  {w:10.3f}    {f:10.3f}")

    # Plot and save mode shapes with actuator
    print("\n--- Saving mode shapes with actuator ---")
    modes_with = []
    for i, w in enumerate(roots_with[:5]):
        fig, ax, x_vals, phi_vals = plot_mode_shape(
            omega=w,
            mode_index=i+1,
            mu=mu_with,
            S=S_with,
            x=x,
            m_a=m_a,
            save=save_option_individual_plots,
            base_filename="Mode shapes with actuator",
            plot_number=i+1,
            show=show_option_individual_plots
        )
        modes_with.append((w, x_vals, phi_vals))
        # Save data to .txt file
        save_mode_shape_data(w, x_vals, phi_vals,
                            filename=f"Mode {i+1:01d} with actuator",
                            mode_index=None, save=save_option_mode_shape_txt)

    # Plot and save mode shapes without actuator
    print("\n--- Saving mode shapes without actuator ---")
    modes_without = []
    for i, w in enumerate(roots_without[:5]):
        fig, ax, x_vals, phi_vals = plot_mode_shape(
            omega=w,
            mode_index=i+1,
            mu=mu_without,
            S=S_without,
            x=x,
            m_a=0,
            save=save_option_individual_plots,
            base_filename="Mode shapes without actuator",
            plot_number=i+1,
            show=show_option_individual_plots
        )
        modes_without.append((w, x_vals, phi_vals))
        # Save data to .txt file
        save_mode_shape_data(w, x_vals, phi_vals,
                            filename=f"Mode {i+1:01d} without actuator",
                            mode_index=None, save=save_option_mode_shape_txt)

    if save_option_comparison_plots:
        # Compare modes (with vs without actuator)
        print("\n--- Comparing modes ---")
        for i in range(1, 6):
            load_and_plot_comparison(
                filename_with=f"Mode {i:01d} with actuator.txt",
                filename_without=f"Mode {i:01d} without actuator.txt",
                label_with="With actuator",
                label_without="Without actuator",
                mode_index=i,
                show=show_option_comparison_plots,
                save=save_option_comparison_plots,
                save_name=f"Comparison mode {i:01d}"
            )
    else:
        pass

# Record end time
end_time = time.time()
print(f"\nEnd time: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(end_time))}")

# Calculate runtime
runtime = end_time - start_time
print(f"Total runtime: {runtime:.2f} s")