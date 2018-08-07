import numpy as np
import scipy.misc as sm


def nchoosek(n, k):
    return sm.comb(n, k)


def nmultichoosek(n, k):
    return sm.comb(n + k - 1, k)


def F(n, k, w):
    F = 0
    for jj in range(k+1):
        F += ((-1)**jj)*sm.comb(k, jj)*sm.comb(n - jj*w - 1, k - 1)

    return F


def rho2R(rho):
    return np.nonzero(rho)[0][-1] + 1


def rho2rmin(rho):
    return np.nonzero(rho)[0][0] + 1


def rho2N(rho):
    return np.dot(np.arange(1, rho.size + 1), rho)


def rho2U(rho):
    return np.sum(rho)


def C_lb_norep(rho, K):
    return nchoosek(rho2U(rho), K)


def C_ub_norep(rho, K):
    return nchoosek(rho2N(rho), K)


def C_lb_unirep_KleqR(rho, K):
    return nmultichoosek(rho2U(rho), K)


def C_ub_unirep_KleqR(rho, K):
    return nmultichoosek(rho2U(rho), K)


def C_lb_unirep(rho, K):
    return F(K + rho2U(rho), rho2U(rho), rho2rmin(rho) + 1)


def C_ub_unirep(rho, K):
    return F(K + rho2U(rho), rho2U(rho), rho2R(rho) + 1)


rho = np.array([5, 15, 5])

K = 4

print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))

rho = np.array([5])

K = 4

print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))

rho = np.array([0, 0, 5])

K = 3

print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep_KleqR(rho, K))
print(C_ub_unirep_KleqR(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))