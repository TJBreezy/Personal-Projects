import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
import warnings

def _lognormal_cdf(x, theta, beta):
    """Calculates the lognormal CDF value(s). P[X <= x] = Phi(ln(x/theta)/beta)"""
    # Ensure input is numpy array for vectorized operations
    x = np.asarray(x)
    
    # Handle non-positive x values (CDF is 0) and theta/beta constraints
    if theta <= 0 or beta <= 0:
        # This case should ideally be prevented by optimization bounds/transforms
        # Return NaN or raise error, depending on desired behavior
        return np.full_like(x, np.nan, dtype=float) 
        
    # Avoid division by zero or log(0) if x contains non-positive values
    cdf_values = np.zeros_like(x, dtype=float)
    positive_mask = x > 0
    
    # Calculate CDF only for positive x values
    if np.any(positive_mask):
        log_arg = np.log(x[positive_mask] / theta) / beta
        cdf_values[positive_mask] = norm.cdf(log_arg)
        
    return cdf_values

def _negative_log_likelihood(params, x, k, n):
    """
    Negative log-likelihood function for lognormal fragility curve fitting.

    Args:
        params (list/tuple): Parameters to optimize [ln_theta, ln_beta].
        x (np.ndarray): Intensity measure levels.
        k (np.ndarray): Number of exceedances at each level.
        n (np.ndarray): Number of trials (ground motions) at each level.

    Returns:
        float: Negative log-likelihood value.
    """
    ln_theta, ln_beta = params
    theta = np.exp(ln_theta)
    beta = np.exp(ln_beta)

    if beta <= 1e-6: # Prevent excessively small beta causing issues
        return np.inf

    # Calculate probability of exceedance using lognormal CDF
    # P(Exceed | IM=x) = P(Capacity <= x) = Phi(ln(x/theta)/beta)
    p = _lognormal_cdf(x, theta, beta)

    # Clip probabilities to avoid log(0) errors
    epsilon = 1e-9
    p = np.clip(p, epsilon, 1 - epsilon)

    # Calculate log-likelihood for binomial distribution (ignoring constant combinatorial term)
    # LL = sum(k * log(p) + (n - k) * log(1 - p))
    log_likelihood = np.sum(k * np.log(p) + (n - k) * np.log(1 - p))

    # Return negative log-likelihood
    return -log_likelihood

def fit_fragility_curve_MLE(im_levels: np.ndarray,
                             num_exceed: np.ndarray,
                             num_trials: np.ndarray
                             ) -> tuple[float, float, bool, object]:
    """
    Fits a lognormal CDF fragility curve using Maximum Likelihood Estimation (MLE).

    Args:
        im_levels (np.ndarray): Vector of intensity measure levels.
        num_exceed (np.ndarray): Vector of the number of exceedances at each IM level.
        num_trials (np.ndarray): Vector of the total trials (GMs) at each IM level.

    Returns:
        tuple[float, float, bool, object]: A tuple containing:
            - theta (float): Estimated median capacity (θ). NaN if fitting fails.
            - beta (float): Estimated log-standard deviation (β). NaN if fitting fails.
            - success (bool): Flag indicating if optimization was successful.
            - opt_result (object): The full optimization result object from scipy.optimize.minimize.
    """
    im_levels = np.asarray(im_levels)
    num_exceed = np.asarray(num_exceed)
    num_trials = np.asarray(num_trials)

    if not (im_levels.shape == num_exceed.shape == num_trials.shape):
        raise ValueError("Input arrays must have the same shape.")
    if np.any(num_exceed > num_trials):
        raise ValueError("num_exceed cannot be greater than num_trials.")
    if np.any(num_exceed < 0) or np.any(num_trials <= 0):
        raise ValueError("num_exceed must be >= 0 and num_trials must be > 0.")

    # --- Initial Guesses ---
    # Handle cases where all exceed or none exceed
    if np.all(num_exceed == 0):
        warnings.warn("All num_exceed are zero. Fragility curve is likely zero everywhere. Returning NaNs.", RuntimeWarning)
        return np.nan, np.nan, False, None
    if np.all(num_exceed == num_trials):
        warnings.warn("All trials resulted in exceedance. Fragility curve is likely one everywhere. Returning NaNs.", RuntimeWarning)
        return np.nan, np.nan, False, None
        
    # Calculate empirical exceedance rates
    empirical_rates = num_exceed / num_trials
    
    # Guess theta: IM level where rate is closest to 0.5, or geometric mean if needed
    valid_rates_mask = (empirical_rates > 0) & (empirical_rates < 1)
    if np.any(valid_rates_mask):
         theta0_guess = np.interp(0.5, empirical_rates[valid_rates_mask], im_levels[valid_rates_mask])
         # Fallback if interpolation fails (e.g., rates don't bracket 0.5)
         if np.isnan(theta0_guess) or theta0_guess <= 0:
              theta0_guess = np.exp(np.mean(np.log(im_levels[valid_rates_mask])))
    else: # If only 0% and 100% rates exist
         first_one = np.where(empirical_rates == 1)[0]
         last_zero = np.where(empirical_rates == 0)[0]
         if len(first_one) > 0 and len(last_zero) > 0:
              idx0 = last_zero[-1]
              idx1 = first_one[0]
              if idx0 < idx1: # Ensure there's a transition
                   theta0_guess = np.sqrt(im_levels[idx0] * im_levels[idx1]) # Geometric mean
              else:
                   theta0_guess = np.median(im_levels) # Fallback guess
         else:
              theta0_guess = np.median(im_levels) # Fallback guess
              
    # Ensure theta guess is positive
    theta0_guess = max(theta0_guess, np.min(im_levels[im_levels > 0]) * 0.1, 1e-6) 

    # Guess beta: Common starting value (can be refined based on slope)
    beta0_guess = 0.5

    # Initial parameters for optimization (using log transforms)
    params0 = np.array([np.log(theta0_guess), np.log(beta0_guess)])

    # --- Optimization ---
    # Use 'Nelder-Mead' or 'L-BFGS-B' etc.
    # L-BFGS-B can handle bounds if not using log-transform, but transform is often more stable.
    # Nelder-Mead is robust but might be slower.
    opt_method = 'Nelder-Mead' #'L-BFGS-B'
    
    result = minimize(
        _negative_log_likelihood,
        params0,
        args=(im_levels, num_exceed, num_trials),
        method=opt_method,
        options={'maxiter': 1000, 'adaptive': True} # Options for Nelder-Mead
        # bounds=bounds # Example if using L-BFGS-B with direct params
    )

    if result.success:
        ln_theta_opt, ln_beta_opt = result.x
        theta_opt = np.exp(ln_theta_opt)
        beta_opt = np.exp(ln_beta_opt)
        success = True
        print(f"MLE Optimization Successful: theta={theta_opt:.4f}, beta={beta_opt:.4f} (Method: {opt_method})")
    else:
        warnings.warn(f"MLE optimization failed: {result.message}", RuntimeWarning)
        theta_opt = np.nan
        beta_opt = np.nan
        success = False

    return theta_opt, beta_opt, success, result


# Example usage (optional):
# if __name__ == '__main__':
#     # Example Data (replace with your actual data)
#     im_test = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]) # IM levels (e.g., Sa in g)
#     n_trials_test = np.full_like(im_test, 40, dtype=int) # Number of GMs per level
#     # Simulate some exceedance counts based on a known underlying curve
#     true_theta = 0.5
#     true_beta = 0.4
#     prob_exceed_true = _lognormal_cdf(im_test, true_theta, true_beta)
#     np.random.seed(0) # for reproducibility
#     n_exceed_test = np.random.binomial(n=n_trials_test, p=prob_exceed_true)

#     print("Example Data:")
#     print(f"IM Levels: {im_test}")
#     print(f"Num Exceed: {n_exceed_test}")
#     print(f"Num Trials: {n_trials_test}")

#     # Fit the curve
#     theta_mle, beta_mle, fit_success, fit_result = fit_fragility_curve_MLE(
#         im_levels=im_test,
#         num_exceed=n_exceed_test,
#         num_trials=n_trials_test
#     )

#     print(f"\nFit Results:")
#     print(f"  Success: {fit_success}")
#     print(f"  Theta (MLE): {theta_mle:.4f} (True: {true_theta})")
#     print(f"  Beta (MLE):  {beta_mle:.4f} (True: {true_beta})")
#     # print(f"\nFull Optimization Result:\n{fit_result}")

#     # Plot results (optional)
#     if fit_success:
#         import matplotlib.pyplot as plt
#         plt.figure()
#         empirical_rate = n_exceed_test / n_trials_test
#         plt.plot(im_test, empirical_rate, 'bo', label='Empirical Data')

#         # Plot fitted curve
#         im_plot = np.linspace(min(im_test)*0.8, max(im_test)*1.2, 200)
#         prob_exceed_mle = _lognormal_cdf(im_plot, theta_mle, beta_mle)
#         plt.plot(im_plot, prob_exceed_mle, 'r-', label=f'MLE Fit ($\theta={theta_mle:.3f}, \beta={beta_mle:.3f}$)')

#         # Plot true curve
#         prob_exceed_true_plot = _lognormal_cdf(im_plot, true_theta, true_beta)
#         plt.plot(im_plot, prob_exceed_true_plot, 'g--', label=f'True Curve ($\theta={true_theta:.3f}, \beta={true_beta:.3f}$)')

#         plt.xlabel("Intensity Measure (IM)")
#         plt.ylabel("Probability of Exceedance")
#         plt.title("Fragility Curve Fitting (MLE)")
#         plt.legend()
#         plt.grid(True)
#         plt.ylim([0, 1])
#         plt.show()

