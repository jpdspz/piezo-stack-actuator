import numpy as np
import matplotlib.pyplot as plt
import os
from matrix import get_mode_shape

def ch(x, beta):
    return np.cosh(beta * x)

def sh(x, beta):
    return np.sinh(beta * x)

def c(x, beta):
    return np.cos(beta * x)

def s(x, beta):
    return np.sin(beta * x)

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
        outputs_dir = os.path.join(os.getcwd(), 'Outputs')
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

        outputs_dir = os.path.join(os.getcwd(), 'Outputs')
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
        test_path = os.path.join(outputs_dir, filename_with)
        if os.path.exists(test_path):
            filename_with = test_path
        else:
            raise FileNotFoundError(f"File not found: {filename_with}")
    
    if not os.path.exists(filename_without):
        test_path = os.path.join(outputs_dir, filename_without)
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