from matplotlib.animation import FuncAnimation
import numpy as np
from scipy.integrate import solve_ivp

m = 1  # mass
k = 1  # spring constant
g = 10 # gravity
eta = 8  # initial position of spring
v = 1 # velocity of spring
x0 = 8 # spring len

# coefficient of friction depends on velocity of block
def mu(u_):
    if u_ <= 0:
        return 0.3 # static friction
    else:
        return 0.1 # dynamic friction

# Define the system of ODEs.
def system(t, y):
    u, u_ = y
    f = k*(eta + v*t - x0 - u) # Spring force
    tau = mu(u_)*m*g # drag force
    if tau >= abs(f):
        u__ = 0
    elif f > 0:
        u__ = f - tau
    else:
        u__ = f + tau
    return (u_, u__)

# Initial conditions
u0 = 0  # Initial position
v0 = 0  # Initial velocity
y0 = (u0, v0)

# Time span
t_span = (0, 100)
t_eval = np.linspace(t_span[0], t_span[1], 1000)  # Points to evaluate the solution

# Solve the system
solution = solve_ivp(system, t_span, y0, t_eval=t_eval, method='RK45')

# Extract results
t = solution.t
u = solution.y[0]  # Position
u_ = solution.y[1]  # Velocity

# Plot results
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(16, 7), layout="constrained")

figs = fig.subfigures(nrows=2, ncols=1)

ax = figs[0].subplots()
ax.plot(t, u, label='$u$')
ax.plot(t, u_, label='$\dot{u}$')
ax.set_xlabel('$t$')
ax.legend()

tax = ax.twinx()
tax.plot(t, np.vectorize(mu)(u_), label='$\mu$', color="green")
tax.legend()


t_marker, = ax.plot([], [], "r-")

# Animation settings
ax = figs[1].subplots()
ax.set_xlim(-1, u.max() + 1)  # Horizontal axis (fixed range)
ax.set_ylim(-0.5, 0.5)  # Vertical axis (fixed range)
ax.set_xlabel("$u$")
ax.set_yticks([])

# Initialize spring as a sine wave
spring, = ax.plot([], [], lw=2, color='blue')
mass, = ax.plot([], [], "rs")
end, = ax.plot([], [], "ks")

# Number of coils in the spring
num_coils = 4

# Function to initialize the animation
def init():
    # spring.set_data([], [])
    return spring, mass, end, t_marker

N = 1000
y = 0.1 * np.sin(2*np.pi*num_coils*np.linspace(0, 1, N))

# Function to update the animation at each frame
def update(frame):
    # Spring stretch/compression based on position u(t)
    x_start = u[frame]
    x_end = eta + v*t[frame]
    x = np.linspace(x_start, x_end, N)
    spring.set_data(x, y)
    mass.set_data([x_start], [0])
    end.set_data([x_end], [0])
    t_marker.set_data([t[frame], t[frame]], [u.min(), u.max()])
    return spring, mass, end, t_marker

# Create the animation
ani = FuncAnimation(figs[1], update, frames=len(t), init_func=init, blit=True, interval=20)

# Display the animation
plt.show()