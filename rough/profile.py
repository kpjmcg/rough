# AUTOGENERATED! DO NOT EDIT! File to edit: ..\01_profile.ipynb.

# %% auto 0
__all__ = ['Ra', 'Rms']

# %% ..\01_profile.ipynb 4
import numpy as np
from PIL import Image  

# %% ..\01_profile.ipynb 9
def Ra(im, axis = 0, norm = True):
    '''
    Calculates Mean Absolute Roughness (Ra) along given axis. Calculated as the average deviation of absolute height values from the mean line of a given profile.
    '''
    if norm:
        im = im - np.mean(im, axis = axis)
    return np.mean(np.absolute(im))

# %% ..\01_profile.ipynb 11
def Rms(im, axis = 0, norm = True):
    '''
    Calculates Root Mean Square Roughness (Rms) along given axis. Calculated as the root mean square of deviations of height from the mean line of a given profile. 
    '''
    if norm:
        im = im - np.mean(im, axis = axis)
    return np.sqrt(np.mean(np.square(im), axis = axis))