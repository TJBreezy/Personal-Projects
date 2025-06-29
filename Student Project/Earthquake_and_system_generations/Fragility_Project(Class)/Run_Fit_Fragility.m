clear; clc; close all;
addpath('Provided_Code');
addpath('Custom_Code');
addpath('Custom_Code/Plotting'); % Assuming plotting functions are here

% --- User Settings ---
results_dir = 'Results';
ida_results_file = 'IDA_Results.mat';
output_fragility_file = 'Fragility_Parameters.mat';

% Define Damage States based on MIDR (EXAMPLE - VERIFY FROM FEMA P-58)
Damage_States(1).Name = 'Slight';      Damage_States(1).MIDR_Limit = 0.2;
Damage_States(2).Name = 'Moderate';    Damage_States(2).MIDR_Limit = 0.5;
Damage_States(3).Name = 'Severe';      Damage_States(3).MIDR_Limit = 1.0;
Damage_States(4).Name = 'Collapse';    Damage_States(4).MIDR_Limit = 4.0; % Or based on analysis failure

n_DS = length(Damage_States);

% --- Load IDA Results ---
load(fullfile(results_dir, ida_results_file)); % Loads IDA_Results and System structs
PGA_levels = IDA_Results.PGA_levels;
MIDR_Linear = IDA_Results.MIDR_Linear;
MIDR_Nonlinear = IDA_Results.MIDR_Nonlinear;
[n_GMs, n_PGA_levels] = size(MIDR_Nonlinear);

fprintf('  IDA data: %d GMs × %d PGA levels\n', size(MIDR_Linear,1), size(MIDR_Linear,2));
fprintf('  Non-NaN linear drifts: %d out of %d\n', ...
        nnz(~isnan(MIDR_Linear)), numel(MIDR_Linear));
fprintf('  Non-NaN nonlinear drifts: %d out of %d\n', ...
        nnz(~isnan(MIDR_Nonlinear)), numel(MIDR_Nonlinear));

% --- Initialize Fragility Results Storage ---
Fragility = struct();
Fragility.Damage_States = Damage_States;
Fragility.Linear.theta = NaN(n_DS, 1);
Fragility.Linear.beta = NaN(n_DS, 1);
Fragility.Nonlinear.theta = NaN(n_DS, 1);
Fragility.Nonlinear.beta = NaN(n_DS, 1);

% --- Fit Fragility Curves ---
fprintf('Fitting Fragility Curves using MLE...\n');

for i_ds = 1:n_DS
    DS_Limit = Damage_States(i_ds).MIDR_Limit;
    fprintf('  Fitting for Damage State: %s (MIDR > %.4f)\n', Damage_States(i_ds).Name, DS_Limit);

    % --- Process for MLE (Nonlinear) ---
    IM_nl = []; % Vector of IM levels for all points
    Outcome_nl = []; % Vector of 0/1 outcomes for all points
    for i_gm = 1:n_GMs
        for i_pga = 1:n_PGA_levels
            if ~isnan(MIDR_Nonlinear(i_gm, i_pga))
                IM_nl(end+1) = PGA_levels(i_pga);
                Outcome_nl(end+1) = (MIDR_Nonlinear(i_gm, i_pga) > DS_Limit);
            end
        end
    end
    if isempty(IM_nl) || sum(Outcome_nl) == 0 || sum(Outcome_nl) == length(Outcome_nl)
         fprintf('    Skipping Nonlinear fit for DS %d: Insufficient data or all/no points exceeded.\n', i_ds);
    else
        [theta_nl, beta_nl] = Fit_Fragility_MLE(IM_nl', Outcome_nl');
        Fragility.Nonlinear.theta(i_ds) = theta_nl;
        Fragility.Nonlinear.beta(i_ds) = beta_nl;
        fprintf('    Nonlinear Fit: theta = %.4f, beta = %.4f\n', theta_nl, beta_nl);
    end


    % --- Process for MLE (Linear) ---
     IM_lin = []; % Vector of IM levels for all points
    Outcome_lin = []; % Vector of 0/1 outcomes for all points
     for i_gm = 1:n_GMs
        for i_pga = 1:n_PGA_levels
             if ~isnan(MIDR_Linear(i_gm, i_pga))
                IM_lin(end+1) = PGA_levels(i_pga);
                Outcome_lin(end+1) = (MIDR_Linear(i_gm, i_pga) > DS_Limit);
            end
        end
    end
    if isempty(IM_lin) || sum(Outcome_lin) == 0 || sum(Outcome_lin) == length(Outcome_lin)
        fprintf('    Skipping Linear fit for DS %d: Insufficient data or all/no points exceeded.\n', i_ds);
    else
        [theta_lin, beta_lin] = Fit_Fragility_MLE(IM_lin', Outcome_lin');
        Fragility.Linear.theta(i_ds) = theta_lin;
        Fragility.Linear.beta(i_ds) = beta_lin;
         fprintf('    Linear Fit   : theta = %.4f, beta = %.4f\n', theta_lin, beta_lin);
    end

end % End Damage State loop

% --- Save Fragility Parameters ---
save(fullfile(results_dir, output_fragility_file), 'Fragility');
fprintf('\nFragility fitting complete. Parameters saved to %s.\n', fullfile(results_dir, output_fragility_file));

% --- Plot Fragility Curves ---
Plot_Fragility_Curves(Fragility, PGA_levels); % Call plotting function