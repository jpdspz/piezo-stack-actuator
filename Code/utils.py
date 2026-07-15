import numpy as np

def ch(x, beta):
    return np.cosh(beta * x)

def sh(x, beta):
    return np.sinh(beta * x)

def c(x, beta):
    return np.cos(beta * x)

def s(x, beta):
    return np.sin(beta * x)