# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_data.ipynb.

# %% auto 0
__all__ = ['gen_rot_prof', 'image2xyz', 'xyz2image', 'remove_form', 'plane_level', 'smooth_image', 'gen_sections',
           'compute_parameters', 'distance_matrix', 'normalize']

# %% ../00_data.ipynb 5
import numpy as np
import imutils
import cv2 as cv
from matplotlib import pyplot as plt
import scipy.ndimage as ndimage
import scipy
import sklearn.preprocessing
import sklearn.linear_model
from mpl_toolkits import mplot3d

# %% ../00_data.ipynb 15
def gen_rot_prof(array, #2D array of height values
                 deg       = 180, #Number of degrees to rotate through, i.e 180 gives full 360 rotation
                 increment = 1 # indent/180 = number of evenly spaced profiles to calculate.  
                ):
    
    ''' Generates an array of rotational profiles through to deg, in even increments of increment. 
    Uses OpenCV and Imutils to rotate the array around the center of the array/raster/image, extracts the middle row. 
    '''
    if deg % increment != 0:
        raise ValueError('Cannot sample evenly, deg % indent must = 0')
        
    profiles = np.zeros(shape = (deg//increment,array.shape[0]))
    index    = 0
    center   = array.shape[0]//2  #Center is returned as index to the right of center for even arrays
    
    for degree in range(0, deg, increment):
        rot_array          = imutils.rotate(array, angle = degree)
        profiles[index, :] = rot_array[center,:]
        index             += 1
    return profiles
            

# %% ../00_data.ipynb 17
def image2xyz(im):
    '''
    Converts 2D (m,n) image/array to xyz coordinates. Used for plane levelling
    '''
    
    m, n = im.shape
    Y, X = np.mgrid[:m,:n]
    xyz = np.column_stack((X.ravel(),Y.ravel(), im.ravel()))
    
    return xyz

# %% ../00_data.ipynb 18
def xyz2image(xyz, # (n,3) shape array 
             ):
    '''
    Helper to convert back from xyz (n,3) arrays to (M,N) image/matrices
    '''
    return xyz[:,2].reshape(np.max(xyz[:,1]) + 1,
                            np.max(xyz[:,0]) + 1)

              


# %% ../00_data.ipynb 21
def remove_form(im, # 2D Numpy array or array like
               degree = 3, # Polynomial degree to remove
               return_form = False # Return the form/computed polynomial values instead of removing them from im
               ):
    '''
    Remove the form of the raster by fitting a polynomial of specified degree and subtracting it. 
    '''
    imagexyz = image2xyz(im)
    imagexy  = imagexyz[:,:2]
    imagez   = imagexyz[:,2]
    
    poly     = sklearn.preprocessing.PolynomialFeatures(degree=degree, include_bias = False) #No bias as it is introduced later
    features = poly.fit_transform(imagexy)
    
    poly_reg_model = sklearn.linear_model.LinearRegression() #Polynomial Regression Model
    poly_reg_model.fit(features, imagez)
    
    predictions    =  poly_reg_model.predict(features) #Get the fitted values
    form = predictions.reshape(int(np.max(imagexyz[:,1])) + 1, #Reshape the predictions into the original image dimensions
                               int(np.max(imagexyz[:,0])) + 1)
    if return_form:
        return form
    else:
        return im - form
    

# %% ../00_data.ipynb 22
def plane_level(im, #Numpy array or array like
                norm = True, #Normalize the data by subtracting the mean
                return_form = False
               ):
    '''
    Level an (m,n) array by computing the best fit plane and subtracting the results.
    Thin wrapper around `remove_form` with degree = 1. 
    '''
    if norm:
        im = im - np.mean(im, axis = None)
        
    return remove_form(im = im, degree = 1, return_form = return_form)

# %% ../00_data.ipynb 28
def smooth_image(array, #Numpy array or array like
                 sigma = 1, #Standard deviation for gaussian kernel Useful for determining the wavelength of the low pass filter
                 **kwargs #Keyword arguments for modification of the gaussian_filter function
                ):
    '''
    Removes low frequency/wavelength features ('noise') by applying a gaussian filter on the image. 
    Thin wrapper of scipy.ndimage.gaussian_filter.
    '''
    return ndimage.gaussian_filter(input = array, sigma = sigma, **kwargs)

# %% ../00_data.ipynb 30
def gen_sections(image, #2D array (or arraylike) of height values
                how = 'square', #How to subdivide the array, options are: 'square', 'row', 'column'
                number = 100, #Number of sections to produce
                
                ):
    '''
    Generates sections of the array/image, either in square, horizontal, or vertical sections.
    Useful for studying the change of parameters over the surface.
    Mostly wraps around np.hsplit and np.vsplit.
    Note, if 'number' does not divide into the array evenly, the bottom/side remains will not be
    included. 
    '''
    if how not in ['square','row','column']:
        raise ValueError('Invalid how, expected one of:')
   
    if how == 'square':
        im_height, im_width = image.shape
        length   = number**0.5
        roww     = int(im_height//length)
        colw     = int(im_width//length) 

        image = image[:(im_height - (im_height % roww)), :(im_width - (im_width % colw))] #Remove extra rows/columns
        
        #https://towardsdatascience.com/efficiently-splitting-an-image-into-tiles-in-python-using-numpy-d1bf0dd7b6f7
        #reshape_formula = a_10000.reshape(int(im_height/tile),tile,int(im_width/tile),tile,channels)
        image_reshaped = image.reshape(int(im_height/roww),roww,int(im_width/colw),colw)
        
        tiled_image = image_reshaped.swapaxes(1,2)
        
        sectioned_image = tiled_image.reshape(-1,roww,colw)
        return sectioned_image
    
    if how == 'row':
        return np.vsplit(image, number)
    
    if how == 'column':
        return np.hsplit(image, number)

# %% ../00_data.ipynb 39
def compute_parameters(array, #Input array to be calculate parameters on
                       parameter_list:list,  #List of parameters to calculate as strings
                       valid_module  = None, #module to generate functions from, used to check user input, see rough.cli:rough
                       to_df:bool    = False,#Return the parameters as a pandas dataframe, with columns set as the parameter names
                       **kwargs              #Keyword arguments to modify behavior of parameter calls, usually to define sections = True or the axis. 
                      ):
    '''
    Computes a set of parameters for a given array, provide a list of parameters (as strings of their respective functions e.g. ['Ra','Rms']) and a module
    to verify against (might require some module aliasing, see CLI notebook for example use). Returns a list of results or a dataframe.
    '''
    
    results = []
    
    #The following generates a {'func':func} dict from given list of parameters if the parameter is available in the module
    valid_dict = {k: v for k, v in vars(valid_module).items() if callable(v) and k in valid_module.__all__}
    for parameter in parameter_list:
        result = valid_dict[parameter](array, **kwargs)
        results.append(result)
        
    if to_df:
        results_array = np.array(results)
        if len(results_array.shape) == 1: results_array = np.expand_dims(results_array, axis=1) #Fix for when only 1 section is being calculated
        return pd.DataFrame(data = results_array.T, columns = parameter_list)
    else:
        return results

# %% ../00_data.ipynb 40
def distance_matrix(shape: tuple, #Shape of array, used to calculate center if not given
                    center: (int,int) = None, #Central point from which to calculate distances, if None, defaults to x//2, y//2
                    sections = False, #If True, takes the first element of shape as the number of stack in image
                   ):
    '''
    Returns a (m,n) matrix containing distance values from center coordinates.
    
    if Sections = True. Returns (x,m,n) where x is the number of input sections. 
    
    '''
    if sections:
        n_stack = shape[0]
        shape   = shape[1:]
    if center is None:
        center = (shape[0]//2,shape[1]//2)
        
    y_arr, x_arr = np.mgrid[0:shape[0],0:shape[1]]
    #Pythagoras
    return np.sqrt(((y_arr - center[0])**2) + ((x_arr - center[1]) ** 2))
        
    

# %% ../00_data.ipynb 46
def normalize(im, #Array or stack of array to normalize
              axis = 1, #Axis along which to normalize
              how = 'center', #normalization method: 'center', 'standardize', 'minmax'
              feature_range = None, #Tuple containing the feature range for minmax
             ):
    '''
    Normalize the input array along given axis. Typically used to 'center' rows/columns/areas in order to calculate parameters.
    how can be:
    - 'center': Subtract the mean from the array along the axis,
    - 'l1'
    - 'l2'
    - 'standardize' : Subtract the mean and divide by the standard deviation along given axis
    - 'minmax' : 'standardize' within 'feature_range'. See use in `Sal`
    
    Mostly a reimplementation of scalers from sklearn with explicit formulation. 
    '''
    if how == 'center':
        return im - np.mean(im,axis=axis,keepdims= True)
    elif how == 'standardize':
        return ((im - np.mean(im,axis=axis,keepdims=True)) / np.std(im,axis=axis,keepdims= True))
    elif how == 'minmax':
        if feature_range is None:
            feature_range = (-1,1)
            
        im_std = (im - np.amin(im,axis=axis,keepdims=True)) / np.ptp(im,axis=axis,keepdims=True)
        min_r,max_r = feature_range 
        return im_std * (max_r - min_r) + min_r
    elif how == 'none':
        return im
    
