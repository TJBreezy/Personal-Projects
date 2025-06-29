function Plot_IDA_Curves(IDA_Results)
% Plots the IDA curves (PGA vs. MIDR) for linear and nonlinear analyses.
% Input:
%   IDA_Results: Structure containing IDA results (.PGA_levels,
%                .MIDR_Linear, .MIDR_Nonlinear)

figure('Name', 'IDA Curves', 'NumberTitle', 'off');

PGA_levels = IDA_Results.PGA_levels;
MIDR_Linear = IDA_Results.MIDR_Linear;
MIDR_Nonlinear = IDA_Results.MIDR_Nonlinear;

max_midr_plot = max([max(MIDR_Linear,[],'all'), max(MIDR_Nonlinear,[],'all')], [], 'omitnan');
if isempty(max_midr_plot) || max_midr_plot == 0 || ~isfinite(max_midr_plot)
    max_midr_plot = 0.1; % Default max plot limit if no data or only zeros
end
plot_limit_midr = min(max_midr_plot * 1.1, 0.15); % Set a reasonable upper limit, e.g., 15% drift
plot_limit_pga = max(PGA_levels) * 1.05;

% --- Linear IDA Plot ---
subplot(1, 2, 1);
hold on;
for i = 1:size(MIDR_Linear, 1) % Loop through each ground motion
    plot(MIDR_Linear(i, :), PGA_levels, '-', 'Color', [0.7 0.7 0.7]); % Plot each GM in light gray
end
% Plot median IDA curve (optional, requires calculation)
% median_midr_lin = median(MIDR_Linear, 1, 'omitnan');
% plot(median_midr_lin, PGA_levels, 'r-', 'LineWidth', 1.5);

hold off;
grid on;
box on;
xlabel('Max Interstory Drift Ratio (MIDR)');
ylabel('PGA (g)');
title('IDA Curves - Linear Model');
xlim([0 plot_limit_midr]);
ylim([0 plot_limit_pga]);
set(gca, 'FontSize', 10);

% --- Nonlinear IDA Plot ---
subplot(1, 2, 2);
hold on;
for i = 1:size(MIDR_Nonlinear, 1) % Loop through each ground motion
    plot(MIDR_Nonlinear(i, :), PGA_levels, '-', 'Color', [0.7 0.7 0.7]); % Plot each GM in light gray
end
% Plot median IDA curve (optional, requires calculation)
median_midr_nl = median(MIDR_Nonlinear, 1, 'omitnan');
plot(median_midr_nl, PGA_levels, 'b-', 'LineWidth', 1.5); % Plot median in blue

hold off;
grid on;
box on;
xlabel('Max Interstory Drift Ratio (MIDR)');
ylabel('PGA (g)');
title('IDA Curves - Nonlinear Model');
xlim([0 plot_limit_midr]);
ylim([0 plot_limit_pga]);
legend('Individual GMs', 'Median IDA', 'Location', 'southeast'); % Add legend if plotting median
set(gca, 'FontSize', 10);

sgtitle('Incremental Dynamic Analysis Results Cloud'); % Overall figure title

end