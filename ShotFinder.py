import numpy as np
from scipy.optimize import least_squares

g = 9.81

def trajectory_residual(x, d, hs, ht):
    theta, v = x
    if np.cos(theta) <= 0:
        return [1e6]
    y = hs + d * np.tan(theta) - (g * d**2) / (2 * v**2 * np.cos(theta)**2)
    return [y - ht]

def descent_angle(theta, v, d):
    vx = v * np.cos(theta)
    t = d / vx
    vy = v * np.sin(theta) - g * t
    return np.arctan2(vy, vx)

def flight_time(theta, v, d):
    vx = v * np.cos(theta)
    return d / vx

def entry_angle(theta, v, d):
    return -np.rad2deg(descent_angle(theta, v, d))

def margin_of_error(theta, v, d, hs, ht, hub_radius=0.3):
    y_at_hub = hs + d * np.tan(theta) - (g * d**2) / (2 * v**2 * np.cos(theta)**2)
    height_above_rim = y_at_hub - ht
    if height_above_rim <= 0:
        return 0.0
    return hub_radius * (height_above_rim / ht)

def find_ideal_shot(
    hs=0.5,          # Robot shooter height (m)
    ht=2.5,          # HUB target height (m)
    d=5.0,           # Horizontal distance to HUB (m)
    v_max=25.0,      # Maximum achievable launch speed (m/s)
    theta_min_deg=30,
    theta_max_deg=80,
    descent_angle_max_deg=-10,
    min_angle_separation_deg=2,
    hub_radius=0.3,
    criterion="balanced",
    return_type="theta"  # Changed from 'res' to avoid conflict
):
    theta_min = np.deg2rad(theta_min_deg)
    theta_max = np.deg2rad(theta_max_deg)
    descent_angle_max = np.deg2rad(descent_angle_max_deg)
    min_sep = np.deg2rad(min_angle_separation_deg)

    solutions = []
    theta_guesses = np.linspace(theta_min, theta_max, 10)
    v_guesses = np.linspace(2.0, v_max, 10)

    for th0 in theta_guesses:
        for v0 in v_guesses:
            # Use a different variable name to avoid conflict
            optimization_result = least_squares(
                trajectory_residual,
                x0=[th0, v0],
                bounds=([theta_min, 0.1], [theta_max, v_max]),
                args=(d, hs, ht),
                ftol=1e-10,
                xtol=1e-10,
            )
            if not optimization_result.success:
                continue

            theta, v = optimization_result.x
            da = descent_angle(theta, v, d)
            if da > descent_angle_max:
                continue

            entry = entry_angle(theta, v, d)
            time = flight_time(theta, v, d)
            margin = margin_of_error(theta, v, d, hs, ht, hub_radius)

            if any(abs(theta - s['theta']) < min_sep for s in solutions):
                continue
            if theta < theta_min or theta > theta_max:
                continue

            solutions.append({
                'theta': theta,
                'v': v,
                'descent_angle': da,
                'entry_angle': entry,
                'flight_time': time,
                'margin': margin
            })

    if not solutions:
        return None

    # Select the best shot based on the chosen criterion
    if criterion == "minimum_speed":
        best = min(solutions, key=lambda x: x['v'])
    elif criterion == "steep_entry":
        best = max(solutions, key=lambda x: x['entry_angle'])
    elif criterion == "max_margin":
        best = max(solutions, key=lambda x: x['margin'])
    elif criterion == "fastest":
        best = min(solutions, key=lambda x: x['flight_time'])
    elif criterion == "balanced":
        speeds = [s['v'] for s in solutions]
        entries = [s['entry_angle'] for s in solutions]
        norm_speeds = [(max(speeds) - s) / (max(speeds) - min(speeds)) for s in speeds]
        norm_entries = [(e - min(entries)) / (max(entries) - min(entries)) for e in entries]
        scores = [0.4 * ns + 0.6 * ne for ns, ne in zip(norm_speeds, norm_entries)]
        best = solutions[np.argmax(scores)]
    else:
        raise ValueError(f"Unknown criterion: {criterion}")

    if return_type == "theta":
        return np.rad2deg(best['theta'])  # Return in degrees
    elif return_type == "v":
        return best['v']
    elif return_type == "all":
        return best
    else:
        raise ValueError(f"Unknown return_type: {return_type}")