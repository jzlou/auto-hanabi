function C = p(N, M, K)

% partition N into M non-negative bins of at most K

C = p_wiki(K+1, M, N+M);

end

function C = p_wiki(N, M, n)
% https://en.wikipedia.org/wiki/Partition_(number_theory)

if n<=0 || M<=0 || M>n || n>N*M
    C = 0;
    return;
end

if M==n || M==1 || N==1
    C = 1;
    return;
end

if N>=n
    C = p_k(n, M);
    return;
end

C = p_wiki(N, M - 1, n) + p_wiki(N-1, M, n-M);

end

