import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import threading
import queue
import time

# -----------------------------------
# Objective function (Himmelblau)
# -----------------------------------
def objective(x):
    return (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 - 7)**2

# -----------------------------------
# Thread-safe queue for plotting
# -----------------------------------
plot_queue = queue.Queue()

# -----------------------------------
# Worker function (one simplex)
# -----------------------------------
def run_simplex(start_point, simplex_id, color):
    path = []

    def callback(xk):
        path.append(xk.copy())
        plot_queue.put((simplex_id, np.array(path), color))

    minimize(
        objective,
        start_point,
        method="Nelder-Mead",
        callback=callback,
        options={
            "maxiter": 200,
            "xatol": 1e-6,
            "fatol": 1e-6,
            "disp": False
        }
    )

# -----------------------------------
# Generate one random point per quadrant
# -----------------------------------
def random_point(quadrant, scale=5):
    x = np.random.uniform(1, scale)
    y = np.random.uniform(1, scale)

    if quadrant == 1:
        return np.array([ x,  y])
    if quadrant == 2:
        return np.array([-x,  y])
    if quadrant == 3:
        return np.array([-x, -y])
    if quadrant == 4:
        return np.array([ x, -y])

# -----------------------------------
# Visualization setup
# -----------------------------------
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6))

x = np.linspace(-6, 6, 400)
y = np.linspace(-6, 6, 400)
X, Y = np.meshgrid(x, y)
Z = np.array([objective([xi, yi]) for xi, yi in zip(X.ravel(), Y.ravel())])
Z = Z.reshape(X.shape)

ax.contour(X, Y, Z, levels=50, cmap="viridis")
ax.set_title("Multi-Threaded Nelder–Mead (One Simplex per Quadrant)")
ax.set_xlabel("x")
ax.set_ylabel("y")

colors = ["red", "blue", "orange", "magenta"]
lines = {}

# -----------------------------------
# Start threads
# -----------------------------------
threads = []

for i in range(4):
    start = random_point(i + 1)
    line, = ax.plot([], [], "-", color=colors[i], lw=2, label=f"Simplex {i+1}")
    lines[i] = line

    t = threading.Thread(
        target=run_simplex,
        args=(start, i, colors[i]),
        daemon=True
    )
    threads.append(t)
    t.start()

ax.legend()

# -----------------------------------
# Main plotting loop (main thread only)
# -----------------------------------
while any(t.is_alive() for t in threads) or not plot_queue.empty():
    try:
        simplex_id, path, color = plot_queue.get(timeout=0.1)
        lines[simplex_id].set_data(path[:, 0], path[:, 1])
        plt.pause(0.01)
    except queue.Empty:
        pass

plt.ioff()
plt.show()
