import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from matrix import build_matrix, plot_mode_shape, save_mode_shape_data, load_and_plot_comparison
import time
import os

# Record start time
start_time = time.time()
print(f"Start time: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(start_time))}\n")

# Physical and geometric parameters with actuator
E1 = 3.5e+9                 # Elastic modulus of the beam [Pa]
b1 = 3.5e-2                 # Width of the beam [m]
t1 = 6.0e-3                 # Thickness of the beam [m]
I1 = (b1 * t1**3) / 12      # Area moment of inertia of the beam [m^4]
rho1 = 8.5e+2               # Density of the beam [kg/m³]
A1 = b1 * t1                # Cross-section area of the beam [m²]
mu1 = rho1 * A1             # Mass per unit length of the beam [kg/m]
S1 = E1 * I1                # Bending stiffness of the beam [Nm²]

E2 = 2.0e+11                # Elastic modulus of the actuator support's leg [Pa]
b2 = 1.5e-2                 # Width of the actuator support's leg [m]
t2 = 2.0e-3                 # Thickness of the actuator support's leg [m]
I2 = (b2 * t2**3) / 12       # Area moment of inertia [m^4]
rho2 = 7800                 # Density of the actuator support's leg [kg/m³]
A2 = b2 * t2                # Cross-section area of the actuator support's leg [m²]
mu2 = rho2 * A2             # Mass per unit length of the actuator support's leg [kg/m]
S2 = E2 * I2                # Bending stiffness of the actuator support's leg [Nm²]

mu_with = [mu1, mu1 + mu2, mu1, mu1, mu1 + mu2, mu1]
S_with  = [S1,  S1 + S2,   S1,  S1,  S1 + S2,   S1]

# Physical and geometric parameters without actuator
mu_without = [mu1] * 6
S_without  = [S1] * 6

# Geometry parameters common to both systems (with and without the actuator)
L = 0.550                           # Free length of the beam [m]
a1 = 0.018                          # Distance between the bolts of one of the actuator's angle support [m]
a2 = 0.014                          # Distance between the inner bolt and the inner face of the actuator support's vertical leg [m]
a3 = 0.056                          # Distance between the inner faces of the actuator's angle supports [m]
x1 = 0.020                          # Position of the actuator support's 1st bolt in relation to the fixed end of the beam [m]
x2 = x1 + a1                        # Position of the actuator support's 2nd bolt in relation to the fixed end of the beam [m]
x3 = x2 + a2 + a3 / 2               # Position of the actuator's lumped mass (midpoint of piezo stack) [m]
x4 = x2 + a3 + a2 / 2               # Position of the actuator support's 3rd bolt in relation to the fixed end of the beam [m]
x5 = x4 + a1                        # Position of the actuator support's 4th bolt in relation to the fixed end of the beam [m]
x = [0.0, x1, x2, x3, x4, x5, L]
m_a = 0.140                         # Total mass of the actuator system [kg]

# Saving and plotting options
save_option_individual_plots = False
show_option_individual_plots = False
save_option_comparison_plots = True
show_option_comparison_plots = True
if save_option_comparison_plots == True or show_option_comparison_plots == True:
    save_option_mode_shape_txt = True
elif save_option_comparison_plots == False and show_option_comparison_plots == False:
    save_option_mode_shape_txt = False
number_of_modes_to_plot = 5
outputs_dir = os.path.join(os.getcwd(), 'Outputs')

# Define functions
def det_omega(omega, S, mu, x, m_a):
    """
    Calculate the determinant of the matrix M(ω) at a given frequency ω.
    """
    M = build_matrix(omega, S, mu, x, m_a)
    sign, logdet = np.linalg.slogdet(M)
    if np.abs(logdet) > 500:
        return sign * np.exp(500)
    return sign * np.exp(logdet)

def find_omega_roots(omega_range, S, mu, x, m_a, n_points=5000):
    """
    Find natural frequencies by locating zeros of det[M(ω)].    
    Uses grid search to identify sign changes, then refines with Brent's method.
    """
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

# Main execution block (only runs when executed directly, i.e., not when imported as a module)
if __name__ == "__main__":
    # Find roots without actuator
    roots_without = find_omega_roots((1, 2500), S_without, mu_without, x, 0, n_points=10000)

    # Find roots with actuator
    roots_with = find_omega_roots((1, 2500), S_with, mu_with, x, m_a, n_points=10000)
    
    # Print results without actuator
    print("Natural frequencies without actuator")
    print("     ω (rad/s)        f (Hz)")
    for i, w in enumerate(roots_without[:number_of_modes_to_plot]):
        beta1 = (mu_without[0] * w**2 / S_without[0]) ** 0.25
        f = w / (2 * np.pi)
        print(f"{i+1:2d}  {w:10.1f}    {f:10.1f}")

    # Print results with actuator
    print("\nNatural frequencies with actuator")
    print("     ω (rad/s)        f (Hz)")
    for i, w in enumerate(roots_with[:number_of_modes_to_plot]):
        beta1 = (mu_with[0] * w**2 / S_with[0]) ** 0.25
        f = w / (2 * np.pi)
        print(f"{i+1:2d}  {w:10.1f}    {f:10.1f}")

    # Plot mode shapes without actuator
    modes_without = []
    for i, w in enumerate(roots_without[:number_of_modes_to_plot]):
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
        
        # if save_option_individual_plots:
        #     if i == number_of_modes_to_plot - 1:
        #         print(f"\nMode shape plots without actuator saved to {outputs_dir}")

        # Save data to .txt file
        save_mode_shape_data(w, x_vals, phi_vals,
                            filename=f"Mode {i+1:01d} without actuator",
                            mode_index=None, save=save_option_mode_shape_txt)
        
        # if i == number_of_modes_to_plot - 1:
        #     print(f"\nMode shape data without actuator saved as .txt to {outputs_dir}")

    # Plot mode shapes with actuator
    modes_with = []
    for i, w in enumerate(roots_with[:number_of_modes_to_plot]):
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
        
        # if save_option_individual_plots:
        #     if i == number_of_modes_to_plot - 1:
        #         print(f"\nMode shape plots with actuator saved to {outputs_dir}")

        # Save data to .txt file
        save_mode_shape_data(w, x_vals, phi_vals,
                            filename=f"Mode {i+1:01d} with actuator",
                            mode_index=None, save=save_option_mode_shape_txt)
        
        # if i == number_of_modes_to_plot - 1:
        #     print(f"\nMode shape data with actuator saved as .txt to {outputs_dir}")
        

    # Compare modes (with vs without actuator)
    for i in range(1, number_of_modes_to_plot + 1):
        load_and_plot_comparison(
            filename_with=f"Mode {i:01d} with actuator.txt",
            filename_without=f"Mode {i:01d} without actuator.txt",
            label_with="With actuator",
            label_without="Without actuator",
            mode_index=i,
            show=show_option_comparison_plots,
            save=save_option_comparison_plots,
            save_name=f"Comparison mode {i:01d}",
            bolt_positions=[x[1], x[2], x[4], x[5]]
        )
        
        # if i == number_of_modes_to_plot:
        #     print(f"\nMode shape comparison plots saved to {outputs_dir}")

# Record end time
end_time = time.time()
print(f"\nEnd time: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(end_time))}")

# Calculate runtime
runtime = end_time - start_time
print(f"Total runtime: {runtime:.2f} s")