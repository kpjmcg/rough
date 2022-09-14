# AUTOGENERATED! DO NOT EDIT! File to edit: ..\04_cli.ipynb.

# %% auto 0
__all__ = ['compute_parameters', 'rough']

# %% ..\04_cli.ipynb 3
from fastcore.script import *
import numpy as np
import pandas as pd
from pathlib import Path

from .data import *
from .profile import *
from .section import *

import rough.profile as profile_mod
import rough.section as section_mod

# %% ..\04_cli.ipynb 5
def compute_parameters(array, #Input array to be calculate paramers on
                       parameter_list:list,  #List of parameters to calculate as strings
                       valid_module  = None, #module to generate functions from, used to check user input, see rough.cli:rough
                       to_df:bool    = False,#Return the parameters as a pandas dataframe, with columns set as the parameter names
                       **kwargs              #Keyword arguments to modify behavior of parameter calls, usually to define sections = True
                      ):
    '''
    computes a set of parameters, provide a list of parameters (as strings of their respective functions e.g. ['Ra','Rms']) and a module
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

# %% ..\04_cli.ipynb 7
@call_parse
def rough(
    fname:str   = None,   #File name, path or directory with data files to be read
    ext:str     = '.txt', #Extension for the  files .txt or .csv
    
    result:str     = None,     #Directory to write results to, if None, writes to 'results'
    result_how:str = 'concat', #How to save the results, 'concat' concatenates all respective types of results (i.e. profile,section,rotational,subsection) into one dataframe file. 'split' produces respective result files for each input file. Use split for large amounts of data.
    
    level:Param("Perform plane levelling", bool_arg) = True, #Perform plane levelling 
    form:Param("Remove form by polynomial subtraction", bool_arg) = True, #Remove form by polynomial subtraction
    deg:int = 3, #Degree of polynomial to remove
    smooth:Param("Smooth array by applying gaussian", bool_arg) = True, #Smooth the array by applying a gaussian
    sigma:int = 1, #Sigma for gaussian to be applied
    
    gen_rot:Param("Generate rotational profiles and apply parameter calculation to them", bool_arg) = True, #Generate rotational profiles and apply parameter calculation to them
    
    gen_section:Param("Generate sub-sections of the surface", bool_arg) = True, #Generate sub-sections of the surface
    sec_how:str = 'square', #Type of section to generate, currently only supports 'square'
    sec_num:int = 100,      #Number of sections to generate
    
    profile:Param("Calculate profile parameters", bool_arg) = True, #Calculate profile parameters
    section:Param("Calculate section parameters", bool_arg) = True, #Calculate section parameters
    
    params1D:list = profile_mod.__all__, # list of 1D parameters to calculate,
    params2D:list = section_mod.__all__, #list of 2D parameters to calculate, calculates for both the sections and the whole
):
    '''
    Perform parameter calculation on a given file or directory, if none is provided .
    '''
    
    delims = {'.txt': None,
              '.csv': ','}
    
    path = Path().cwd() if fname == None else Path(fname)
    
    #Figuring out where the file/s are and results go
    if   path.is_dir():
        result_dir = path / 'results' if result == None else Path(result)
    elif path.is_file():
        result_dir = path.parent / 'results' if result == None else Path(result) 

    if not path.exists(): 
        raise FileNotFoundError('Could not find file/directory check fname')
    if not result_dir.exists(): 
        result_dir.mkdir(parents=True) #Make the results directory if it doesn't exist
        
    glob_pattern    = '*' + ext
    file_paths = [path] if path.is_file() else path.glob(glob_pattern)
    
    if result_how == 'concat': 
        profile_result_list = []
        rot_profile_result_list = []
        section_result_list = []
        sections_result_list = []
    
    for file_path in file_paths:
        array = np.loadtxt(file_path,delimiter=delims[file_path.suffix])
        print(file_path)
        print('got to before data cleaning')
        
        #--------------Data Cleaning-------------------------
        if level:
            array = plane_level(array)
            print('Got to level')
        if form:
            array = remove_form(array)
            print('Got to form')
        if smooth:
            array = smooth_image(array,sigma=sigma)
            print('got to smooth')
            
        #-------------Parameter Calculation------------------
        if profile:
            profile_results = compute_parameters(array, params1D, profile_mod, to_df = True)
            
            if result_how == 'concat':
                profile_results.insert(loc = 0, column = 'id', value = file_path.stem)
                profile_result_list.append(profile_results)
            if gen_rot:
                profiles = gen_rot_prof(array)
                rot_profile_results = compute_parameters(profiles, params1D, profile_mod, to_df = True)
                
                if result_how == 'concat':
                    rot_profile_results.insert(loc = 0, column = 'id', value = file_path.stem)
                    rot_profile_result_list.append(rot_profile_results)
        
        if section:
            section_results = compute_parameters(array, params2D, section_mod, to_df = True)
            
            if result_how == 'concat':
                section_results.insert(loc = 0, column = 'id', value = file_path.stem)
                section_result_list.append(section_results)
            
            if gen_section:
                sections         = gen_sections(array, how=sec_how, number = sec_num)
                sections_results = compute_parameters(sections, params2D, section_mod, sections = True, to_df = True)
                
                if result_how == 'concat':
                    sections_results.insert(loc = 0, column = 'id', value = file_path.stem)
                    sections_result_list.append(sections_results)
    #-----------Data saving----------------------
        if result_how == 'split':
            #TODO: figure out how to make this into a loop
            if profile:
                profile_file_name  = file_path.stem +'_profile.csv'
                result_path = result_dir / profile_file_name
                profile_results.to_csv(result_path)
                
            if gen_rot:
                rot_file_name      = file_path.stem + '_rotprofile.csv'
                result_path = result_dir / rot_file_name
                rot_profile_results.to_csv(result_path)
            if section:
                section_file_name  = file_path.stem + '_section.csv'
                result_path = result_dir / section_file_name
                section_results.to_csv(result_path)
            if gen_section:
                sections_file_name = file_path.stem + '_sections.csv'
                result_path = result_dir / section_file_name
                sections_results.to_csv(result_path)
            print(f'Finished saving {file_path.stem} results') 
            
    if result_how == 'concat':
        if profile:
            result_path = result_dir / 'profile.csv'
            results = pd.concat(profile_result_list)
            results.to_csv(result_path)
            print(f'Saved profile results to {result_path}')
        if gen_rot:
            result_path = result_dir / 'rotprofile.csv'
            results = pd.concat(rot_profile_result_list)
            results.to_csv(result_path)
            print(f'Saved rotational profile results to {result_path}')
        if section:
            result_path = result_dir / 'section.csv'
            results = pd.concat(section_result_list)
            results.to_csv(result_path)
            print(f'Saved section results to {result_path}')
        if gen_section:
            result_path = result_dir / 'sections.csv'
            results = pd.concat(sections_result_list)
            results.to_csv(result_path)
            print(f'Saved sub-section results to {result_path}')
