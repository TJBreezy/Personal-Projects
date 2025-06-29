import numpy as np
from scipy.linalg import solve, eig
import warnings

def run_time_history(model_type: str,
                       M: np.ndarray,
                       K_or_Fy: np.ndarray, # K (linear) or Fy (nonlinear)
                       dt: float,
                       accel_gm_g: np.ndarray,
                       H: np.ndarray,
                       alpha_M: float, # Rayleigh damping coefficient for Mass
                       beta_K: float,  # Rayleigh damping coefficient for Initial Stiffness
                       K_init: np.ndarray | None = None, # Initial stiffness (required for nonlinear AND linear if passing beta_K)
                       alpha: float | None = None      # Post-yield stiffness ratio (required if nonlinear)
                       ) -> dict:
    """
    Performs time history analysis using the Newmark-Beta method with provided Rayleigh damping coefficients.

    Args:
        model_type (str): 'linear' or 'nonlinear'.
        M (np.ndarray): 3x3 Mass matrix (kg).
        K_or_Fy (np.ndarray): If 'linear', 3x3 Stiffness matrix K (N/m).
                              If 'nonlinear', 3x1 Yield force vector Fy (N).
        dt (float): Time step of the ground motion (seconds).
        accel_gm_g (np.ndarray): Ground acceleration column vector (units: g).
        H (np.ndarray): 3x1 Story height vector (m).
        alpha_M (float): Rayleigh damping coefficient proportional to mass (C = alpha_M*M + beta_K*K_initial).
        beta_K (float): Rayleigh damping coefficient proportional to initial stiffness (C = alpha_M*M + beta_K*K_initial).
        K_init (np.ndarray | None, optional): Initial stiffness matrix (N/m).
                                             Required if model_type='nonlinear'.
                                             Also needed for linear if beta_K != 0. Defaults to None.
        alpha (float | None, optional): Post-yield stiffness ratio.
                                        Required if model_type='nonlinear'. Defaults to None.

    Returns:
        dict: A dictionary containing results:
            'time' (np.ndarray): Time vector (seconds).
            'disp' (np.ndarray): Displacement time histories (m) (n_steps x DOF).
            'PIDR' (np.ndarray): Peak Interstory Drift Ratio per story (DOF x 1).
            'maxPIDR' (float): Maximum PIDR across all stories.
    """
    g = 9.81 # m/s^2

    # --- Input Validation & Setup ---
    if accel_gm_g.ndim > 1 and accel_gm_g.shape[1] != 1:
         if accel_gm_g.shape[0] == 1: accel_gm_g = accel_gm_g.T # Transpose row vector
         else: raise ValueError("accel_gm_g must be a column vector.")
    accel_gm_g = accel_gm_g.reshape(-1, 1)
    accel_gm = accel_gm_g * g # Convert g to m/s^2

    n_steps = len(accel_gm)
    num_dof = M.shape[0]
    if H.shape != (num_dof,): H = H.flatten() # Ensure H is 1D array

    if M.shape != (num_dof, num_dof): raise ValueError("M matrix shape mismatch.")

    time = np.arange(n_steps) * dt
    influence_vector = np.ones((num_dof, 1))

    # Initialize result arrays
    disp = np.zeros((n_steps, num_dof))
    vel = np.zeros((n_steps, num_dof))
    acc = np.zeros((n_steps, num_dof)) # Relative acceleration

    # Newmark-Beta parameters (Average Acceleration)
    gamma = 0.5
    beta = 0.25
    # Newmark constants for implicit formulation
    a0 = 1.0 / (beta * dt**2)
    a1 = 1.0 / (beta * dt)
    a2 = 1.0 / (2.0 * beta) - 1.0
    a3 = dt * (1.0 - gamma)
    a4 = dt * gamma
    a5 = dt / 2.0 * (1.0 - gamma / beta)
    a6 = dt * (1.0 - gamma / (2.0*beta)) # Used for explicit v/a calculation if needed? Check Chopra
    a7 = gamma / (beta * dt)
    a8 = 1.0 - gamma / beta
    a9 = dt * (1.0 - gamma / (2.0 * beta))

    # --- Initial Conditions ---
    # Assume u(0)=0, v(0)=0
    # M*a(0) + C*v(0) + Fs(u(0)) = -M*I*accel_gm(0)
    # Since Fs(0)=0, v(0)=0 => M*a(0) = -M*I*accel_gm(0) => a(0) = -I*accel_gm(0)
    acc[0, :] = -influence_vector.flatten() * accel_gm[0]

    # Transformation matrix: delta = T_mat @ u (Define before model type check)
    T_mat = np.zeros((num_dof, num_dof))
    for i in range(num_dof):
        T_mat[i, i] = 1.0
        if i > 0: T_mat[i, i-1] = -1.0

    # --- Model Specific Setup ---
    if model_type == 'linear':
        K = K_or_Fy
        if K.shape != (num_dof, num_dof): raise ValueError("K matrix shape mismatch for linear model.")
        # Use K itself as K_initial for linear damping calculation if K_init not explicitly provided
        if K_init is None:
             K_init_for_damping = K
             if beta_K != 0:
                 warnings.warn("K_init not provided for linear analysis with non-zero beta_K. Using K for damping calculation.", RuntimeWarning)
        else:
             K_init_for_damping = K_init
             if K_init.shape != (num_dof, num_dof): raise ValueError("Provided K_init matrix shape mismatch for linear model.")

        # Damping Matrix (using provided coefficients and appropriate K)
        C = alpha_M * M + beta_K * K_init_for_damping
        K_eff = K + a0 * M + a7 * C # Effective stiffness matrix
        K_eff_inv = None # Reset placeholder

    elif model_type == 'nonlinear':
        Fy = K_or_Fy.flatten() # Ensure Fy is 1D array
        if K_init is None or alpha is None:
            raise ValueError("K_init and alpha are required for nonlinear analysis.")
        if K_init.shape != (num_dof, num_dof): raise ValueError("K_init matrix shape mismatch.")
        if Fy.shape != (num_dof,): raise ValueError("Fy vector shape mismatch.")

        # Extract initial story stiffnesses from K_init
        k_init_stories = np.zeros(num_dof)
        try:
            # Assume standard shear building K_init structure to extract story stiffness
            k_init_stories[num_dof - 1] = K_init[num_dof - 1, num_dof - 1]
            for i in range(num_dof - 2, -1, -1):
                 # K_init[i, i] = k_i + k_{i+1} => k_i = K_init[i,i] - k_{i+1}
                 # Also check off-diagonal: K_init[i, i+1] == -k_{i+1}
                 if not np.isclose(K_init[i, i+1], -k_init_stories[i + 1]):
                     warnings.warn(f"Off-diagonal term K_init[{i},{i+1}] does not match -k_{i+1} from diagonal. K_init might not be standard shear building form.", RuntimeWarning)
                 k_init_stories[i] = K_init[i, i] - k_init_stories[i + 1]
        except IndexError:
             raise ValueError("Error extracting story stiffnesses from K_init. Is it 3x3?")

        if np.any(k_init_stories <= 0): raise ValueError("Derived initial story stiffnesses must be positive.")

        delta_y = Fy / k_init_stories # Yield displacements for each story

        # Damping Matrix (using provided coefficients and K_init)
        C = alpha_M * M + beta_K * K_init

        # Initialize nonlinear state variables per story
        story_force = np.zeros(num_dof) # Force in each story from previous converged step
        story_peak_pos_drift = np.zeros(num_dof) # Max positive drift reached
        story_peak_neg_drift = np.zeros(num_dof) # Min negative drift reached
        
        # Tolerances for Newton-Raphson
        tol_nr = 1e-5
        max_iter_nr = 50

    else:
        raise ValueError("model_type must be 'linear' or 'nonlinear'.")

    # --- Time Stepping Loop ---
    for j in range(n_steps - 1):
        # External force vector for step j+1
        P_ext = -M @ influence_vector * accel_gm[j+1] # Shape (3, 1)

        # Effective force P_hat from previous step properties (used in linear and NR initial guess)
        term_M = M @ (a0 * disp[j, :] + a1 * vel[j, :] + a2 * acc[j, :]) # Shape (3,)
        term_C = C @ (a7 * disp[j, :] + a8 * vel[j, :] + a9 * acc[j, :]) # Shape (3,)
        P_hat = P_ext.flatten() + term_M + term_C # Flatten P_ext to (3,)

        if model_type == 'linear':
            # --- Linear Step ---
            if K_eff_inv is None: # Calculate inverse/factorization only once
                 try:
                     K_eff_inv = np.linalg.inv(K_eff)
                 except np.linalg.LinAlgError:
                     raise RuntimeError("Effective stiffness matrix K_eff is singular.")
            
            # Solve for displacement at j+1
            disp[j+1, :] = K_eff_inv @ P_hat
            
            # Update velocity and acceleration using Newmark equations
            vel[j+1, :] = a7 * (disp[j+1, :] - disp[j, :]) - a8 * vel[j, :] - a9 * acc[j, :]
            acc[j+1, :] = a0 * (disp[j+1, :] - disp[j, :]) - a1 * vel[j, :] - a2 * acc[j, :]

        elif model_type == 'nonlinear':
            # --- Nonlinear Step (Newton-Raphson) ---
            # Initial guess for iteration (k=0)
            u_k = disp[j, :] # Guess for u[j+1]
            
            iter_nr = 0
            converged_nr = False
            
            while iter_nr < max_iter_nr and not converged_nr:
                 iter_nr += 1
                 
                 # Calculate interstory drifts for current guess u_k
                 delta_k = T_mat @ u_k
                 
                 # Interstory drift from previous *converged* step j
                 delta_prev = T_mat @ disp[j, :]

                 # Calculate tangent stiffness and restoring force for each story using hysteresis
                 kt_stories = np.zeros(num_dof)
                 fs_stories = np.zeros(num_dof)
                 
                 for story_i in range(num_dof):
                     ki = k_init_stories[story_i]
                     dy = delta_y[story_i]
                     fy = Fy[story_i]
                     ai = alpha
                     k_post = ai * ki
                     dk = delta_k[story_i]       # Current iteration drift guess
                     dk_prev = delta_prev[story_i] # Previous converged step drift
                     fs_prev = story_force[story_i]  # Previous converged step force
                     d_max = story_peak_pos_drift[story_i]
                     d_min = story_peak_neg_drift[story_i]

                     # --- Hysteresis Logic ---
                     # 1. Determine Tangent Stiffness (kt) based on loading path
                     if dk > d_max or dk < d_min:  # Loading on backbone beyond previous peaks
                         kt = k_post
                     else: # Unloading or reloading within bounds [d_min, d_max]
                         kt = ki

                     # 2. Determine Force (fs) based on path
                     # Potential force assuming current stiffness applies from prev step
                     fs_trial = fs_prev + kt * (dk - dk_prev)

                     # Calculate backbone force at current drift dk
                     if abs(dk) <= dy:
                         f_backbone = ki * dk
                     elif dk > dy:
                         f_backbone = fy + k_post * (dk - dy)
                     else: # dk < -dy
                         f_backbone = -fy + k_post * (dk + dy)

                     # Apply constraints / Select force
                     if kt == k_post: # Must be on the backbone
                         fs = f_backbone
                     else: # Unloading/reloading (kt = ki), ensure doesn't exceed backbone
                         if dk > dk_prev: # Loading positively
                              fs = min(fs_trial, f_backbone)
                         elif dk < dk_prev: # Loading negatively
                              fs = max(fs_trial, f_backbone)
                         else: # No change in drift
                              fs = fs_prev # Or fs_trial, should be same

                     fs_stories[story_i] = fs
                     kt_stories[story_i] = kt
                     # --- End Hysteresis Logic ---

                 # Assemble global tangent stiffness K_T
                 K_T = np.zeros((num_dof, num_dof))
                 K_T[num_dof-1, num_dof-1] = kt_stories[num_dof-1]
                 for i in range(num_dof - 2, -1, -1):
                     K_T[i, i] = kt_stories[i] + kt_stories[i+1]
                     K_T[i, i+1] = -kt_stories[i+1]
                     K_T[i+1, i] = -kt_stories[i+1]
                     
                 # Assemble global restoring force Fs
                 Fs_k = T_mat.T @ fs_stories # Fs = T^T * fs_story
                 
                 # Calculate corresponding velocity and acceleration for u_k using Newmark
                 # These are needed if residual is defined based on EoM at j+1
                 v_k = a7 * (u_k - disp[j,:]) - a8 * vel[j,:] - a9 * acc[j,:]
                 a_k = a0 * (u_k - disp[j,:]) - a1 * vel[j,:] - a2 * acc[j,:]
                 
                 # Calculate Residual Force Vector
                 # R = P_ext - Fs_k - C @ v_k - M @ a_k
                 Residual = P_ext.flatten() - Fs_k - C @ v_k - M @ a_k # Flatten P_ext

                 # Check for NaN/Inf in Residual before checking norm
                 if np.isnan(Residual).any() or np.isinf(Residual).any():
                     warnings.warn(f"NaN or Inf detected in Residual at step {j+1}, iter {iter_nr}. Aborting NR.", RuntimeWarning)
                     converged_nr = False # Mark as not converged
                     break # Exit NR loop immediately

                 # Check convergence
                 residual_norm = np.linalg.norm(Residual)
                 if residual_norm < tol_nr:
                     converged_nr = True
                     disp[j+1, :] = u_k
                     vel[j+1, :] = v_k
                     acc[j+1, :] = a_k

                     # --- Update State Variables upon Convergence ---
                     final_delta = T_mat @ disp[j+1, :] # Final drifts for step j+1
                     story_force = fs_stories # Store converged forces for next step
                     for story_i in range(num_dof):
                         story_peak_pos_drift[story_i] = max(story_peak_pos_drift[story_i], final_delta[story_i])
                         story_peak_neg_drift[story_i] = min(story_peak_neg_drift[story_i], final_delta[story_i])
                     # --- End State Update ---
                     break # Exit NR loop
                     
                 # Calculate Effective Tangent Stiffness
                 K_eff_T = K_T + a0 * M + a7 * C
                 
                 # Solve for correction
                 try:
                     # Check if K_eff_T contains NaN/Inf before solving
                     if np.isnan(K_eff_T).any() or np.isinf(K_eff_T).any():
                         warnings.warn(f"NaN or Inf detected in K_eff_T at step {j+1}, iter {iter_nr}. Aborting NR.", RuntimeWarning)
                         converged_nr = False
                         break # Exit NR loop
                         
                     delta_u = solve(K_eff_T, Residual, assume_a='sym') # Assume symmetric
                     
                     # Check for NaN/Inf in correction
                     if np.isnan(delta_u).any() or np.isinf(delta_u).any():
                         warnings.warn(f"NaN or Inf detected in delta_u at step {j+1}, iter {iter_nr}. Aborting NR.", RuntimeWarning)
                         converged_nr = False
                         break # Exit NR loop
                         
                 except np.linalg.LinAlgError:
                     print(f"Warning: K_eff_T singular at step {j+1}, iter {iter_nr}. Using pseudo-inverse.")

                 # Update displacement guess
                 u_k = u_k + delta_u
                 
            # End of Newton-Raphson loop
            if not converged_nr:
                 warnings.warn(f"Newton-Raphson failed to converge at time step {j+1} (t={time[j+1]:.3f}s). Results may be inaccurate.", RuntimeWarning)
                 # Use the last iteration's results? Or stop? Let's use last results for now.
                 # Using last calculated u_k, v_k, a_k from the final iteration attempt
                 disp[j+1, :] = u_k
                 vel[j+1, :] = a7 * (u_k - disp[j,:]) - a8 * vel[j,:] - a9 * acc[j,:]
                 acc[j+1, :] = a0 * (u_k - disp[j,:]) - a1 * vel[j,:] - a2 * acc[j,:]

                 # Calculate story forces based on the non-converged displacement u_k
                 # Use the same hysteresis logic with the final u_k to get consistent forces
                 final_delta_nonconv = T_mat @ u_k
                 fs_stories_nonconv = np.zeros(num_dof)
                 delta_prev = T_mat @ disp[j, :] # Previous converged step drift
                 for story_i in range(num_dof):
                     # Simplified recalculation for non-converged step: Use backbone directly?
                     # Or apply the same hysteresis logic as above? Let's use hysteresis for consistency
                     ki = k_init_stories[story_i]; dy = delta_y[story_i]; fy = Fy[story_i]; ai = alpha; k_post = ai * ki
                     dk = final_delta_nonconv[story_i]; dk_prev = delta_prev[story_i]; fs_prev = story_force[story_i]
                     d_max = story_peak_pos_drift[story_i]; d_min = story_peak_neg_drift[story_i]

                     if dk > d_max or dk < d_min: kt = k_post
                     else: kt = ki

                     fs_trial = fs_prev + kt * (dk - dk_prev)

                     if abs(dk) <= dy: f_backbone = ki * dk
                     elif dk > dy: f_backbone = fy + k_post * (dk - dy)
                     else: f_backbone = -fy + k_post * (dk + dy)

                     if kt == k_post: fs = f_backbone
                     else:
                         if dk > dk_prev: fs = min(fs_trial, f_backbone)
                         elif dk < dk_prev: fs = max(fs_trial, f_backbone)
                         else: fs = fs_prev
                     fs_stories_nonconv[story_i] = fs

                 story_force = fs_stories_nonconv # Store these forces for next step
                 # Update peak drifts based on this non-converged step's displacement
                 for story_i in range(num_dof):
                     story_peak_pos_drift[story_i] = max(story_peak_pos_drift[story_i], final_delta_nonconv[story_i])
                     story_peak_neg_drift[story_i] = min(story_peak_neg_drift[story_i], final_delta_nonconv[story_i])

    # --- Post-Processing: Calculate PIDR ---
    # Calculate all interstory drifts
    with warnings.catch_warnings(): # Suppress potential warnings from NaN comparisons if analysis failed
        warnings.simplefilter("ignore", category=RuntimeWarning)
        interstory_drifts = disp @ T_mat.T # disp is N x Dof, T_mat is Dof x Dof => drifts N x Dof

        # Find peak absolute drift for each story, ignoring NaNs
        try:
            peak_abs_interstory_drifts = np.nanmax(np.abs(interstory_drifts), axis=0)
        except ValueError: # Handle case where all drifts might be NaN
             peak_abs_interstory_drifts = np.full(num_dof, np.nan)

        # Calculate PIDR, handle division by zero or NaN/Inf heights (unlikely but safe)
        H_safe = np.where(np.abs(H) > 1e-9, H, np.nan) # Avoid division by zero/small H
        PIDR_stories = peak_abs_interstory_drifts / H_safe

        # Find overall maximum PIDR, ignoring NaNs
        try:
            maxPIDR = np.nanmax(PIDR_stories)
        except ValueError: # Handle case where all PIDRs are NaN
            maxPIDR = np.nan

    # --- Assemble Results ---
    results = {
        'time': time,
        'disp': disp,       # meters
        'PIDR': PIDR_stories, # dimensionless
        'maxPIDR': maxPIDR    # dimensionless
        # Optional: return velocity, acceleration, story forces etc.
        # 'vel': vel,
        # 'acc': acc,
    }

    return results

# Example Usage (Optional)
# if __name__ == '__main__':
#     from ..02_StructuralModels.define_linear_3dof import define_linear_3dof
#     from ..02_StructuralModels.define_nonlinear_3dof import define_nonlinear_3dof
#
#     # 1. Define Models
#     try:
#         M_l, K_l, T1_l, H_l = define_linear_3dof(target_T1=0.6)
#         M_nl, K_init_nl, Fy_nl, alpha_nl, H_nl = define_nonlinear_3dof(M_l, K_l, H_l, yield_drift_ratio=0.005, alpha_post_yield=0.05)
#     except Exception as e:
#         print(f"Error defining models: {e}")
#         exit()
#
#     # 2. Create Sample Ground Motion (e.g., sine wave in g)
#     dt_gm = 0.01
#     sim_time = 10.0
#     time_gm = np.arange(0, sim_time, dt_gm)
#     freq_gm = 1.0 / T1_l # Excite near resonance
#     accel_input_g = 0.5 * np.sin(2 * np.pi * freq_gm * time_gm)
#     accel_input_g = accel_input_g.reshape(-1, 1)
#
#     print(f"\n--- Running Linear Analysis ---")
#     try:
#         results_lin = run_time_history(
#             model_type='linear',
#             M=M_l,
#             K_or_Fy=K_l,
#             dt=dt_gm,
#             accel_gm_g=accel_input_g,
#             H=H_l,
#             alpha_M=0.05, # Pass coeffs
#             beta_K=0.05,  # Pass coeffs
#             K_init=K_l # Pass K_l as K_init for damping calc
#         )
#         print(f"Linear Analysis Max PIDR: {results_lin['maxPIDR']:.6f}")
#         print(f"Linear Story PIDRs: {results_lin['PIDR']}")
#     except Exception as e:
#         print(f"Linear analysis failed: {e}")
#
#
#     print(f"\n--- Running Nonlinear Analysis ---")
#     try:
#         results_nl = run_time_history(
#             model_type='nonlinear',
#             M=M_nl,
#             K_or_Fy=Fy_nl, # Pass Fy vector
#             dt=dt_gm,
#             accel_gm_g=accel_input_g,
#             H=H_nl,
#             alpha_M=0.05, # Pass coeffs
#             beta_K=0.05,  # Pass coeffs
#             K_init=K_init_nl, # Pass K_init
#             alpha=alpha_nl      # Pass alpha
#         )
#         print(f"Nonlinear Analysis Max PIDR: {results_nl['maxPIDR']:.6f}")
#         print(f"Nonlinear Story PIDRs: {results_nl['PIDR']}")
#     except Exception as e:
#         print(f"Nonlinear analysis failed: {e}")
#
#     # Plotting (optional)
#     import matplotlib.pyplot as plt
#     plt.figure(figsize=(10, 6))
#
#     plt.subplot(2, 1, 1)
#     plt.plot(results_lin['time'], results_lin['disp'][:, -1], label=f'Linear Top Floor Disp (Max PIDR={results_lin["maxPIDR"]:.4f})')
#     if 'results_nl' in locals():
#          plt.plot(results_nl['time'], results_nl['disp'][:, -1], '--', label=f'Nonlinear Top Floor Disp (Max PIDR={results_nl["maxPIDR"]:.4f})')
#     plt.ylabel('Displacement (m)')
#     plt.title('Top Floor Displacement Comparison')
#     plt.legend()
#     plt.grid(True)
#
#     plt.subplot(2, 1, 2)
#     plt.plot(results_lin['time'], accel_input_g, label='Ground Motion (g)', color='gray')
#     plt.ylabel('Accel (g)')
#     plt.xlabel('Time (s)')
#     plt.legend()
#     plt.grid(True)
#
#     plt.tight_layout()
#     plt.show()
#
