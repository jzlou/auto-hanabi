function [C, mem] = comb_w_rep(N, x)

x = colvec(x);
M = length(x);

mem = -ones([N; x + 1].');

[C, mem] = comb_w_rep_dyn(N, M, x, mem);

return
end

function [C, mem] = comb_w_rep_dyn(N, M, x, mem)

if N==0
    C = 1;
    return;
end

mem_size = size(mem);
mem_dims = length(mem_size);
J = [zeros(mem_dims - M, 1); x] + 1;
J(2:end,:) = J(2:end,:)-1;
ind = cumprod([1 mem_size(1:end-1)])*J;
if mem(ind)==-1
    
    if N==sum(x)
        C = 1;
        mem(ind) = C;
        return;
    end
    
    C = 0;
    for kk = max(0, N - sum(x(2:end))):min(x(1), N)
        C = C + comb_w_rep_dyn(N - kk, M - 1, x(2:end), mem);
    end
    
    mem(ind) = C;
    return;
    
end

C = mem(ind);

return
end