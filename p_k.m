function C = p_k(n, k)

if n==0 && k==0
    C = 1;
    return;
end

if n<=0 || k<=0
    C = 0;
    return;
end

C = p_k(n - k, k) + p_k(n - 1, k - 1);

end