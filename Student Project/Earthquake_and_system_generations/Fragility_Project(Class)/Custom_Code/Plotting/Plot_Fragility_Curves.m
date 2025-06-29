function Plot_Fragility_Curves(Fragility, PGA_plot_range)
% Plots the fitted fragility curves.

figure;
hold on;
grid on;

pga_fine = linspace(min(PGA_plot_range)*0.5, max(PGA_plot_range)*1.1, 200); % Finer range for plotting CDFs
colors = lines(length(Fragility.Damage_States)); % Different color for each DS
line_styles = {'-', '--'}; % Solid for Nonlinear, Dashed for Linear

legend_entries = {};

for i_ds = 1:length(Fragility.Damage_States)
    DS_Name = Fragility.Damage_States(i_ds).Name;

    % Nonlinear
    theta_nl = Fragility.Nonlinear.theta(i_ds);
    beta_nl = Fragility.Nonlinear.beta(i_ds);
    if ~isnan(theta_nl) && ~isnan(beta_nl) && beta_nl > 0
        prob_exceed_nl = normcdf(log(pga_fine / theta_nl) / beta_nl);
        plot(pga_fine, prob_exceed_nl, 'Color', colors(i_ds,:), 'LineStyle', line_styles{1}, 'LineWidth', 1.5);
        legend_entries{end+1} = sprintf('%s (Nonlinear)', DS_Name);
    end

     % Linear
    theta_lin = Fragility.Linear.theta(i_ds);
    beta_lin = Fragility.Linear.beta(i_ds);
     if ~isnan(theta_lin) && ~isnan(beta_lin) && beta_lin > 0
        prob_exceed_lin = normcdf(log(pga_fine / theta_lin) / beta_lin);
        plot(pga_fine, prob_exceed_lin, 'Color', colors(i_ds,:), 'LineStyle', line_styles{2}, 'LineWidth', 1.5);
         legend_entries{end+1} = sprintf('%s (Linear)', DS_Name);
    end

end

xlabel('Peak Ground Acceleration (PGA) (g)');
ylabel('Probability of Exceedance');
title('Fragility Curves (Linear vs. Nonlinear)');
legend(legend_entries, 'Location', 'bestoutside');
ylim([0 1]);
xlim([0 max(PGA_plot_range)]); % Adjust xlim if needed

hold off;

end