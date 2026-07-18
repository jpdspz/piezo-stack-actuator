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
