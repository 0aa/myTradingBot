import numpy as np
from scipy.optimize import minimize

import main
from main import *


# Define the function to be minimized
def rosen(x):
    return sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)


# Set the initial guess for the minimum value of x
x0 = np.array([5, 5, 5, 5, 14, 10, 5])
# res=minimize_params(x0)
# Call the minimize function
bounds = ((-100, 100), (-100, 100), (1, 10), (1, 10), (2, 30), (2, 30), (2, 30))
res = minimize(minimize_params, x0, method='Powell', bounds=bounds, options={'disp': True})

# Print the result
print(res)
