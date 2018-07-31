function N = f(n, x)

if n==1
    N = sum(x);
    return;
end

K = length(x);

N = x(1)*f(n - 1, x + [-1, zeros(1, K - 1)]);

for kk = 2:K
    N = N + x(kk)*f(n-1, x + [zeros(1, kk - 2), 1, -1, zeros(1, K - kk)]);
end

return