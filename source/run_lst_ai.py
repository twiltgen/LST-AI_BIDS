import argparse
import os
import shutil
import datetime
import subprocess
from pathlib import Path
import multiprocessing
from utils import getSessionID, getSubjectID, split_list, getfileList, availability_check

def process_lst_ai(dirs, derivatives_dir, clipping, remove_temp=False, use_cpu=False):
    """
    This function applies LST-AI lesion segmentation and also applies required pre-processing steps of the T1w and FLAIR images. 
    Pre-processing includes skull-stripping and image registration. 
    We use the original T1w and FLAIR images as input.
    Next, we check if SAMSEG segmentation was successful by making sure that the space-orig_seg-lst.nii.gz file was generated.
    All resulting files are saved to a temp folder and the segmentation files are save to anat folderin derivatives. 
    In order to be compliant with BIDS convention, we rename the output files. 
    Optionally, the output folder can be deleted (e.g., to clean up if it is not needed anymore)

    Parameters:
    -----------
    dirs : list
        List with all subject IDs for which we want to generate LST-AI lesion segmentations
    derivatives_dir : str
        Path of the LST-AI derivatives folder in the BIDS database
    remove_temp : bool
        Boolean variable indicating if the temp folder should be removed after segmentation files were generated
    use_cpu : bool
        Boolean variable indicating if CPU or GPU should be used for processing
    
    Returns:
    --------
    None 
        This function produces LST-AI lesion segmentation files
    """
    # iterate through all subject folders
    for dir in dirs:

        # assemble T1w file lists
        # since we need T1w AND FLAIR images, we can first list all T1w images and then check if FLAIR image also exists
        t1w = getfileList(path = dir, 
                          suffix = '*T1w*')
        t1w = [str(x) for x in t1w if (('.nii.gz' in str(x)) and 
                                       (not 'GADOLINIUM' in str(x)))]
        

        # get subject ID of current subject
        subID = getSubjectID(path = t1w[0])


        # iterate over all sessions with T1w images and check if FLAIR files are available and if lesion segmentation already exists
        for i in range(len(t1w)):
            try:

                # get session ID of current T1w image
                sesID = getSessionID(path = t1w[i])


                # check availability of files and folders (create folders if necessary)
                flair = str(t1w[i]).replace('_T1w.nii.gz', '_FLAIR.nii.gz')
                if not os.path.exists(flair):
                    raise ValueError(f'sub-{subID}_ses-{sesID}: FLAIR image not available!!')
                
                temp_dir = os.path.join(derivatives_dir, f'sub-{subID}', f'ses-{sesID}', 'temp')
                if not os.path.exists(temp_dir):
                    Path(temp_dir).mkdir(parents=True, exist_ok=True)
                
                deriv_ses = os.path.join(derivatives_dir, f'sub-{subID}', f'ses-{sesID}', 'anat')
                if not os.path.exists(deriv_ses):
                    Path(deriv_ses).mkdir(parents=True, exist_ok=True)
                

                # skip to next case if segmentation already exist
                seg_file = os.path.join(deriv_ses, f'sub-{subID}_ses-{sesID}_space-FLAIR_label-lesion_mask.nii.gz')
                seg_file_annot = os.path.join(deriv_ses, f'sub-{subID}_ses-{sesID}_space-FLAIR_desc-annotated_label-lesion_mask.nii.gz')
                if os.path.exists(seg_file) and os.path.exists(seg_file_annot):
                    print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: LST-AI lesion segmentation already exists, skip and proceed to next case...')
                    continue
                

                # define command line for LST-AI
                if remove_temp and use_cpu:
                    command = f'lst --t1 {t1w[i]} --flair {flair} --output {deriv_ses} --device cpu --clipping {clipping[0]} {clipping[1]}'
                elif remove_temp:
                    command = f'lst --t1 {t1w[i]} --flair {flair} --output {deriv_ses} --device 0 --clipping {clipping[0]} {clipping[1]}'
                elif use_cpu:
                    command = f'lst --t1 {t1w[i]} --flair {flair} --output {deriv_ses} --temp {temp_dir} --device cpu --clipping {clipping[0]} {clipping[1]}'
                else:
                    command = f'lst --t1 {t1w[i]} --flair {flair} --output {deriv_ses} --temp {temp_dir} --device 0 --clipping {clipping[0]} {clipping[1]}'
                print(command)
                # run LST-AI
                subprocess.run(command, shell=True)


                # check if folder contains *seg-lst.nii.gz files, indicating that LST-AI successfully finished, and rename files
                output_anat_files = os.listdir(deriv_ses)
                les_vol_file = os.path.join(deriv_ses, f'sub-{subID}_ses-{sesID}_lesion_stats.csv')
                les_vol_annot_file = os.path.join(deriv_ses, f'sub-{subID}_ses-{sesID}_annotated_lesion_stats.csv')

                if ('space-flair_seg-lst.nii.gz' in output_anat_files) and ('space-flair_desc-annotated_seg-lst.nii.gz' in output_anat_files):
                    
                    print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: Rename LST-AI lesion mask (BIDS)...')
                    os.rename(os.path.join(deriv_ses,'space-flair_seg-lst.nii.gz'), seg_file)
                    os.rename(os.path.join(deriv_ses,'space-flair_desc-annotated_seg-lst.nii.gz'), seg_file_annot)
                    os.rename(os.path.join(deriv_ses,'lesion_stats.csv'), les_vol_file)
                    os.rename(os.path.join(deriv_ses,'annotated_lesion_stats.csv'), les_vol_annot_file)
                    if os.path.exists(seg_file) and os.path.exists(seg_file_annot):
                        print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: Rename LST-AI lesion mask (BIDS) DONE!')

                    # also rename auxiliary files if they are available
                    output_temp_files = os.listdir(temp_dir)
                    if (len(output_temp_files)>0):
                        print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: Rename LST-AI auxiliary files (BIDS)...')
                        # iterate over all output files and rename to BIDS
                        for filename in output_temp_files:
                            if ('sub-X_ses-Y' in filename):
                                os.rename(os.path.join(temp_dir, filename), os.path.join(temp_dir, str(filename).replace('sub-X_ses-Y', f'sub-{subID}_ses-{sesID}')))
                            else:
                                os.rename(os.path.join(temp_dir, filename), os.path.join(temp_dir, f'sub-{subID}_ses-{sesID}_{filename}'))
                        print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: Rename LST-AI auxiliary files (BIDS) DONE!')
                else:
                    print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: failed to generate segmentation, delete ouput folder...')
                    shutil.rmtree(str(Path(deriv_ses).parent))
                    if os.path.exists(deriv_ses) or os.path.exists(temp_dir):
                        raise ValueError(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: failed to delete the derivatives folder(s)!')
                    else:
                        print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: successfully deleted the derivatives folder(s)!')
                        continue

            except:
                print(f'{datetime.datetime.now()} sub-{subID}_ses-{sesID}: Error occured during processing, proceeding with next case.')
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run LST-AI Pipeline on cohort.')

    parser.add_argument('-i', '--input_directory', 
                        help='Folder of derivatives in BIDS database.', 
                        required=True)

    parser.add_argument('-n', '--number_of_workers', 
                        help='Number of parallel processing cores.', 
                        type=int, 
                        default=os.cpu_count()-1)

    parser.add_argument('--cpu', 
                        help='Use the --cpu flag if you only want to use CPU.', 
                        action='store_true')
    
    parser.add_argument('--remove_temp', 
                        help='Use the --remove_temp flag if you want to remove the temp folder containing auxiliary files.', 
                        action='store_true')

    parser.add_argument('--clipping',
                        dest='clipping',
                        help='Clipping for standardization of image intensities (default: (min,max)=(0.5,99.5))',
                        nargs='+',
                        type=float,
                        default=(0.5, 99.5))
    
    # read the arguments
    args = parser.parse_args()

    if args.cpu:
        use_cpu = True
    else:
        use_cpu = False

    if args.remove_temp:
        remove_temp = True
    else:
        remove_temp = False
    
    input_path = args.input_directory
    n_workers = args.number_of_workers


    # generate derivatives
    derivatives_dir = os.path.join(input_path, "derivatives/lst-ai-v1.1.0")
    if not os.path.exists(derivatives_dir):
        Path(derivatives_dir).mkdir(parents=True, exist_ok=True)

    
    # generate list with subject folders for multiprocessing
    data_root = Path(os.path.join(input_path))
    dirs = sorted(list(data_root.glob('*')))
    dirs = [str(x) for x in dirs]
    dirs = [x for x in dirs if "sub-" in x]

    # check which files have already been processed
    dirs_missing, dirs_processed = availability_check(sub_dirs=dirs,
                                                      deriv_dir=derivatives_dir,
                                                      file_suffix='space-FLAIR_label-lesion_mask.nii.gz')
    print(f'Number of incomplete subjects: {len(dirs_missing)}')
    print(f'Number of complete subjects: {len(dirs_processed)}')

    # only split the list of subjects with missing LST-AI lesion segmentation for multiprocessing
    files = split_list(alist = dirs_missing, 
                       splits = n_workers)


    # initialize multithreading
    pool = multiprocessing.Pool(processes=n_workers)
    # call samseg processing function in multiprocessing setting
    for x in range(0, n_workers):
        pool.apply_async(process_lst_ai, args=(files[x], derivatives_dir, args.clipping, remove_temp, use_cpu))

    pool.close()
    pool.join()

    print('DONE!')