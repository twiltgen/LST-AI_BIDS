import argparse
import os
import pandas as pd

from utils import getfileList, getSessionID, getSubjectID

def combineStats(path, subID, sesID):
    '''
    This function reads the _stats.csv files of a session and merges them into a dataframe. 

    Parameters:
    -----------
    path : str
        Path to the BIDS derivatives directory (e.g., .../Database_BIDS/derivatives/lst-ai-v1.1.0)
    subID : str
        Subject ID of the current session
    sesID : str
        Session ID of the current session
    
    Returns:
    --------
    df : dataframe 
        Dataframe containing all volumes of the current session
    '''
    # define path of stat files and load them as dataframe
    les_path = os.path.join(path, "sub-"+subID, "ses-"+sesID, "anat", f'sub-{subID}_ses-{sesID}_lesion_stats.csv')
    annot_les_path = os.path.join(path, "sub-"+subID, "ses-"+sesID, "anat", f'sub-{subID}_ses-{sesID}_annotated_lesion_stats.csv')
    df_les_stat = pd.read_csv(les_path)
    df_les_stat.insert(0, "Region", "WM")
    df_annot_les_stat = pd.read_csv(annot_les_path)

    # combine lesion stats and annotated lesion stats
    df = pd.concat([df_les_stat, df_annot_les_stat], ignore_index=True)
    # add subject ID and session ID to the dataframe
    df.insert(0, "ses-ID", sesID)
    df.insert(0, "sub-ID", subID)

    return df

####################################################
# main script

parser = argparse.ArgumentParser(description='Read lesion data of LST-AI lesion segmentation.')
parser.add_argument('-i', '--input_directory', help='Folder of derivatives in BIDS database.', required=True)
parser.add_argument('-o', '--output_directory', help='Destination folder for the output table with volume stats.', default='/home/twiltgen/media/twiltgen/raid3/Tun/MR_database/Data/Database')

# read the arguments
args = parser.parse_args()

# define path of the derivatives folder
derivatives_dir = os.path.join(args.input_directory, "derivatives/lst-ai-v1.1.0")

# get a list with the paths of the LST-AI lesion segmentation files 
# (we do this because we only want subject- and session-IDs for the cases that have been successfully segmented by SAMSEG)
seg_list = getfileList(path = derivatives_dir, 
                       suffix = '*space-FLAIR_label-lesion_mask.nii.gz')
# initialize empty dataframe into which we will write the stats data of all cases
df_stat = pd.DataFrame()
for i in range(len(seg_list)):
    # get subject and session ID
    subjectID = getSubjectID(seg_list[i])
    sessionID = getSessionID(seg_list[i])
    # get stats of current session
    loop_stat = combineStats(derivatives_dir, subjectID, sessionID)
    # write stats in the final dataframe
    df_stat = pd.concat([df_stat, loop_stat])
    print(f'sub-{subjectID}_ses-{sessionID}: stats added.')

# write stats table to .csv file in chosen output directory
df_stat.to_csv(os.path.join(args.output_directory, "lst-ai_lesion_stats.csv"), index=False)
