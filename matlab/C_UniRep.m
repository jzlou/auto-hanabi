function N = C_UniRep(rho, K)

R = find(rho);
if length(R)~=1
    warning('C_UniRep is only valid for Uniform Repetition frequencies');
    N = 1i;
    return;
end

U = sum(rho);

N = F(K + U, U, R+1);

end