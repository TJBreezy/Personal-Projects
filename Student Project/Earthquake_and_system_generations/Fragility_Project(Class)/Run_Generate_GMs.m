clear; clc; close all;
addpath('Provided_Code');
addpath('Custom_Code');

% --- User Settings ---
Num_GMs = 30; % Number of ground motions to generate
Quake_Scenario = 'nrfault'; % SAC Scenario (Changed from 'la10in50')
dt = 0.01;      % Time step (s) - Should match analysis dt
f_lo = 0.10;    % Low freq cutoff for generation (Hz)
f_hi = 10.0;    % High freq cutoff for generation (Hz)
output_dir = 'Ground_Motions';

% --- Generate Motions ---
if ~exist(output_dir, 'dir'); mkdir(output_dir); end

fprintf('Generating %d ground motions for scenario: %s\n', Num_GMs, Quake_Scenario);

for i = 1:Num_GMs
    fprintf('  Generating GM %d of %d...\n', i, Num_GMs);
    seed = i; % Use loop index as seed for reproducibility

    [time, quake_data, X_params] = quake_SAC2d_nofig(Quake_Scenario, dt, f_lo, f_hi, seed);

    % Extract Original PGA (Max of NS and EW components)
    accel_ns = quake_data(:, 1);
    accel_ew = quake_data(:, 4);
    PGA_orig = max([max(abs(accel_ns)), max(abs(accel_ew))]);

    % Save data
    filename = fullfile(output_dir, sprintf('GM_%s_%02d.mat', Quake_Scenario, i));
    save(filename, 'time', 'quake_data', 'X_params', 'PGA_orig', 'dt', 'Quake_Scenario');
end

fprintf('\nGround motion generation complete. Files saved in %s.\n', output_dir);