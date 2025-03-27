# Replication of some of the modeling in Lipovsky, B. P., & Dunham, E. M. (2016). Tremor during ice-stream stick slip. The Cryosphere, 10(1), 385–399. https://doi.org/10.5194/tc-10-385-2016.

from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt

mu0 = 0.4
a = 5e-3
b = 15e-3
V0 = 1e-5 # m/s
sigma_eff = 25e3 # Pa
rho_i = 916 # kg/m^3
c_i = 2000 # m/s
rho_b = 1700 # kg/m^3
c_b = 95 # m/s
z_i = rho_i*c_i
z_b = rho_b*c_b
eta = 1/(1/z_i + 1/z_b)
R = 1.8 # m
G_b = 20e6 # Pa
G_star = 3.5*G_b
k = G_star/R # Typo in paper?
Vs = 7.47e-4 # m/s, max GPS velocity
L = 1.4e-6 # m

def ode(t, y):
    [tau, V] = y
    mu_ss = mu0 - (b - a)*np.log(V/V0)
    dVdt = 1/(a*sigma_eff/V + eta)*(V/L*(tau - mu_ss*sigma_eff) - k*(V - Vs))
    dtaudt = -k*(V - Vs) - eta*dVdt
    return [dtaudt, dVdt]

# Initial conditions
t_span = (0, 10)
V_initial = V0
tau_initial = 0

# Solve IVP
solution = solve_ivp(ode, t_span, [tau_initial, V_initial], method='RK45')

# Plotting:
fig, axs = plt.subplots(2, 1, sharex=True, figsize=(8, 6), layout="constrained")

# Plot tau (solution.y[0])
axs[0].plot(solution.t, solution.y[0], label='τ (tau)')
axs[0].set_ylabel('τ (tau)')
axs[0].legend()
axs[0].grid()

# Plot V (solution.y[1])
axs[1].plot(solution.t, solution.y[1], label='V', color='orange')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('V')
axs[1].legend()
axs[1].grid()

plt.show()