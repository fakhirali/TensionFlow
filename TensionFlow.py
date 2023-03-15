import numpy as np
import copy 
import warnings

#TODO:
#fix adding in numpy, since numpy broadcasts the data


class Neuron:
    def __init__(self, value):
        #value
        #local derivative
        self.value = value
        self.grad = None
        self._local_backwards = []
        self.children = []
        
        
    def __repr__(self):
        return str(f'{self.value} grad: {self.grad}')
    
    def __mul__(self, other_neuron):
        #if not a neuron then create a neuron
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        if isinstance(self.value, np.ndarray) and isinstance(other_neuron.value, np.ndarray):
            assert self.value.shape == other_neuron.value.shape, "Shapes must be same to perform element-wise multiplication"

        # self,other_neuron = self._handle_back_add(other_neuron)
        new_val = self.value * other_neuron.value
        new_neuron = Neuron(self.value * other_neuron.value)
        new_neuron.children = [self,other_neuron]

        t1= other_neuron.value
        t2= self.value
        new_neuron._local_backwards.append(lambda x: x*t1)
        new_neuron._local_backwards.append(lambda x: x*t2)
        return new_neuron

    def __matmul__(self,other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        new_neuron = Neuron(self.value @ other_neuron.value)
        new_neuron.children = [self, other_neuron]
        t1 = other_neuron.value.T
        t2 = self.value.T
        new_neuron._local_backwards.append(lambda x: x @ t1)
        new_neuron._local_backwards.append(lambda x: t2 @ x)
        return new_neuron
    
    # def __rmatmul__(self,other_neuron):
    #     #
    #     if not isinstance(other_neuron, Neuron):
    #         other_neuron = Neuron(other_neuron)
    #     new_neuron = Neuron(self.value @ other_neuron.value)
    #     new_neuron.children = [self, other_neuron]
    #     t1 = other_neuron.value.T
    #     t2 = self.value.T
    #     new_neuron._local_backwards.append(lambda x: x @ t1)
    #     new_neuron._local_backwards.append(lambda x: t2 @ x)
    #     return new_neuron

    def shape(self):
        return self.value.shape

    def __add__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        if isinstance(self.value, np.ndarray) and isinstance(other_neuron.value, np.ndarray):
            assert self.value.shape == other_neuron.value.shape, "Shapes must be same to perform element-wise addition"
        # self,other_neuron = self._handle_back_add(other_neuron)
        new_neuron = Neuron(self.value + other_neuron.value)
        new_neuron.children = [self,other_neuron]
        new_neuron._local_backwards.append(lambda x: x)
        new_neuron._local_backwards.append(lambda x: x)
        return new_neuron
    

    def sum(self, dim=-1):
        assert isinstance(self.value, np.ndarray), "Has to be a numpy array to sum"
        new_neuron = Neuron(self.value.sum(dim, keepdims=True))
        new_neuron.children = [self]
        t1 = self.value.shape
        new_neuron._local_backwards.append(lambda x: x * np.ones(t1))
        return new_neuron

    #setting right add and mul to mul and add
    __radd__ = __add__
    __rmul__ = __mul__
    
    def __neg__(self):
        # self,other_neuron = self._handle_back_add()
        minus_one = Neuron(-1)
        return self * minus_one
    
    def __sub__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self + (-other_neuron)
    
    def __rsub__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return other_neuron + -(self)
    
    def __truediv__(self,other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        
        return self * other_neuron.mul_inverse()
    
    def __rtruediv__(self,other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.mul_inverse() * other_neuron
    
    def __lt__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.value < other_neuron.value
    
    def __gt__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.value > other_neuron.value
    def __eq__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.value == other_neuron.value

    def __ge__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.value >= other_neuron.value

    def __le__(self, other_neuron):
        if not isinstance(other_neuron, Neuron):
            other_neuron = Neuron(other_neuron)
        return self.value <= other_neuron.value

    def __float__(self):
        return self.value

    def mul_inverse(self):
        # self,other_neuron = self._handle_back_add()
        new_neuron = Neuron(1/self.value)
        temp = -1/(self.value**2)
        # print(temp)
        new_neuron._local_backwards.append(lambda x: x * temp)
        new_neuron.children = [self]
        return new_neuron
    def reshape(self, new_shape):
        assert isinstance(self.value, np.ndarray)
        self.value = self.value.reshape(new_shape)
        return self
    
    def zero_grad(self):
        self.grad = None

    def log(self):
        new_val = np.log(self.value)
        if np.inf in new_val or -np.inf in new_val:
            warnings.warn("inf in log, replacing with zero")
            new_val[new_val==np.inf] = 0
            new_val[new_val==-np.inf] = 0
        new_neuron = Neuron(new_val)
        temp = 1/self.value
        new_neuron.children = [self]
        new_neuron._local_backwards.append(lambda x: x * temp)
        return new_neuron
         
        
    def exp(self):
        # self,other_neuron = self._handle_back_add()
        new_neuron = Neuron(np.exp(self.value))
        temp = np.exp(self.value)
        new_neuron._local_backwards.append(lambda x: x *temp)
        new_neuron.children = [self]
        return new_neuron
    def argmax(self,dim=None):
        return Neuron(self.value.argmax(axis=dim))        
    def backward(self):
        assert self.grad is None
        if isinstance(self.value, np.ndarray):
            self.grad = np.ones_like(self.value)
        else:
            self.grad = 1
        root = self
        stack = [root]
        while len(stack) != 0:
            root = stack.pop(0)
            for child, local_backwards in zip(root.children, root._local_backwards):
                # print(root, child)
                if not (child.grad is None): 
                    child.grad += local_backwards(root.grad)
                else:
                    child.grad = local_backwards(root.grad)
                stack.append(child)

    def backward_zero_grad(self):
            self.grad = None
            root = self
            stack = [root]
            while len(stack) != 0:
                root = stack.pop(0)
                for child, local_backwards in zip(root.children, root._local_backwards):
                    # print(root, child)
                    child.grad = None
                    stack.append(child)
 



    


