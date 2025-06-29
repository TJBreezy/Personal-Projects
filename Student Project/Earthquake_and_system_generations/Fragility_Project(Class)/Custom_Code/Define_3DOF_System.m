function [System] = Define_3DOF_System()
% Defines the parameters for a 3DOF shear building model.
% Outputs:
%   System - Structure containing M, K_initial, C, h, Nonlinear_Params

fprintf('Defining 3DOF System Parameters...\n');

% --- Basic Properties ---
m = 1000; % Mass per floor (kg or kips, keep units consistent)
k = 50000; % Base stiffness per floor (N/m or kips/in)
h_story = 3.0; % Story height (m or in)
n_stories = 3;

System.nDOF = n_stories;
System.h = ones(n_stories, 1) * h_story; % Story heights

% --- Mass Matrix ---
System.M = diag(ones(n_stories, 1) * m);

% --- Initial Stiffness Matrix (Shear Building) ---
% Assuming stiffness is proportional, maybe decreasing slightly with height
k_factors = [1.0; 0.9; 0.8]; % Stiffness relative to base floor
k_story = k * k_factors;     % Stiffness of each story spring

K_initial = zeros(n_stories);
for i = 1:n_stories
    if i == 1
        K_initial(i, i) = k_story(i) + k_story(i+1);
        K_initial(i, i+1) = -k_story(i+1);
        K_initial(i+1, i) = -k_story(i+1);
    elseif i < n_stories
        K_initial(i, i) = k_story(i) + k_story(i+1);
        K_initial(i, i+1) = -k_story(i+1);
        K_initial(i+1, i) = -k_story(i+1);
    else % Last story
        K_initial(i, i) = k_story(i);
    end
end
System.K_initial = K_initial;

% --- Damping Matrix (Rayleigh Damping) ---
target_damping_ratio = 0.05; % 5% damping

% Calculate natural frequencies (omega) and periods (T)
[eig_vec, eig_val_sq] = eig(System.K_initial, System.M);
omega_sq = diag(eig_val_sq);
omega = sqrt(omega_sq);
T = 2*pi./omega;
fprintf('  Natural Periods (s): %.3f, %.3f, %.3f\n', T(1), T(2), T(3));

% Use first two modes for Rayleigh damping coeffs (alpha, beta)
i = 1; j = 2;
A = 0.5 * [1/omega(i), omega(i); 1/omega(j), omega(j)];
coeffs = A \ [target_damping_ratio; target_damping_ratio];
alpha_damp = coeffs(1);
beta_damp = coeffs(2);

System.C = alpha_damp * System.M + beta_damp * System.K_initial;

% --- Nonlinear Parameters (Bilinear Model) ---
yield_drift_ratio = 0.005; % Yield drift / story height (Reduced from 0.015)
alpha_post_yield = 0.02;  % Post-yield stiffness / initial stiffness (Reduced from 0.10)

System.Nonlinear_Params.k_story_initial = k_story;
System.Nonlinear_Params.dy = yield_drift_ratio * System.h; % Yield displacement for each story
System.Nonlinear_Params.Fy = System.Nonlinear_Params.k_story_initial .* System.Nonlinear_Params.dy; % Yield force
System.Nonlinear_Params.alpha_post_yield = alpha_post_yield;

fprintf('System Definition Complete.\n\n');

end