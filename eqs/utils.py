import numpy as np
import scipy.misc as sm
import time


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


def C_unirep(U, R, K):
    return F(K + U, U, R + 1)


def C_for_unirep(rho, K):
    C_unireps = np.zeros((rho.size, K + 1))
    C_unireps[:, 0] = 1
    for rr in range(rho.size):
        for kk in range(1, K + 1):
            C_unireps[rr, kk] = C_unirep(rho[rr], rr + 1, kk)

        if rr:
            C = np.convolve(C, C_unireps[rr], 'full')[:K + 1]
        else:
            C = np.copy(C_unireps[0])

    return C[K]


def C_rec_norep_rec(rho, K):
    if not np.count_nonzero(rho):
        return np.concatenate((np.array([1]), np.zeros((K, ))), 0)

    rmin = rho2rmin(rho)
    rho_new = np.copy(rho)
    rho_new[rmin - 1] -= 1

    C = np.convolve(np.ones((rmin + 1, )), C_rec_norep_rec(rho_new, K), 'full')[:K + 1]
    return C


def C_rec_norep(rho, K):
    return C_rec_norep_rec(rho, K)[K]


rho = np.array([5, 15, 5])

K = 4

start = time.time()
print(C_for_unirep(rho, K))
end = time.time()
print(end - start)
start = time.time()
print(C_rec_norep(rho, K))
end = time.time()
print(end - start)
print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))

rho = np.array([5])

K = 4

start = time.time()
print(C_for_unirep(rho, K))
end = time.time()
print(end - start)
start = time.time()
print(C_rec_norep(rho, K))
end = time.time()
print(end - start)
print(C_rec_norep(rho, K))
print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))

rho = np.array([0, 0, 5])

K = 3

start = time.time()
print(C_for_unirep(rho, K))
end = time.time()
print(end - start)
start = time.time()
print(C_rec_norep(rho, K))
end = time.time()
print(end - start)
print(C_rec_norep(rho, K))
print(C_lb_norep(rho, K))
print(C_ub_norep(rho, K))
print(C_lb_unirep_KleqR(rho, K))
print(C_ub_unirep_KleqR(rho, K))
print(C_lb_unirep(rho, K))
print(C_ub_unirep(rho, K))