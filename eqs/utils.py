import numpy as np
import scipy.misc as sm
import time
import itertools


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
    return nmultichoosek(rho2N(rho), K)


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

    rmin = rho2rmin(rho)
    rho_new = np.copy(rho)
    rho_new[rmin - 1] -= 1

    if np.count_nonzero(rho_new):
        return np.convolve(np.ones((rmin + 1, )), C_rec_norep_rec(rho_new, K), 'full')[:K + 1]
    else:
        return np.ones((rmin + 1, ))


def C_rec_norep(rho, K):
    return C_rec_norep_rec(rho, K)[K]


def G_sum_start(n, k, w, j):
    sum = 0
    iter = list(itertools.combinations(np.arange(k), j))
    for inds in np.array(iter):
        sum += nchoosek(n - 1 - np.sum(w[inds]), k - 1)

    return sum


def G(n, k, w):
    sum = nchoosek(n - 1, k - 1)
    for jj in np.arange(1, k):
        sum += (-1)**jj * G_sum_start(n, k, w, jj)
    return sum


def C_G(rho, K):
    w = rho2rmin(rho)*np.ones((rho[rho2rmin(rho) - 1], ))
    for rr in range(rho2rmin(rho), rho2R(rho)):
        w = np.concatenate((w, (rr + 1)*np.ones((rho[rr], ))), 0)
    return G(K + rho2U(rho), rho2U(rho), w + 1)


def print_perf(rho, K):
    print(C_lb_norep(rho, K), C_ub_norep(rho, K))
    print(C_lb_unirep(rho, K), C_ub_unirep(rho, K))
    start = time.time()
    result = C_rec_norep(rho, K)
    end = time.time()
    print(result, "(", end - start, ")")
    start = time.time()
    result = C_for_unirep(rho, K)
    end = time.time()
    print(result, "(", end - start, ")")
    # start = time.time()
    # result = C_G(rho, K)
    # end = time.time()
    # print(result, "(", end - start, ")")
    return

print_perf(np.array([5, 15, 5]), 4)
print_perf(np.array([6, 18, 6]), 20)
print_perf(np.array([5, 10, 1, 4, 3, 1, 2, 1]), 7)
print_perf(np.array([2, 2, 2]), 4)
print_perf(np.array([5]), 4)
print_perf(np.array([0, 0, 5]), 3)
print_perf(np.array([0, 0, 0, 0, 0, 0, 10]), 3)
print_perf(np.array([0, 0, 0, 13]), 5)
print_perf(np.array([2, 0, 0, 0, 0, 0, 0, 0, 7]), 9)