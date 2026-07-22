import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

def dft(x):
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-2j * np.pi * k * n / N)
    dft = np.dot(M, x)

    return dft

def fft(x, ti=0, tf=60):
    """Compute the Fourier Transform using the Fast Fourier Transform algorithm."""
    N = len(x)                                      # Sample number
    T = tf - ti                                     # Analysis interval
    t = np.linspace(ti, tf, N, endpoint=False)      # Time vector (s)
    f_s = N/T                                       # Sampling rate (Hz)
    df = 1/T                                        # Frequency resolution (Hz)
    f_i = 0                                         # Initial frequency (Hz)
    f_f = f_s / 2                                   # Final frequency (Hz)
    f = np.linspace(f_i, f_s, N, endpoint=False)    # Frequencies vector (Hz)

    if N == 1:
        return x
    else:
        X_par = fft(x[::2])
        X_impar = fft(x[1::2])
        C = np.exp(-2j * np.pi * np.arange(N)/N)

        X = np.concatenate([X_par + C[:int(N/2)] * X_impar, X_par + C[int(N/2):] * X_impar])

    f_oneside = f[:N // 2]
    n_oneside = N // 2
    f_oneside = f[:n_oneside]
    X_oneside = X[:n_oneside]

    abs = np.abs(X_oneside)
    A = 2 * abs / N                     # Amplitude
    PSD =  abs**2 / (N * f_s)           # Power spectral density
    X = [f_oneside, PSD]
    
    return X
