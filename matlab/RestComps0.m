function F = RestComps0(n, k, w)

F = RestComps1(n + k, k, w + 1);

end
    
function F = RestComps1(n, k, w)

F = 0;
for jj = 0:min(k, floor((n - k)/w))
    if k <= n - jj*w
        F = F + (-1)^jj*nchoosek(k, jj)*nchoosek(n - jj*w - 1, k - 1);
    end
end

end