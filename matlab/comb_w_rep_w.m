function [C] = comb_w_rep_w(N, x)

x = colvec(x);
M = length(x);

C = comb_w_rep_rec(N, M, x);

return
end

function [C] = comb_w_rep_rec(N, M, x)

if N==0 || N==sum(x)
    C = 1;
    return;
end

C = 0;
for kk = max(0, N - sum(x(2:end))):min(x(1), N)
    C = C + comb_w_rep_rec(N - kk, M - 1, x(2:end));
end

return;
end