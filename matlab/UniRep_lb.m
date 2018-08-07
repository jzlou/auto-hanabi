function rho_lb = UniRep_lb(rho, r_0)

R = length(rho);
rho_lb = zeros(r_0, 1);

rho_lb(r_0) = floor(rho(1:min(R, r_0 - 1)).'*(1:min(R, r_0 - 1)).'/r_0) + sum(rho(r_0 + 1:end));

if r_0 <= R
    rho_lb(r_0) = rho_lb(r_0) + rho(r_0);
end

end