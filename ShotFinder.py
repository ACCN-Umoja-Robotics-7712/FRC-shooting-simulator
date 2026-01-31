import numpy as np
from scipy.optimize import least_squares

g = 9.81

def meters_to_inches(m):
    return m * 39.37

def trajectory_residual(x, d, hs, ht):
    """
    x = [theta (rad), v (m/s)]
    """
    theta, v = x

    # Prevent invalid cos(theta)
    if np.cos(theta) <= 0:
        return [1e6]

    y = hs + d * np.tan(theta) - (g * d**2) / (2 * v**2 * np.cos(theta)**2)
    return [y - ht]


def descent_angle(theta, v, d):
    """
    Angle of velocity vector at target (rad).
    Must be negative for descending shots.
    """
    vx = v * np.cos(theta)
    t = d / vx
    vy = v * np.sin(theta) - g * t
    return np.arctan2(vy, vx)


def find_shot_solutions(
    hs,
    ht,
    d,
    v_max=20.0,
    theta_min_deg=45,
    theta_max_deg=80,
    descent_angle_max_deg=-5,
    min_angle_separation_deg=3,
):
    theta_min = np.deg2rad(theta_min_deg)
    theta_max = np.deg2rad(theta_max_deg)
    descent_angle_max = np.deg2rad(descent_angle_max_deg)
    min_sep = np.deg2rad(min_angle_separation_deg)

    solutions = []

    # Multi-start grid
    theta_guesses = np.linspace(theta_min, theta_max, 12)
    v_guesses = np.linspace(2.0, v_max, 12)

    for th0 in theta_guesses:
        for v0 in v_guesses:
            res = least_squares(
                trajectory_residual,
                x0=[th0, v0],
                bounds=(
                    [theta_min, 0.1],
                    [theta_max, v_max],
                ),
                args=(d, hs, ht),
                ftol=1e-10,
                xtol=1e-10,
            )

            if not res.success:
                continue

            theta, v = res.x

            # Descent angle constraint
            da = descent_angle(theta, v, d)
            if da > descent_angle_max:
                continue

            # Deduplicate solutions
            if any(abs(theta - s[0]) < min_sep for s in solutions):
                continue
            if theta < theta_min or theta > theta_max:
                continue    
            else:
                solutions.append((theta, v))

    return solutions

if __name__ == "__main__":
    hs = 0.56  # shooter height (m)
    ht = 1.83  # hoop height (m)
    d = 6.5    # distance (m)

    sols = find_shot_solutions(
        hs, ht, d,
        v_max=18.0,
        descent_angle_max_deg=-8,
        min_angle_separation_deg=4
    )

    print("Valid shooting solutions:")
    for theta, v in sols:
        print(f"Pitch: {np.rad2deg(theta):.2f} deg | Speed: {meters_to_inches(v):.2f} in/s")
