function c = Comps_intraM(n, M)

if n==0
     c = 0;
    return;
end

if n==1
    c = sum(M);
    return;
end

adds = find(M);

c = 0;
for ii = adds
    tmpM = M;
    tmpM(ii) = tmpM(ii) - 1;
    if ii>1
        tmpM(ii - 1) = tmpM(ii - 1) + 1;
    end
    c = c + M(ii)*Comps_intraM(n - 1, tmpM);
end

return;
end