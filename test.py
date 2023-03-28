import numpy as np

a = np.empty((0,1,4))
print(a.shape)
t = np.array([[1,2,3,4]])
t= np.reshape(t,(1,1,4))

a= np.append(a,t,0)
a= np.append(a,t,0)
print(a.shape)
print(a)