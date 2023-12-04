import os
import shutil
from pathlib import Path
import re

# bids helpers
def getSubjectID(path):
    """
    This function extracts the subject ID from the file path (BIDS format)

    Parameters:
    -----------
    path : str
        Path to data file
    
    Returns:
    --------
    found : str 
        BIDS-compliant subject ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if 'sub-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'sub-([a-zA-Z0-9]+)', text).group(1)
    except AttributeError:
        found = ''
    return found

def getSessionID(path):
    """
    This function extracts the seesion ID from the file path (BIDS format)

    Parameters:
    -----------
    path : str
        Path to data file
    
    Returns:
    --------
    found : str 
        BIDS-compliant session ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if '_ses-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'ses-(\d{8})', text).group(1)
    except AttributeError:
        found = ''
    return found

def split_list(alist, splits=1):
    """
    This function splits a list for multiprocessing

    Parameters:
    -----------
    alist : list
        The list that should be split into multiple sub-lists
    
    Returns:
    --------
    alist : list
        This list contains the multiple sub-lists that are used for multiprocessing
    """
    length = len(alist)
    return [alist[i * length // splits: (i + 1) * length // splits]
            for i in range(splits)]

def CopyandCheck(src, dst):
    """
    This function tries to copy a file with original path (src) to a target path (dst) and 
    checks if the src file exists and if it was copied successfully to dst

    Parameters:
    -----------
    src : str
        Full path of original location (with filename in the path)
    dst : str 
        Full path of target location (with filename in the path)

    Returns:
    --------
    None
        The function copies files (with renaming) from an original path (src) to a target path (dst) 
    """
    if os.path.exists(src):
        shutil.copy(src, dst)
        if not os.path.exists(dst):
            raise ValueError(f'failed to copy {src}')
        # else:
        #     print(f'successfully copied {os.path.basename(src)} to {os.path.basename(dst)} target location')
    else:
        raise Warning(f'File {os.path.basename(src)} does not exist in original folder!')

def getfileList(path, suffix):
    """
    This function lists all "*suffix"-files that are in the given path. 

    Parameters:
    -----------
    path : str
        Path to directory in which we want to search for files
    suffix : str
        Suffix of the files we want to list (e.g., "*.nii.gz")
    
    Returns:
    --------
    file_ls : list
        Return the lists of "*suffix"-files.
    """
    file_ls = sorted(list(Path(path).rglob(suffix)))
    return file_ls