function N = C(k, x)

n = x*[1:length(x)].';

if k > n
    N = 0;
    return;
end

Ns = zeros(length(x), n + 1);
for xx = 1:length(x)
    for nn = 0:n
        if x(xx)
            Ns(xx, nn + 1) = RestComps0(nn, x(xx), xx);
        else
            if ~nn
                Ns(xx, nn + 1) = 1;
            end
        end
    end
end

N0 = Ns(1,:);
for xx = 2:length(x)
    N0 = conv(N0(1:k+1), Ns(xx , 1:k+1), 'full');
end

N = N0(k + 1);

end
