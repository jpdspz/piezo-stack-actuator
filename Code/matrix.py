import numpy as np
from utils import ch, sh, c, s

# Parâmetros físicos
E1 = 2.78e9
I1 = 7.54e-11
rho1 = 1050
A1 = 1.0e-4
mu1 = rho1 * A1
S1 = E1 * I1

E2 = 200e9
I2 = 1.0e-11
rho2 = 7800
A2 = 3.0e-5
mu2 = rho2 * A2
S2 = E2 * I2

mu = [mu1, mu1 + mu2, mu1, mu1, mu1 + mu2, mu1]
S  = [S1,  S1 + S2,   S1,  S1,  S1 + S2,   S1]

L = 0.25
a1 = 0.01 + 0.009
a2 = 0.102
x = [0.0, a1 - 0.009, a1 + 0.009, (a1 + a2)/2, a2 - 0.009, a2 + 0.009, L]
m_a = 0.14

def build_matrix(omega):
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