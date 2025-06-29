import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
import warnings

def lognormal_logcdf(x, theta, beta):
    """Calculate the log of the lognormal CDF.

    Args:
        x (float or np.ndarray): Intensity measure level(s). Must be > 0.
        theta (float): Median of the lognormal distribution.
        beta (float): Logarithmic standard deviation.

    Returns:
        float or np.ndarray: Log of the CDF value(s).
    """
    # Ensure input is numpy array for vectorized operations
    x = np.asarray(x)
    # Avoid log(0) or negative values; CDF is 0 for x <= 0
    safe_x = np.maximum(x, 1e-12) # Use a small positive number instead of zero
    return norm.logcdf(np.log(safe_x / theta) / beta)

def neg_log_likelihood(params, im_levels, num_exceed, num_trials):
    """Negative log-likelihood function for fragility curve fitting.

    Assumes a lognormal CDF model.

    Args:
        params (tuple): (theta, beta) - median and log std dev.
        im_levels (np.ndarray): Array of intensity measure levels.
        num_exceed (np.ndarray): Array of number of exceedances at each IM level.
        num_trials (np.ndarray): Array of total number of trials at each IM level.

    Returns:
        float: Negative log-likelihood value. Returns np.inf if params are invalid.
    """
    theta, beta = params
    if theta <= 0 or beta <= 0:
        return np.inf # Parameters must be positive

    # Calculate probability of exceedance (P) using lognormal CDF
    # Use logcdf for numerical stability, then exponentiate
    log_p_exceed = lognormal_logcdf(im_levels, theta, beta)
    p_exceed = np.exp(log_p_exceed)

    # Probability of non-exceedance (1-P)
    # Handle potential precision issues: p_exceed can be very close to 1
    p_non_exceed = 1.0 - p_exceed
    # Ensure probabilities are within [0, 1] and handle potential log(0)
    p_exceed = np.clip(p_exceed, 1e-12, 1.0 - 1e-12)
    p_non_exceed = np.clip(p_non_exceed, 1e-12, 1.0 - 1e-12)


    # Calculate Log-Likelihood using binomial probability formula components
    log_likelihood = np.sum(
        num_exceed * np.log(p_exceed) +
        (num_trials - num_exceed) * np.log(p_non_exceed)
    )

    # Check for NaN/Inf in likelihood (can happen with extreme inputs/params)
    if np.isnan(log_likelihood) or np.isinf(log_likelihood):
        return np.inf # Penalize invalid likelihood

    return -log_likelihood # Return negative for minimization

def fit_fragility_curve_MLE(im_levels, num_exceed, num_trials):
    """Fits a lognormal fragility curve using Maximum Likelihood Estimation (MLE).

    Args:
        im_levels (np.ndarray): Intensity measure levels.
        num_exceed (np.ndarray): Number of exceedances at each IM level.
        num_trials (np.ndarray): Total number of trials at each IM level.

    Returns:
        tuple: (theta, beta, success, result_object)
               theta (float): Fitted median.
               beta (float): Fitted logarithmic standard deviation.
               success (bool): True if optimization converged.
               result_object: The optimization result object from scipy.minimize.
    """
    # Initial guess for parameters (theta, beta)
    # Use simple heuristics: theta near middle IM where P is around 0.5, beta ~0.4-0.6?
    prob_exceed = num_exceed / num_trials
    try:
        # Find first IM where prob > 0.1 and last where prob < 0.9 for a rough median guess
        im_low = im_levels[prob_exceed > 0.1][0] if np.any(prob_exceed > 0.1) else np.min(im_levels)
        im_high = im_levels[prob_exceed < 0.9][-1] if np.any(prob_exceed < 0.9) else np.max(im_levels)
        initial_theta_guess = np.sqrt(im_low * im_high) # Geometric mean as guess
        if initial_theta_guess <= 0: initial_theta_guess = np.mean(im_levels) # Fallback
    except IndexError:
        initial_theta_guess = np.mean(im_levels) # Fallback if indexing fails
        
    initial_beta_guess = 0.6 # Common starting point
    initial_guess = [initial_theta_guess, initial_beta_guess]

    # Bounds for parameters (theta > 0, beta > 0)
    bounds = [(1e-6, None), (1e-6, None)] # Avoid zero

    # Minimize the negative log-likelihood
    with warnings.catch_warnings():
        # Suppress RuntimeWarnings during optimization (e.g., invalid value in log)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = minimize(
            neg_log_likelihood,
            initial_guess,
            args=(im_levels, num_exceed, num_trials),
            method='L-BFGS-B', # Supports bounds
            bounds=bounds
        )

    if result.success:
        theta_fit, beta_fit = result.x
        return theta_fit, beta_fit, True, result
    else:
        warnings.warn(f"MLE optimization failed: {result.message}", RuntimeWarning)
        # Try Nelder-Mead as a fallback? Sometimes more robust but slower & no bounds.
        # result = minimize(neg_log_likelihood, initial_guess, args=(im_levels, num_exceed, num_trials), method='Nelder-Mead')
        # if result.success:
        #     theta_fit, beta_fit = result.x
        #     # Ensure params are positive even if Nelder-Mead goes slightly negative
        #     theta_fit = max(theta_fit, 1e-6)
        #     beta_fit = max(beta_fit, 1e-6)
        #     warnings.warn(f"MLE optimization succeeded with fallback Nelder-Mead.", RuntimeWarning)
        #     return theta_fit, beta_fit, True, result
        # else:
        return np.nan, np.nan, False, result # Return NaN if fitting fails

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    # Example Data (replace with your actual data)
    im_test = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    trials_test = np.full_like(im_test, 20, dtype=int) # 20 trials per IM level
    # Simulate exceedances based on a known curve (theta=0.5, beta=0.4)
    true_theta = 0.5
    true_beta = 0.4
    np.random.seed(0) # for reproducibility
    prob_true = np.exp(lognormal_logcdf(im_test, true_theta, true_beta))
    exceed_test = np.random.binomial(trials_test, prob_true)

    print("Test Data:")
    print(f"IM Levels: {im_test}")
    print(f"Num Trials: {trials_test}")
    print(f"Num Exceed: {exceed_test}")
    print(f"True Params: theta={true_theta}, beta={true_beta}")

    # Fit the curve
    theta_mle, beta_mle, success_mle, res_obj = fit_fragility_curve_MLE(im_test, exceed_test, trials_test)

    if success_mle:
        print(f"\nMLE Fit Results:")
        print(f"  Theta (Median): {theta_mle:.4f}")
        print(f"  Beta (Log Std Dev): {beta_mle:.4f}")
        print(f"  Optimization Success: {success_mle}")
    else:
        print(f"\nMLE Fit Failed.")
        print(f"  Message: {res_obj.message}")

    # Optional: Plotting the results
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(8, 5))
        # Plot empirical rates
        empirical_rates = exceed_test / trials_test
        plt.plot(im_test, empirical_rates, 'bo', label='Empirical Rates')

        # Plot fitted curve
        if success_mle:
            im_smooth = np.linspace(min(im_test)*0.8, max(im_test)*1.2, 200)
            prob_fitted = np.exp(lognormal_logcdf(im_smooth, theta_mle, beta_mle))
            plt.plot(im_smooth, prob_fitted, 'r-', label=f'Fitted Curve ($\theta={theta_mle:.3f}, \beta={beta_mle:.3f}$)')
        
        # Plot true curve
        prob_true_smooth = np.exp(lognormal_logcdf(im_smooth, true_theta, true_beta))
        plt.plot(im_smooth, prob_true_smooth, 'g--', label=f'True Curve ($\theta={true_theta:.3f}, \beta={true_beta:.3f}$)')

        plt.xlabel("Intensity Measure (IM)")
        plt.ylabel("Probability of Exceedance")
        plt.title("Fragility Curve Fitting Example")
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 1)
        plt.xlim(0, max(im_test)*1.2)
        plt.show()
    except ImportError:
        print("\nInstall matplotlib to see the plot.") 