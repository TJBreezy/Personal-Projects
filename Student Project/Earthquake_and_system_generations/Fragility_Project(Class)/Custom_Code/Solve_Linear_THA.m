function [u, v, a] = Solve_Linear_THA(M, K, C, ag, dt)
% Solves the linear equation of motion M*u'' + C*u' + K*u = -M*1*ag
% using the Newmark-Beta method (Average Acceleration Method assumed).
% Inputs:
%   M, K, C: Mass, Stiffness, Damping matrices
%   ag: Ground acceleration time history vector (as column vector)
%   dt: Time step
% Outputs:
%   u, v, a: Relative displacement, velocity, and total acceleration
%            matrices [nDOF x nTimeSteps]

nDOF = size(M, 1);
nTimeSteps = length(ag);
influence_vector = ones(nDOF, 1); % Influence vector for ground motion

% Newmark-Beta parameters (Average Acceleration Method)
gamma_nb = 0.5;
beta_nb = 0.25;

% Initial conditions
u = zeros(nDOF, nTimeSteps);
v = zeros(nDOF, nTimeSteps);
a = zeros(nDOF, nTimeSteps); % Relative acceleration

% Initial acceleration (relative)
P0 = -M * influence_vector * ag(1); % Effective force at time 0
a(:, 1) = M \ (P0 - C * v(:, 1) - K * u(:, 1)); % Solve M*a = P - C*v - K*u

% Effective stiffness matrix
K_eff = K + (gamma_nb / (beta_nb * dt)) * C + (1 / (beta_nb * dt^2)) * M;
inv_K_eff = inv(K_eff); % Precompute inverse for efficiency

% Precompute constants for speed
a1 = (1 / (beta_nb * dt^2)) * M + (gamma_nb / (beta_nb * dt)) * C;
a2 = (1 / (beta_nb * dt)) * M + (gamma_nb / beta_nb - 1) * C;
a3 = (1 / (2 * beta_nb) - 1) * M + dt * (gamma_nb / (2 * beta_nb) - 1) * C;

% Time stepping loop
for i = 1:(nTimeSteps - 1)
    % Effective force vector at next step (i+1)
    P_eff_next = -M * influence_vector * ag(i+1) + a1 * u(:, i) + a2 * v(:, i) + a3 * a(:, i);

    % Solve for displacement at next step
    u(:, i+1) = inv_K_eff * P_eff_next;

    % Calculate velocity and acceleration at next step
    a(:, i+1) = (1 / (beta_nb * dt^2)) * (u(:, i+1) - u(:, i)) - (1 / (beta_nb * dt)) * v(:, i) - (1 / (2 * beta_nb) - 1) * a(:, i);
    v(:, i+1) = v(:, i) + dt * ((1 - gamma_nb) * a(:, i) + gamma_nb * a(:, i+1));
end

% Note: Output 'a' is relative acceleration. Total acceleration = a_rel + ag
% We typically need relative displacement 'u' for drift calculations.

end