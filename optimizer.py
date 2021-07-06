import numpy as np
from scipy.optimize import LinearConstraint
from scipy.optimize import minimize
from numpy import linalg

class Optimizer():

    np_array = None

    def __init__(self):
        self.np_array = None
    
    def obj_func(self, x):
        '''
            Objective function is the L2 Norm of Ax
        '''
        v = []
        for i in range(self.np_array.shape[0]):
            v.append(self.np_array[i] * x)
        return linalg.norm(v, 2)
    
    def opt(self, np_array):
        '''
            Return vector x such that Ax has the minimum L2 norm under the constraint
                that the L1 norm of x is 1
            Params: np_array (matrix A)
            Return: numpy array x of coefficients
        '''
        self.np_array = np_array
        row, col = self.np_array.shape
        linear_constraint = LinearConstraint([[1]*col], [1], [1])
        x0 = np.array([1/col]*col)
        result = minimize(self.obj_func, x0, constraints=linear_constraint)
        return result['x']