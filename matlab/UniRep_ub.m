function rho_ub = UniRep_ub(rho, r_0)

R = length(rho);
rho_ub = zeros(r_0, 1);

rho_ub(r_0) = sum(rho(1:min(R, r_0 - 1))) + ceil(rho(r_0 + 1:R).'*(r_0 + 1:R).'/r_0);

if r_0 <= R
    rho_ub(r_0) = rho_ub(r_0) + rho(r_0);
end

end