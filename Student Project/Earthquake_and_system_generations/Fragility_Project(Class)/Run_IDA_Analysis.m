clear; clc; close all;
addpath('Provided_Code');
addpath('Custom_Code');

% --- User Settings ---
gm_dir = 'Ground_Motions';
gm_files = dir(fullfile(gm_dir, 'GM_*.mat')); % Get list of generated GM files
output_dir = 'Results';
output_filename = 'IDA_Results.mat';

% Define PGA levels for IDA (adjust range and number as needed)
PGA_levels = 0.05:0.05:1.5; % Example: 0.05g to 1.5g in 0.05g steps
n_PGA_levels = length(PGA_levels);
n_GMs = length(gm_files);

% --- Setup System ---
System = Define_3DOF_System();
M = System.M;
K_lin = System.K_initial;
C = System.C;
h = System.h;
Nonlinear_Params = System.Nonlinear_Params;

% --- Initialize Results Storage ---
IDA_Results = struct();
IDA_Results.PGA_levels = PGA_levels;
IDA_Results.GM_Filenames = cell(n_GMs, 1);
IDA_Results.MIDR_Linear = NaN(n_GMs, n_PGA_levels);
IDA_Results.MIDR_Nonlinear = NaN(n_GMs, n_PGA_levels);

% --- Run IDA ---
if ~exist(output_dir, 'dir'); mkdir(output_dir); end
fprintf('Starting IDA Analysis for %d ground motions...\n', n_GMs);

% Initialize temporary storage for parfor results
temp_GM_Filenames = cell(n_GMs, 1);
temp_MIDR_Linear = cell(n_GMs, 1);
temp_MIDR_Nonlinear = cell(n_GMs, 1);

parfor i_gm = 1:n_GMs % Use parfor for parallel processing if available
    fprintf('  Processing GM %d of %d: %s\n', i_gm, n_GMs, gm_files(i_gm).name);
    
    % Load GM data within the loop
    gm_data_struct = load(fullfile(gm_dir, gm_files(i_gm).name));
    
    % Store filename for this iteration
    current_gm_filename = gm_files(i_gm).name; 

    accel_ns = gm_data_struct.quake_data(:, 1);
    % accel_ew = gm_data_struct.quake_data(:, 4); % EW not used in this version
    dt_gm = gm_data_struct.dt; % Use a different variable name from outside loop if needed
    PGA_orig_gm = gm_data_struct.PGA_orig;

    % Choose one component for analysis (e.g., NS) or use resultant/max
    ag_base = accel_ns; % Using NS component for this example
    if PGA_orig_gm == 0; PGA_orig_gm = 1e-6; end % Avoid division by zero

    % Initialize results for this specific GM iteration
    iter_midr_lin = NaN(1, n_PGA_levels);
    iter_midr_nl = NaN(1, n_PGA_levels);

    for i_pga = 1:n_PGA_levels
        PGA_target = PGA_levels(i_pga);
        % Ensure PGA_orig_gm is treated as cm/s^2 if accel is cm/s^2, scale factor expects g vs g
        % Assuming quake_SAC2d outputs in cm/s^2, PGA_orig is max abs value in cm/s^2
        % Scale factor should be PGA_target_g / PGA_orig_g
        PGA_orig_g = PGA_orig_gm / 981; % Convert cm/s^2 to g
        if PGA_orig_g == 0; PGA_orig_g = 1e-6; end % Avoid division by zero again
        scale_factor = PGA_target / PGA_orig_g; 

        ag_scaled = ag_base * scale_factor; % Scale the chosen component

        % --- Linear Analysis ---
        % Define M, K_lin, C, h, Nonlinear_Params explicitly for parfor slicing
        M_par = M; K_lin_par = K_lin; C_par = C; h_par = h; Nonlinear_Params_par = Nonlinear_Params;
        try % Add error handling for solver issues
            [u_lin, ~, ~] = Solve_Linear_THA(M_par, K_lin_par, C_par, ag_scaled, dt_gm);
            [midr_lin, ~] = Calculate_MIDR(u_lin, h_par);
            iter_midr_lin(i_pga) = midr_lin;
        catch ME_lin
            fprintf('    Warning: Linear solver failed for GM %d (%s), PGA %.2fg. Error: %s\n', i_gm, current_gm_filename, PGA_target, ME_lin.message);
        end

        % --- Nonlinear Analysis ---
        try
            [u_nl, ~, ~, ~] = Solve_Nonlinear_THA(M_par, C_par, ag_scaled, dt_gm, Nonlinear_Params_par, h_par);
            [midr_nl, ~] = Calculate_MIDR(u_nl, h_par);
            iter_midr_nl(i_pga) = midr_nl;
        catch ME_nl
             fprintf('    Warning: Nonlinear solver failed for GM %d (%s), PGA %.2fg. Error: %s\n', i_gm, current_gm_filename, PGA_target, ME_nl.message);
        end

    end % End PGA level loop
    
    % Store results for this iteration in temporary cell arrays
    temp_GM_Filenames{i_gm} = current_gm_filename;
    temp_MIDR_Linear{i_gm} = iter_midr_lin;
    temp_MIDR_Nonlinear{i_gm} = iter_midr_nl;

end % End GM loop

% --- Consolidate results from temporary storage ---
IDA_Results.GM_Filenames = temp_GM_Filenames;
% Convert cell arrays back to numeric matrices
IDA_Results.MIDR_Linear = cell2mat(temp_MIDR_Linear); 
IDA_Results.MIDR_Nonlinear = cell2mat(temp_MIDR_Nonlinear);

% --- Save Results ---
save(fullfile(output_dir, output_filename), 'IDA_Results', 'System');
fprintf('\nIDA Analysis Complete. Results saved to %s.\n', fullfile(output_dir, output_filename));

% --- Optional: Basic IDA Plot ---
figure;
subplot(1,2,1);
plot(IDA_Results.MIDR_Linear', IDA_Results.PGA_levels, 'r-');
xlabel('Max Interstory Drift Ratio (MIDR)'); ylabel('PGA (g)');
title('IDA Curves - Linear'); grid on; ylim([0 max(PGA_levels)]);
subplot(1,2,2);
plot(IDA_Results.MIDR_Nonlinear', IDA_Results.PGA_levels, 'b-');
xlabel('Max Interstory Drift Ratio (MIDR)'); ylabel('PGA (g)');
title('IDA Curves - Nonlinear'); grid on; ylim([0 max(PGA_levels)]);
sgtitle('Incremental Dynamic Analysis Results');