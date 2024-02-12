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
    indices = [i for i, s in enumerate(stringList) if 'ses-' in s]
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

def availability_check(sub_dirs, deriv_dir, file_suffix):
    """
    This function checks availability of files with a specific suffix (e.g., "_space-T1w_seg.nii.gz") within a derivatives folder for each subject in the provided list and outputs two lists, 
    one with subjects with missing files and one with subjects fow hich all fuiles are available. First, the function iterates over all subjects, and for each subject it lists all available 
    sessions and then checks the availability of files for each session in the provided derivatives folder.

    Parameters:
    -----------
    sub_dirs : list
        List with all subject IDs for which availability of files should be checked
    deriv_dir : str
        Path of derivatives folder in which availability of files should be checked
    file_suffix : str
        Suffix of files for which availability should be checked
    
    Returns:
    --------
    sub_missing : list
        List with subjects for which one or more files are missing
    sub_available : list 
        List with subjects for which all files are available
    """
    # initialize empty lists
    sub_missing = []
    sub_available = []

    # iterate through all subject folders
    for sub_dir in sub_dirs:
        # get subject ID
        sub_ID = getSubjectID(sub_dir)

        # list all sessions
        ses_dirs = sorted(list(Path(sub_dir).glob('*')))
        ses_dirs = [str(x) for x in ses_dirs if "ses-" in str(x)]
        
        # initialize availability list 
        any_missing = []

        # iterate through all sessions
        for ses_dir in ses_dirs:
            # get session ID
            ses_ID = getSessionID(ses_dir)

            # check availability of file for this session
            file_path = os.path.join(deriv_dir, f'sub-{sub_ID}', f'ses-{ses_ID}', 'anat', f'sub-{sub_ID}_ses-{ses_ID}_{file_suffix}')
            t1_path = os.path.join(ses_dir, 'anat', f'sub-{sub_ID}_ses-{ses_ID}_T1w.nii.gz')
            flair_path = os.path.join(ses_dir, 'anat', f'sub-{sub_ID}_ses-{ses_ID}_FLAIR.nii.gz')
            if (not os.path.exists(file_path)) and os.path.exists(t1_path) and os.path.exists(flair_path):
                any_missing.append(True)
            else:
                any_missing.append(False)
        
        # check if files are missing for any of the sessions and add subject to sub_missing or sub_available accordingly
        if any(any_missing):
            sub_missing.append(sub_dir)
        else:
            sub_available.append(sub_dir)
    
    return sub_missing, sub_available