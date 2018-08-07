
rho = [5 15 5].';

N = rho.'*[1:length(rho)].';

U = sum(rho);

rho_bar = N/U;

K = 4;

R_lb = find(rho, 1, 'last');

U_lb = floor(N/R_lb);

N_lb = R_lb*U_lb;

lb = F(K + U_lb, U_lb, R_lb + 1);

lb = F(K + sum(rho), sum(rho), 1 + 1);

ub = F(K + ceil(N/floor(rho_bar)), ceil(N/floor(rho_bar)), floor(rho_bar) + 1);

ub = F(K + ceil(N/floor(rho_bar)), ceil(N/floor(rho_bar)), floor(rho_bar) + 1);

% ub = F(K + ceil(N/floor(rho_bar)), ceil(N/floor(rho_bar)), floor(rho_bar) + 1);
