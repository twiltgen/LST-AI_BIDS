# LST-AI Lesion Segmentation Pipeline

This repository contains a Python script for applying LST-AI lesion segmentation and performing the necessary pre-processing steps on T1w and FLAIR images. The script processes a list of subjects, checks for the availability of required images, and runs the segmentation pipeline, producing outputs that comply with BIDS (Brain Imaging Data Structure) conventions.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Arguments](#arguments)
- [Pipeline Details](#pipeline-details)

## Installation

To use this script, ensure you have Python installed on your system along with the required dependencies. You can install the necessary dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Usage

To run the LST-AI pipeline, use the following command:

```bash
python run_lst_ai.py -i /path/to/bids/dataset -n 4 --cpu --remove_temp --clipping 0.5 99.5
```

## Arguments

*    -i, --input_directory: (Required) Path to the derivatives folder in the BIDS database.
*    -n, --number_of_workers: Number of parallel processing cores to use (default: os.cpu_count()-1).
*    --cpu: Use this flag to process using CPU only (default: GPU if available).
*    --remove_temp: Use this flag to remove the temporary folder containing auxiliary files after processing.
*    --clipping: Clipping for standardization of image intensities (default: (0.5, 99.5)).

## Pipeline Details

The script performs the following steps:
1.  Pre-processing: Applies skull-stripping and image registration to T1w and FLAIR images.
2.  Segmentation: Runs the LST-AI lesion segmentation on the pre-processed images.
3.  Output Handling: Checks if the segmentation was successful, renames output files to comply with BIDS conventions, and optionally removes temporary files.
