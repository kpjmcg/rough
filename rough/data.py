# AUTOGENERATED! DO NOT EDIT! File to edit: ..\00_data.ipynb.

# %% auto 0
__all__ = ['gen_rot_prof']

# %% ..\00_data.ipynb 4
import numpy as np
import imutils
import cv2 as cv
from matplotlib import pyplot as plt

# %% ..\00_data.ipynb 12
def gen_rot_prof(array, #2D array of height values
                     deg = 180, #Number of degrees to rotate through, i.e 180 gives full 360 rotation
                     increment = 1 # indent/180 = number of evenly spaced profiles to calculate.  
                    ):
    ''' Generates an array of rotational profiles through to deg, in even increments of increment. 
    Uses OpenCV and Imutils to rotate the array around the center of the array/raster/image, extracts the middle row. 
    '''
    if deg % increment != 0:
        raise ValueError('Cannot sample evenly, deg % indent must = 0')
    profiles = np.zeros(shape = (deg//increment,array.shape[0]))
    index = 0
    center = array.shape[0]//2  #Center is returned as index to the right of center for even arrays
    for degree in range(0, deg, increment):
        rot_array = imutils.rotate(array, angle = degree)
        profiles[index, :] = rot_array[center,:]
        index += 1
    return profiles
            
