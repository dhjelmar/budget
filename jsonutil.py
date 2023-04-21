'''
General utilities for working with json files
'''

# %%
# standard imports
import copy
import time
import shutil
import pathlib
from datetime import datetime
from typing import Any, List, NoReturn, Union, Callable

# %%
def flatten_dict(
    nested_dict: dict,
    parent_key: str = "",
    sep: str = "."
) -> dict:
    '''
    Adapted from: https://stackoverflow.com/questions/6027558

    Flatens a nested dictionary

    Parameters
    ----------
    nested_dict : dict
        A dictionary of key-value pairs, where the values may be dictionaries
    parent_key : str, optional (default: "")
        Prepended key name used in recursive key name flattening (default recommended)
    sep : str, optional (default: ".")
        Character used to separate concatenated key names during flattening

    Returns
    -------
    dict
        A flattened dictionary of key-value pairs

    Example
    -------
    d = {"a": 1, "c": {"a":2, "b": {"x": 5, "y": 10}}, "d": {"belle": [1,2,3], "sam": 5}}
    d_flat = flatten_dict(d)
    for k, v in d_flat.items():
        print((k, v))
    \n
    Returns: \n
    ("a", 1) \n
    ("c.a", 2) \n
    ("c.b.x", 5) \n
    ("c.b.y", 10) \n
    ("d.belle", [1,2,3]) \n
    ("d.sam", 5) \n

    Access example
    --------------
    d_flat['c.b.x']

    Returns:
    5
    '''

    flat_dict = []
    for key, value in nested_dict.items():
        new_key = parent_key + sep + str(key) if parent_key else str(key)
        if value and isinstance(value, dict):
            flat_dict.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            flat_dict.append((new_key, value))
    return(dict(flat_dict))


# %%
def flat_print(dict : dict = None):
    '''
    Print dictionary as a flattened vertical list to screen
 
    Example
    -------
    d = {"a": 1, "c": {"a":2, "b": {"x": 5, "y": 10}}, "d": {"belle": [1,2,3], "sam": 5}}
    print('regular print(d)')
    print(d)        # single line output
    print('')
    print('flat_print(d)')
    flat_print(d)   # list output
    '''
    flatdict = flatten_dict(dict)
    for k, v in flatdict.items():
        print((k, v))




##--------------------------------------------------------
# %% [markdown]
# Following does not work


# %%
def is_iterable(x):
    return hasattr(x, '__iter__') and not isinstance(x, (str, bytes))



# %%
def map_to_iterable(
    var: Union[dict, list],
    func: Callable,
    args: list = None,
    kwargs: dict = None
) -> Union[dict, list]:
    '''
    Recursively applies a function to each element of an iterable;
    works on most iterable types, but intended for dicts/lists

    Adapted from: https://stackoverflow.com/questions/37714933

    Parameters
    ----------
    var : Union[dict, list]
        A dictionary/list that may contain other dictionaries/lists
    func: Callable
        A function, though probably not any function
    args: list = None
        Arguments to the provided function
    kwargs: dict = None
        Keyword arguments to the provided function

    Returns
    -------
    Union[dict, list]
        [description]
    '''

    if args is None:
        args = []
    if kwargs is None:
        kwargs = []
    if not is_iterable(var):
        return func(var, *args, **kwargs)
    ls_type = type(var)
    if ls_type == dict:
        ls = {k: map_to_iterable(v, func, args, kwargs) for (k, v) in var.items()}
    else:
        ls = [map_to_iterable(v, func, args, kwargs) for v in var]
    return ls_type(ls)
# %%
