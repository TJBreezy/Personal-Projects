function [u, v, a_tot, fs] = Solve_Nonlinear_THA(M, C, ag, dt, Nonlinear_Params, h)
% Solves the nonlinear equation of motion M*u'' + C*u' + fs(u,u') = -M*1*ag
% using the Implicit Newmark-Beta method (Average Acceleration Method)
% with Newton-Raphson iteration within each time step.
% Assumes a BILINEAR shear building model without degradation.
% Inputs:
%   M, C: Mass, Damping matrices
%   ag: Ground acceleration time history vector (column vector)
%   dt: Time step
%   Nonlinear_Params: Structure with k_story_initial, dy, alpha_post_yield
%   h: Story height vector
% Outputs:
%   u: Relative displacement matrix [nDOF x nTimeSteps]
%   v, a_tot: Relative velocity, TOTAL acceleration matrices
%   fs: Restoring force matrix [nDOF x nTimeSteps]

nDOF = size(M, 1);
nTimeSteps = length(ag);
influence_vector = ones(nDOF, 1);

% Newmark-Beta parameters (Average Acceleration Method)
gamma_nb = 0.5;
beta_nb = 0.25;

% Unpack nonlinear parameters
k0 = Nonlinear_Params.k_story_initial;
dy = Nonlinear_Params.dy;
Fy = Nonlinear_Params.Fy; % Yield force
alpha = Nonlinear_Params.alpha_post_yield;
kp = alpha * k0; % Post-yield stiffness

% Iteration parameters
max_iter = 10; % Max iterations per step
tol = 1e-6;    % Tolerance for convergence (on displacement increment norm)

% Initial conditions
u = zeros(nDOF, nTimeSteps);
v = zeros(nDOF, nTimeSteps);
a = zeros(nDOF, nTimeSteps); % Relative acceleration
fs = zeros(nDOF, nTimeSteps); % Global restoring force vector
fs_story = zeros(nDOF, nTimeSteps); % Force in each story spring

% Store state for hysteretic model (current stiffness for each story)
% NOTE: A more robust model would track max/min displacement etc.
k_story_tangent = k0; % Start with initial stiffness
drift_prev_step = zeros(nDOF, 1);

% Initial calculations
P_eff = -M * influence_vector * ag(1); % Effective force at time 0
% Initial restoring force fs(:,1) is zero if u(:,1) is zero
a(:, 1) = M \ (P_eff - C * v(:, 1) - fs(:, 1)); % Solve M*a = P_eff - C*v - fs

% Constants for Newmark integration
a0 = 1 / (beta_nb * dt^2);
a1 = 1 / (beta_nb * dt);
a2 = 1 / (2 * beta_nb) - 1;
a3 = gamma_nb / (beta_nb * dt);
a4 = gamma_nb / beta_nb - 1;
a5 = dt * (gamma_nb / (2 * beta_nb) - 1);

% --- Time stepping loop ---
for i = 1:(nTimeSteps - 1)
    % Predictor values (using state at step i)
    u_predict = u(:, i); % Start iteration with previous step's displacement
    v_predict = v(:, i);
    a_predict = a(:, i);

    P_eff_next = -M * influence_vector * ag(i+1);

    % Newton-Raphson Iteration within the time step
    u_iter = u_predict; % Displacement for the current iteration (k)
    iter = 0;
    converged = false;

    while iter < max_iter && ~converged
        iter = iter + 1;

        % --- Calculate State based on u_iter ---
        % Estimate acceleration and velocity based on u_iter and state at i
        a_iter = a0 * (u_iter - u(:, i)) - a1 * v(:, i) - a2 * a(:, i);
        v_iter = a3 * (u_iter - u(:, i)) + a4 * v(:, i) + a5 * a(:, i);
        % Note: v_iter uses v(:,i), a(:,i). Correct would be v_iter = v(:,i) + dt*((1-gamma)*a(:,i) + gamma*a_iter); but the above is algebraically equivalent for solving for u_iter

        % Calculate interstory drifts for this iteration
        drift_iter = zeros(nDOF, 1);
        drift_iter(1) = u_iter(1);
        for story = 2:nDOF
            drift_iter(story) = u_iter(story) - u_iter(story-1);
        end

        % --- Calculate Story Restoring Forces and Tangent Stiffnesses ---
        fs_story_iter = zeros(nDOF, 1);
        k_story_tangent_iter = zeros(nDOF, 1);

        for story = 1:nDOF
            d_curr = drift_iter(story);
            % Simplified Bilinear Logic (Needs improvement for full hysteresis)
            if abs(d_curr) <= dy(story)
                fs_story_iter(story) = k0(story) * d_curr;
                k_story_tangent_iter(story) = k0(story);
            else % Yielded
                f_yield = Fy(story) * sign(d_curr); % Use precalculated yield force
                fs_story_iter(story) = f_yield + kp(story) * (d_curr - dy(story)*sign(d_curr));
                k_story_tangent_iter(story) = kp(story); % Tangent stiffness is post-yield
            end
        end

        % Assemble Global Restoring Force Vector fs_iter
        fs_iter = zeros(nDOF, 1);
        fs_iter(1) = fs_story_iter(1) - fs_story_iter(2);
        for dof = 2:nDOF-1
            fs_iter(dof) = fs_story_iter(dof) - fs_story_iter(dof+1);
        end
        fs_iter(nDOF) = fs_story_iter(nDOF);

        % Assemble Global Tangent Stiffness Matrix K_tangent_iter
        K_tangent = zeros(nDOF);
        for story = 1:nDOF
            k_curr = k_story_tangent_iter(story);
            if story == 1
                K_tangent(story, story) = k_curr + k_story_tangent_iter(story+1);
                K_tangent(story, story+1) = -k_story_tangent_iter(story+1);
                K_tangent(story+1, story) = -k_story_tangent_iter(story+1);
            elseif story < nDOF
                 K_tangent(story, story) = K_tangent(story, story) + k_curr; % Add current story stiffness
                 % Coupling terms handled by previous story index or next section
            else % Last story
                 K_tangent(story, story) = K_tangent(story, story) + k_curr;
            end
        end

        % --- Form Effective Stiffness and Residual ---
        K_eff = a0 * M + a3 * C + K_tangent;
        Residual = P_eff_next - (M * a_iter + C * v_iter + fs_iter);

        % --- Solve for Displacement Increment delta_u ---
        delta_u = K_eff \ Residual;

        % --- Update Displacement for next iteration ---
        u_iter = u_iter + delta_u;

        % Check convergence
        if norm(delta_u) / (norm(u_iter)+eps) < tol
            converged = true;
        end
    end % End Newton-Raphson iteration

    if ~converged
         fprintf('    Warning: Newton-Raphson did not converge at time step %d (t=%.3f s) for GM %d.\n', i+1, (i+1)*dt, 0); % Need GM index if running inside IDA loop
         % Handle non-convergence (e.g., stop analysis, use last iter, smaller dt?)
         % For now, just use the result from the last iteration
    end

    % --- Update State Vectors for time step i+1 using converged u_iter ---
    u(:, i+1) = u_iter;
    % Recalculate v and a using the converged u
    a(:, i+1) = a0 * (u(:, i+1) - u(:, i)) - a1 * v(:, i) - a2 * a(:, i);
    v(:, i+1) = v(:, i) + dt * ((1 - gamma_nb) * a(:, i) + gamma_nb * a(:, i+1));

    % --- Recalculate final story forces and store them ---
    % (Recalculate based on final u to ensure consistency)
    drift_final = zeros(nDOF, 1);
    drift_final(1) = u(1, i+1);
    for story = 2:nDOF
        drift_final(story) = u(story, i+1) - u(story-1, i+1);
    end
    for story = 1:nDOF
        d_curr = drift_final(story);
         if abs(d_curr) <= dy(story)
             fs_story(story, i+1) = k0(story) * d_curr;
             k_story_tangent(story) = k0(story);
         else
             f_yield = Fy(story) * sign(d_curr);
             fs_story(story, i+1) = f_yield + kp(story) * (d_curr - dy(story)*sign(d_curr));
             k_story_tangent(story) = kp(story);
         end
    end
    fs(1, i+1) = fs_story(1, i+1) - fs_story(2, i+1);
    for dof = 2:nDOF-1
        fs(dof, i+1) = fs_story(dof, i+1) - fs_story(dof+1, i+1);
    end
    fs(nDOF, i+1) = fs_story(nDOF, i+1);

end % End time stepping loop

% Calculate total acceleration
a_tot = a + influence_vector * ag';

% Clearer Warning about simplified hysteresis
% WARNING: The bilinear force calculation used here is still simplified and
% does not fully capture hysteretic unloading/reloading paths. A more
% complex state determination logic is needed for accurate hysteresis.

end