import argparse
import os
from pathlib import Path
import pandas as pd

from utils import getfileList, getSessionID, getSubjectID

####################################################
# main script

parser = argparse.ArgumentParser(description='Check for missing segmentation files (e.g., when processing did not work).')
parser.add_argument('-i', '--input_directory', help='Folder of BIDS database.', required=True)
parser.add_argument('-o', '--output_directory', help='Destination folder for the output file.', required=True)

# read the arguments
args = parser.parse_args()

# define path of the derivatives folder
derivatives_dir = os.path.join(args.input_directory, "derivatives/lst-ai-v1.1.0")

# get a list with all subject folders in the database
T1w_list = getfileList(path = args.input_directory, 
                       suffix = '*T1w*')
T1w_list = [str(x) for x in T1w_list if (('.nii.gz' in str(x)) and 
                                         (not 'derivatives' in str(x)) and
                                         (not 'GADOLINIUM' in str(x)))]

# get a list with the paths of the _seg.mgz files 
seg_list = getfileList(derivatives_dir, '*_space-FLAIR_label-lesion_mask.nii.gz')


# initialize empty dataframe into which we will write the IDs of missing segmentations
df_seg_missing = pd.DataFrame(columns=['subject-ID', 'session-ID'])
df_seg_processed = pd.DataFrame(columns=['subject-ID', 'session-ID'])
for i in range(len(T1w_list)):
    # get subject and session ID
    subjectID = getSubjectID(T1w_list[i])
    sessionID = getSessionID(T1w_list[i])

    # define path of segmentation file
    seg_path = Path(os.path.join(derivatives_dir, f'sub-{subjectID}', f'ses-{sessionID}', 'anat', f'sub-{subjectID}_ses-{sessionID}_space-FLAIR_label-lesion_mask.nii.gz'))

    # check if segmentation file is in seg_list 
    # (if not, then the segmentation must have failed and we want to write the IDs into df_seg_missing)
    if seg_path in seg_list:
        # write subject and session IDs in the dataframe
        dict_proc = {df_seg_processed.columns[0]:[subjectID], df_seg_processed.columns[1]:[sessionID]}
        df_proc = pd.DataFrame(data=dict_proc)
        df_seg_processed = pd.concat([df_seg_processed, df_proc])
        print(f'{subjectID}/{sessionID}: processed successfully!')
    else:
        # write subject and session IDs in the dataframe
        dict_miss = {df_seg_missing.columns[0]:[subjectID], df_seg_missing.columns[1]:[sessionID]}
        df_miss = pd.DataFrame(data=dict_miss)
        df_seg_missing = pd.concat([df_seg_missing, df_miss])
        print(f'{subjectID}/{sessionID}: segmentation failed!')


# write dataframe with missing files as .csv file in chosen output directory
df_seg_missing.to_csv(os.path.join(args.output_directory, "lst-ai_cross_missing.csv"), index=False)
# write dataframe with processed files as .csv file in chosen output directory
df_seg_processed.to_csv(os.path.join(args.output_directory, "lst-ai_cross_processed.csv"), index=False)