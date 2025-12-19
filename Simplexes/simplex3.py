import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import threading
import queue

from mpl_toolkits.mplot3d import Axes3D  # noqa

# -----------------------------------
# Objective function (terrain)
# -----------------------------------
def objective(x):
    return (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 - 7)**2

# -----------------------------------
# Thread-safe plot queue
# -----------------------------------
plot_queue = queue.Queue()

# -----------------------------------
# Simplex worker
# -----------------------------------
def run_simplex(start_point, simplex_id):
    path = []

    def callback(xk):
        z = objective(xk)
        path.append([xk[0], xk[1], z])
        plot_queue.put((simplex_id, np.array(path)))

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
# Random start per quadrant
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
# 3D Visualization setup
# -----------------------------------
plt.ion()
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# Terrain mesh
x = np.linspace(-6, 6, 200)
y = np.linspace(-6, 6, 200)
X, Y = np.meshgrid(x, y)
Z = np.array([objective([xi, yi]) for xi, yi in zip(X.ravel(), Y.ravel())])
Z = Z.reshape(X.shape)

# Surface plot
ax.plot_surface(
    X, Y, Z,
    cmap="terrain",
    alpha=0.7,
    linewidth=0,
    antialiased=True
)

ax.set_title("3D Multi-Simplex Optimization (Geographic View)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Objective Value")

# -----------------------------------
# Start simplex threads
# -----------------------------------
colors = ["red", "blue", "orange", "magenta"]
lines = {}
threads = []

for i in range(4):
    start = random_point(i + 1)
    line, = ax.plot([], [], [], color=colors[i], lw=3, label=f"Simplex {i+1}")
    lines[i] = line

    t = threading.Thread(
        target=run_simplex,
        args=(start, i),
        daemon=True
    )
    threads.append(t)
    t.start()

ax.legend()

# -----------------------------------
# Main plotting loop
# -----------------------------------
while any(t.is_alive() for t in threads) or not plot_queue.empty():
    try:
        simplex_id, path = plot_queue.get(timeout=0.1)
        lines[simplex_id].set_data(path[:, 0], path[:, 1])
        lines[simplex_id].set_3d_properties(path[:, 2])
        plt.pause(0.01)
    except queue.Empty:
        pass

plt.ioff()
plt.show()
