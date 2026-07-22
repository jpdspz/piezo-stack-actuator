import numpy as np
from utils import ch, sh, c, s
from scipy.linalg import null_space
import matplotlib.pyplot as plt
import os
import datetime

# Variáveis globais para controlar a pergunta de sobrescrita
_ask_overwrite_done = False
_overwrite_all = False

def build_matrix(omega, S, mu, x, m_a):
    beta = [(mu[i] * omega**2 / S[i]) ** 0.25 for i in range(6)]
    n_seg = 6
    n_points = n_seg + 1
    ch_vals = np.zeros((n_seg, n_points))
    sh_vals = np.zeros((n_seg, n_points))
    c_vals = np.zeros((n_seg, n_points))
    s_vals = np.zeros((n_seg, n_points))

    for i in range(n_seg):
        for j in range(1, n_points):
            ch_vals[i, j] = ch(x[j], beta[i])
            sh_vals[i, j] = sh(x[j], beta[i])
            c_vals[i, j] = c(x[j], beta[i])
            s_vals[i, j] = s(x[j], beta[i])

    M = np.zeros((24, 24))
    row = 0

    def add_row(coeffs):
        nonlocal row
        for col, val in coeffs:
            M[row, col] = val
        row += 1

    # Engaste
    add_row([(0, 1.0), (2, 1.0)])
    add_row([(1, 1.0), (3, 1.0)])

    # Continuidade
    for j in range(1, 6):
        seg_left = j - 1
        seg_right = j
        S_left = S[seg_left]
        S_right = S[seg_right]
        bL = beta[seg_left]
        bR = beta[seg_right]

        # Deflexão
        add_row([
            (4*seg_left + 0, ch_vals[seg_left, j]),
            (4*seg_left + 1, sh_vals[seg_left, j]),
            (4*seg_left + 2, c_vals[seg_left, j]),
            (4*seg_left + 3, s_vals[seg_left, j]),
            (4*seg_right + 0, -ch_vals[seg_right, j]),
            (4*seg_right + 1, -sh_vals[seg_right, j]),
            (4*seg_right + 2, -c_vals[seg_right, j]),
            (4*seg_right + 3, -s_vals[seg_right, j]),
        ])

        # Rotação
        add_row([
            (4*seg_left + 0, sh_vals[seg_left, j] * bL),
            (4*seg_left + 1, ch_vals[seg_left, j] * bL),
            (4*seg_left + 2, -s_vals[seg_left, j] * bL),
            (4*seg_left + 3, c_vals[seg_left, j] * bL),
            (4*seg_right + 0, -sh_vals[seg_right, j] * bR),
            (4*seg_right + 1, -ch_vals[seg_right, j] * bR),
            (4*seg_right + 2, s_vals[seg_right, j] * bR),
            (4*seg_right + 3, -c_vals[seg_right, j] * bR),
        ])

        # Momento
        add_row([
            (4*seg_left + 0, ch_vals[seg_left, j] * S_left * bL**2),
            (4*seg_left + 1, sh_vals[seg_left, j] * S_left * bL**2),
            (4*seg_left + 2, -c_vals[seg_left, j] * S_left * bL**2),
            (4*seg_left + 3, -s_vals[seg_left, j] * S_left * bL**2),
            (4*seg_right + 0, -ch_vals[seg_right, j] * S_right * bR**2),
            (4*seg_right + 1, -sh_vals[seg_right, j] * S_right * bR**2),
            (4*seg_right + 2, c_vals[seg_right, j] * S_right * bR**2),
            (4*seg_right + 3, s_vals[seg_right, j] * S_right * bR**2),
        ])

        # Cortante (com massa em x3)
        if j == 3:
            add_row([
                (4*seg_left + 0, sh_vals[seg_left, j] * S_left * bL**3 + m_a * omega**2 * ch_vals[seg_left, j]),
                (4*seg_left + 1, ch_vals[seg_left, j] * S_left * bL**3 + m_a * omega**2 * sh_vals[seg_left, j]),
                (4*seg_left + 2, s_vals[seg_left, j] * S_left * bL**3 + m_a * omega**2 * c_vals[seg_left, j]),
                (4*seg_left + 3, -c_vals[seg_left, j] * S_left * bL**3 + m_a * omega**2 * s_vals[seg_left, j]),
                (4*seg_right + 0, -sh_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 1, -ch_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 2, -s_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 3, c_vals[seg_right, j] * S_right * bR**3),
            ])
        else:
            add_row([
                (4*seg_left + 0, sh_vals[seg_left, j] * S_left * bL**3),
                (4*seg_left + 1, ch_vals[seg_left, j] * S_left * bL**3),
                (4*seg_left + 2, s_vals[seg_left, j] * S_left * bL**3),
                (4*seg_left + 3, -c_vals[seg_left, j] * S_left * bL**3),
                (4*seg_right + 0, -sh_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 1, -ch_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 2, -s_vals[seg_right, j] * S_right * bR**3),
                (4*seg_right + 3, c_vals[seg_right, j] * S_right * bR**3),
            ])

    # Extremidade livre
    add_row([
        (20, ch_vals[5, 6]),
        (21, sh_vals[5, 6]),
        (22, -c_vals[5, 6]),
        (23, -s_vals[5, 6]),
    ])

    add_row([
        (20, sh_vals[5, 6]),
        (21, ch_vals[5, 6]),
        (22, s_vals[5, 6]),
        (23, -c_vals[5, 6]),
    ])

    return M

def get_mode_shape(omega, S, mu, x, m_a, n_points_per_segment=50):
    """
    Compute the mode shape for a given natural frequency omega.
    Returns:
        x_vals: array of x positions along the beam
        phi_vals: array of mode shape values
    """
    # Build the matrix at this omega
    M = build_matrix(omega, S, mu, x, m_a)
    
    # Find the null space (eigenvector)
    # The null space gives a vector X such that M * X = 0
    null_vec = null_space(M)
    
    # The null space may have more than one column if the matrix is rank-deficient
    # We take the first column (the most significant)
    X = null_vec[:, 0]
    
    # Extract coefficients for each segment
    # X has 24 entries: 4 per segment
    coeffs = []
    for i in range(6):
        A_i = X[4*i + 0]
        B_i = X[4*i + 1]
        C_i = X[4*i + 2]
        D_i = X[4*i + 3]
        coeffs.append((A_i, B_i, C_i, D_i))
    
    # Compute beta_i for this omega
    beta = [(mu[i] * omega**2 / S[i]) ** 0.25 for i in range(6)]
    
    # Evaluate the mode shape along the beam
    x_vals = []
    phi_vals = []
    
    # For each segment
    for i in range(6):
        # Define the domain of the segment
        x_start = x[i]
        x_end = x[i+1]
        
        # Create points within the segment
        x_seg = np.linspace(x_start, x_end, n_points_per_segment)
        
        A_i, B_i, C_i, D_i = coeffs[i]
        b_i = beta[i]
        
        # Evaluate the mode shape
        phi_seg = (A_i * np.cosh(b_i * x_seg) +
                   B_i * np.sinh(b_i * x_seg) +
                   C_i * np.cos(b_i * x_seg) +
                   D_i * np.sin(b_i * x_seg))
        
        x_vals.extend(x_seg)
        phi_vals.extend(phi_seg)
    
    # Convert to numpy arrays
    x_vals = np.array(x_vals)
    phi_vals = np.array(phi_vals)
    
    return x_vals, phi_vals

def plot_mode_shape(omega, S, mu, x, m_a, mode_index=None, n_points_per_segment=50,
                    save=False, base_filename=None, plot_number=None, show=True):
    """
    Plot the mode shape for a given natural frequency.
    """
    global _ask_overwrite_done, _overwrite_all

    x_vals, phi_vals = get_mode_shape(omega, S, mu, x, m_a, n_points_per_segment)
    
    # Normalize the mode shape
    phi_vals = phi_vals / np.max(np.abs(phi_vals))

    # Force the sign for the displacement to be positive
    if phi_vals[-1] < 0:
        phi_vals = -phi_vals
    
    # Compute frequency in Hz
    f_hz = omega / (2 * np.pi)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Hh%Mmin%Ss")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create figure and axes using object-oriented approach
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x_vals, phi_vals, linewidth=2)
    
    # Mark the bolt locations (x1, x2, x4, x5)
    if m_a != 0:
        bolt_positions = [x[1], x[2], x[4], x[5]]  # x1, x2, x4, x5
        bolt_phi = np.interp(bolt_positions, x_vals, phi_vals)  # Get phi values at those x positions

        ax.scatter(bolt_positions, bolt_phi, 
                   facecolors='white', edgecolors='black', s=50, zorder=5, 
                label='Actuator fixing points', linewidth=1)
    
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('Position along beam (m)')
    ax.set_ylabel('Mode shape (normalized)')
    
    if mode_index is not None:
        ax.set_title(rf'Mode {mode_index}: f = {f_hz:.1f} Hz (ω = {omega:.0f} rad/s)')
    else:
        ax.set_title(rf'Mode shape: f = {f_hz:.1f} Hz (ω = {omega:.0f} rad/s)')
    
    ax.grid(True)
    
    # Save if requested
    if save:
        outputs_dir = os.path.join(os.getcwd(), 'Outputs/Mode shapes')
        os.makedirs(outputs_dir, exist_ok=True)

        if base_filename is None:
            mode_str = f"Mode {mode_index:01d}" if mode_index is not None else "Mode"
            base_filename = f"{mode_str}"

        if plot_number is not None:
            filename = f"{base_filename}_{plot_number}"
        else:
            filename = f"{base_filename}"

        full_path = os.path.join(outputs_dir, f"{filename}.png")

        plt.savefig(full_path, dpi=150, bbox_inches='tight')

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax, x_vals, phi_vals

def save_mode_shape_data(omega, x_vals, phi_vals, filename, mode_index=None, save=False):
    """
    Save mode shape data to a text file.
    """
    if save:
        # Force the sign for the displacement to be positive
        if phi_vals[-1] < 0:
            phi_vals = -phi_vals

        outputs_dir = os.path.join(os.getcwd(), 'Outputs/Mode shapes')
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Build filename
        mode_str = f" mode {mode_index:01d}" if mode_index is not None else ""
        full_path = os.path.join(outputs_dir, f"{filename}{mode_str}.txt")
        
        # Save data
        with open(full_path, 'w') as f:
            f.write(f"# Mode shape data\n")
            f.write(f"# omega = {omega:.1f} rad/s\n")
            f.write(f"# mode_index = {mode_index}\n")
            f.write("# x (m)\t\tphi (normalized)\n")
            for x, phi in zip(x_vals, phi_vals):
                f.write(f"{x:.4f}\t{phi:.3f}\n")
        
        return full_path
    else:
        return

def load_and_plot_comparison(filename_with, filename_without, label_with="With actuator", 
                             label_without="Without actuator", mode_index=None, show=True,
                             save=False, save_name=None, bolt_positions=None):
    """
    Load two mode shape data files (with and without actuator) and plot them together for comparison.
    """
    outputs_dir = os.path.join(os.getcwd(), 'Outputs')
    
    # Handle full paths or relative paths
    if not os.path.exists(filename_with):
        # Try prepending Outputs/ if not found
        test_path = os.path.join(outputs_dir, 'Mode shapes', filename_with)
        if os.path.exists(test_path):
            filename_with = test_path
        else:
            raise FileNotFoundError(f"File not found: {filename_with}")
    
    if not os.path.exists(filename_without):
        test_path = os.path.join(outputs_dir, 'Mode shapes', filename_without)
        if os.path.exists(test_path):
            filename_without = test_path
        else:
            raise FileNotFoundError(f"File not found: {filename_without}")
    
    # Load data
    def load_data(filepath):
        data = np.loadtxt(filepath, comments='#')
        return data[:, 0], data[:, 1]  # x, phi
    
    x1, phi1 = load_data(filename_with)
    x2, phi2 = load_data(filename_without)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x1, phi1, linewidth=2, label=label_with, color='blue')

    # Mark bolt locations (if provided)
    if bolt_positions is not None:
        bolt_phi1 = np.interp(bolt_positions, x1, phi1)
        
        # Circles for the "with actuator" case (blue)
        ax.scatter(bolt_positions, bolt_phi1, 
                   facecolors='white', edgecolors='k', 
                   s=60, zorder=5, linewidths=1.5,
                   label='Actuator fixing points')      

    ax.plot(x2, phi2, linewidth=2, label=label_without, color='red', linestyle='--')
    
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('Position along beam (m)', fontsize=14)
    ax.set_ylabel('Mode shape (normalized)', fontsize=14)
    
    if mode_index is not None:
        ax.set_title(f'Mode {mode_index} with and without actuator')
    else:
        ax.set_title('Mode shape with and without actuator')
    
    ax.legend()
    ax.grid(True)
    
    # Save if requested
    if save:
        outputs_dir = os.path.join(os.getcwd(), 'Outputs', 'Mode shape comparison')
        os.makedirs(outputs_dir, exist_ok=True)
        if save_name is None:
            save_name = f"Comparison mode {mode_index:01d}" if mode_index is not None else "Comparison"
        save_path = os.path.join(outputs_dir, f"{save_name}.png")
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig, ax