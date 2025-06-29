function [theta, beta] = Fit_Fragility_MLE(IM_levels_all, Outcome_all)
% Fits a lognormal fragility curve using Maximum Likelihood Estimation.
% Inputs:
%   IM_levels_all: Vector of intensity measure levels for EACH analysis point
%   Outcome_all: Vector (same size as IM_levels_all) of outcomes (1=exceeded, 0=not exceeded)
% Outputs:
%   theta: Median capacity
%   beta: Logarithmic standard deviation

% Define the negative log-likelihood function
negLogLikelihood = @(params) -sum( ...
    Outcome_all .* log(normcdf(log(IM_levels_all / exp(params(1))) / params(2))) + ...
    (1 - Outcome_all) .* log(1 - normcdf(log(IM_levels_all / exp(params(1))) / params(2))) ...
    );

% Initial guess for parameters [log(theta), beta]
median_guess = median(IM_levels_all(Outcome_all == 1)); % Guess median from failed cases
if isempty(median_guess) || median_guess == 0; median_guess = median(IM_levels_all); end
if median_guess == 0; median_guess = 0.1; end % Handle edge case
beta_guess = 0.4; % Typical starting guess
initial_params = [log(median_guess), beta_guess];

% Optimization options
options = optimset('MaxFunEvals', 1000, 'MaxIter', 1000, 'Display', 'off');

% Perform optimization to minimize the negative log-likelihood
try
    [opt_params, ~, exitflag] = fminsearch(negLogLikelihood, initial_params, options);
    if exitflag <= 0
        warning('MLE optimization did not converge.');
        theta = NaN;
        beta = NaN;
        return;
    end
catch ME
     warning('Error during MLE optimization: %s', ME.message);
     theta = NaN;
     beta = NaN;
     return;
end

% Extract results
theta = exp(opt_params(1));
beta = opt_params(2);

% Basic check on beta reasonableness
if beta <= 0 || beta > 2.0 % Beta shouldn't be non-positive or excessively large
    warning('MLE resulted in an unreasonable beta value (%.2f). Check data/fit.', beta);
    % May decide to cap beta or return NaN depending on desired robustness
end

end