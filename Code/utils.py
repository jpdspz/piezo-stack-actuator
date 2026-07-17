import numpy as np
import matplotlib.pyplot as plt
import os

def ch(x, beta):
    return np.cosh(beta * x)

def sh(x, beta):
    return np.sinh(beta * x)

def c(x, beta):
    return np.cos(beta * x)

def s(x, beta):
    return np.sin(beta * x)

def load_and_plot_comparison(filename_with, filename_without, 
                             label_with="With actuator", 
                             label_without="Without actuator",
                             mode_index=None,
                             show=True, save=False, save_name=None):
    """
    Load two mode shape data files (with and without actuator) and plot them together for comparison.
    """
    if save == True or show == True:
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
            print(f"Comparison plot saved to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig, ax
    else:
        return