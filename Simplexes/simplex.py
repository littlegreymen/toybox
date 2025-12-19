import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ---------------------------
# Objective function (2D)
# Change this function as needed
# ---------------------------
def objective(x):
    # Example: Himmelblau function (multiple minima)
    return (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 - 7)**2

# To MAXIMIZE instead, use:
# def objective(x):
#     return -((x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 - 7)**2)

# ---------------------------
# Visualization setup
# ---------------------------
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6))

# Create contour plot
x = np.linspace(-6, 6, 400)
y = np.linspace(-6, 6, 400)
X, Y = np.meshgrid(x, y)
Z = np.array([objective([xi, yi]) for xi, yi in zip(X.ravel(), Y.ravel())])
Z = Z.reshape(X.shape)

ax.contour(X, Y, Z, levels=50, cmap="viridis")
simplex_plot, = ax.plot([], [], "ro-", lw=2)
best_point, = ax.plot([], [], "bx", markersize=10)

ax.set_title("Real-Time Nelder–Mead Simplex Optimization")
ax.set_xlabel("x")
ax.set_ylabel("y")

# ---------------------------
# Storage for simplex history
# ---------------------------
simplex_history = []

def callback(xk):
    simplex_history.append(xk.copy())
    update_plot()

def update_plot():
    if len(simplex_history) < 3:
        return

    # Nelder–Mead simplex approximation
    simplex = np.array(simplex_history[-3:])
    simplex = np.vstack([simplex, simplex[0]])

    simplex_plot.set_data(simplex[:, 0], simplex[:, 1])
    best_point.set_data(simplex[-1, 0], simplex[-1, 1])

    plt.pause(0.5)

# ---------------------------
# Initial guess
# ---------------------------
x0 = np.array([4.0, 4.0])

# ---------------------------
# Run optimizer
# ---------------------------
result = minimize(
    objective,
    x0,
    method="Nelder-Mead",
    callback=callback,
    options={
        "maxiter": 200,
        "xatol": 1e-6,
        "fatol": 1e-6,
        "disp": True
    }
)

plt.ioff()
plt.show()

print("\nOptimization Result:")
print(result)
