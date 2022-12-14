# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_profile.ipynb.

# %% auto 0
__all__ = ['Ra', 'Rms', 'Rsk', 'Rku', 'Rp', 'Rv', 'Rz']

# %% ../01_profile.ipynb 4
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import skew, kurtosis, moment
from scipy.signal import find_peaks
import math

from .data import *


# %% ../01_profile.ipynb 9
def Ra(im, #Numpy array or arraylike
       axis = 1, #Default to Ra of rows
       norm = True #Normalize the profile by subtracting the mean 
      ):
    '''
    Calculates Mean Absolute Roughness (Ra) along given axis. Defined as the average deviation of absolute height values from the mean line.
    '''
    if norm:
        im = im - np.mean(im, axis = axis, keepdims = True)
    return np.mean(np.absolute(im), axis = axis)

# %% ../01_profile.ipynb 13
def Rms(im, #Numpy array or array like
        axis = 1, #Default to Rms of rows
        norm = True #Normalize the profile by subtracting the mean
       ):
    '''
    Calculates Root Mean Square Roughness (Rms) along given axis. Defined as the root mean square of deviations of height from the mean line of a given profile. 
    '''
    if norm:
        im = im - np.mean(im, axis = axis, keepdims = True)
    return np.sqrt(np.mean(np.square(im), axis = axis))

# %% ../01_profile.ipynb 15
def Rsk(im, #Numpy array or array like
         axis = 1, #Default to Skew of rows
         norm = True, #Normalize the profile by subtracting the mean
        **kwargs #Keyword arguments to modify the skew function
       ):
    '''
    Calcultes the Skew (Rsk) along given axis. Thin wrapper around scipy.stats.skew with bias set to False
    '''
    if norm:
        im = im - np.mean(im, axis=axis, keepdims=True)
    return skew(a = im, axis=axis, **kwargs)

# %% ../01_profile.ipynb 17
def Rku(im, #Numpy array or array like
       axis = 1, #Default to Kurtosis of rows
       norm= True, #Normalize the profile by subtracting the mean
        **kwargs #Keyword arguments to modify the kurtosis function
       ):
    '''
    Calculates the Kurtosis (Rku) along given axis. This wrapper around scipy.stats.kurtosis 
    '''
    if norm:
        im = im - np.mean(im,axis=axis, keepdims=True)
    return kurtosis(a = im, axis = axis, **kwargs)

# %% ../01_profile.ipynb 19
def Rp(im, #Numpy array or array like
       axis = 1, # Default to peaks of rows
       norm = True, #Normalize the profile by subtracting the mean
       **kwargs #Keyword arguments to modify the numpy.amax function
         ):
    '''
    Calculates the peak height of the profile. 
    '''
    
    if norm:
        im = im - np.mean(im, axis = axis, keepdims = True)
    return np.amax(im, axis = axis, **kwargs)
    

# %% ../01_profile.ipynb 20
def Rv(im, #Numpy array or array like
       axis = 1, # Default to peaks of rows
       norm = True, #Normalize the profile by subtracting the mean
       **kwargs #Keyword arguments to modify the numpy.amin function
         ):
    '''
    Calculates the absolute max valley depth of the profile. 
    '''
    
    if norm:
        im = im - np.mean(im, axis = axis, keepdims = True)
        
    return abs(np.amin(im, axis = axis, **kwargs))

# %% ../01_profile.ipynb 21
def Rz(im, #Numpy array or array like
       axis = 1, # Default to peaks of rows
       norm = True, #Normalize the profile by subtracting the mean
       **kwargs #Keyword arguments to modify the numpy.ptp function
         ):
    '''
    Calculates the maximum height (max height + absolute max depth) of the profile. Synonymous with range. 
    Also called Rt
    '''
    
    if norm:
        im = im - np.mean(im, axis = axis, keepdims = True)
    
    return np.ptp(im,axis = axis, **kwargs)
