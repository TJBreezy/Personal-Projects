function [MIDR_max, MIDR_ts] = Calculate_MIDR(u, h)
% Calculates the maximum interstory drift ratio from displacement time histories.
% Inputs:
%   u: Relative displacement matrix [nDOF x nTimeSteps]
%   h: Story height vector [nDOF x 1]
% Outputs:
%   MIDR_max: Scalar maximum absolute interstory drift ratio over all stories and time
%   MIDR_ts: Matrix of interstory drift ratios [nDOF x nTimeSteps]

[nDOF, nTimeSteps] = size(u);

% Calculate interstory drifts
interstory_drift = zeros(nDOF, nTimeSteps);
interstory_drift(1, :) = u(1, :); % First story drift is u1 relative to ground
for i = 2:nDOF
    interstory_drift(i, :) = u(i, :) - u(i-1, :);
end

% Calculate interstory drift ratios
MIDR_ts = interstory_drift ./ h; % Element-wise division

% Find the maximum absolute value
MIDR_max = max(abs(MIDR_ts), [], 'all');

end