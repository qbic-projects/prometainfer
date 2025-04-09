### Infer Missing Metadata from Proteomics Data Using Machine Learning and Database Search

import os
import argparse
import subprocess
from generate_fileinfo_files import generate_fileinfo
from parse_keywords import parse_keywords
from create_parameter_files import create_parameter_files
from run_comet_adapter import run_comet_adapter  
from create_feature_file import create_feature_file
from ml_prediction import ml_prediction
from metadata_file_creation import metadata_file_creation

# Set up the argument parser for input and output directories
def parse_arguments():
    parser = argparse.ArgumentParser(description="Infer missing metadata from proteomics data using ML and database search.")
    parser.add_argument('--mzml_dir', type=str, required=True, help="Folder path containing mzML files.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory where the metadata CSV will be stored.")
    parser.add_argument('--idxml_dir', type=str, help="Optional: Folder path for protein/peptide identification files (idXML).")
    parser.add_argument('--database', type=str, help="Path to the protein database (e.g., SwissProt) for peptide identification.")
    parser.add_argument('--comet_exe', type=str, help="Path to the Comet executable (comet.exe) for peptide identification.")
    return parser.parse_args()

# Check if mzML files exist in the specified directory
def check_mzml_files(mzml_dir):
    mzml_files = [f for f in os.listdir(mzml_dir) if f.endswith('.mzML')]
    if mzml_files:
        print(f"Analysis Initiated: Metadata inference will be performed on {len(mzml_files)} mzML files located in the specified directory.")
    else:
        print("No mzML files were detected in the specified directory. Consequently, metadata inference cannot be performed.")
    return mzml_files

# Ensure that the output directory and the idXML directory exist (if not, create them)
def create_directories(output_dir, idxml_dir=None):
    # Check if output_dir exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # If idxml_dir is provided, check if it exists and contains idXML files
    if idxml_dir:
        if not os.path.exists(idxml_dir):
            print(f"Warning: The specified idXML directory {idxml_dir} does not exist.")
        else:
            idxml_files = [f for f in os.listdir(idxml_dir) if f.endswith('.idXML')]
            if idxml_files:
                print(f"Found {len(idxml_files)} idXML files in the provided directory.")
            else:
                print(f"Warning: No idXML files found in {idxml_dir}. Proceeding as if no idxml_dir was provided.")
    else:
        # If idxml_dir is not provided, create a default idxml directory inside output_dir
        idxml_dir = os.path.join(output_dir, 'idxml')
        if not os.path.exists(idxml_dir):
            os.makedirs(idxml_dir)
            print(f"Created default idXML directory in {output_dir}: {idxml_dir}")

def run_param_medic(mzml_dir, output_dir):
    """ Runs Docker-Container script for param-medic """
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(mzml_dir)}:/app/mzml",
        "-v", f"{os.path.abspath(output_dir)}:/app/output",
        "predict_tolerances_container",  # name of Docker image
        "--mzml_dir", "/app/mzml",
        "--output_dir", "/app/output"
    ]
    
    print("Running param-medic in Docker:")
    print(" ".join(docker_cmd))
    
    subprocess.run(docker_cmd, check=True)

def main():
    args = parse_arguments()
    
    # Check for mzML files in the mzML folder
    mzml_files = check_mzml_files(args.mzml_dir)
    
    # Create necessary directories for output and idXML files
    create_directories(args.output_dir, args.idxml_dir)

    # === FEATURE GENERATION ===

    # 1. OpenMS FileInfo
    # Creates OpenMS Fileinfo files and stores them in output_dir/fileinfo. Again, if a FileInfo file for a mzML file already exists,
    # the cration of this file is being skipped.
    # FileInfo files contain metadata that could be extracted directly from the mzML file as Instrument, Activation method and Software.
    print("[1/7] Generating OpenMS FileInfo files...")
    generate_fileinfo(args.mzml_dir, args.output_dir)

    # 2. Parses keywords from the mzML text
    # Including keywords related to Modification (PTMs), Quantification, Organism, Organism Part and Disease
    print("[2/7] Parsing keywords from mzML files...")
    parse_keywords(args.mzml_dir, args.output_dir)

    # 3. Param-medic tolerance calculations
    # Calculates mass tolerance estimations (precursor mass tolerance and fragment mass tolerance)
    # using param-medic and stores tolerance files in output_dir/tolerances (one file per mzML)
    # If a file already exists, the creation for this file is being skipped.
    print("[3/7] Starting param-medic tolerance calculations...")
    #run_param_medic(args.mzml_dir, args.output_dir)

    # 4. Parameter file creation
    # Create parameter file based on extracted param-medic parameters and instrument information from
    # OpenMS FileInfo. These files will be used for peptide identification via OpenMS CometAdapter.
    print("[4/7] Creating parameter files for peptide identification...")
    create_parameter_files(args.mzml_dir, args.output_dir)

    # 5. Peptide identification via OpenMS CometAdapter
    # Searches peptides for alle mzML files in curated Swissprot db or another specified database.
    # Throws warning of no database is specified or existent.
    print("[5/7] Running peptide identification using CometAdapter...")
    if args.database and os.path.exists(args.database) and args.comet_exe and os.path.exists(args.comet_exe):
        run_comet_adapter(args.mzml_dir, args.output_dir, args.database, args.comet_exe)
    else:
        print("Warning: Database or Comet executable not provided or not found. Skipping peptide identification.")
    
    # 6. Feature file creation
    # Create feature files based on all extracted information incl. information of peptide id results.
    # These files will be used for ML predictions.
    print("[6/7] Creating feature files for machine learning...")
    if args.idxml_dir:
        idxml_dir = args.idxml_dir
    else: 
        idxml_dir = os.path.join(args.output_dir, "idxml")
    create_feature_file(idxml_dir, args.output_dir)

    # === ML PREDICTIONS === 

    # Predict metadata based on extracted features using Random Forest Classifier
    # Uses pretrained ML models for prediction (stored as pkl files). 
    # Stores predictions incl. estimated accuracy as .csv files
    print(f"[7/7] Predicting metadata...")
    ml_prediction(args.output_dir, os.path.join(args.output_dir,"extracted_features.csv"))
    metadata_file_creation(args.output_dir)
    print(f"Metadata inference completed. Results stored as predicted_metadata.csv in {args.output_dir}")

if __name__ == '__main__':
    main()



    #### TODO Thursday:
#### add prediction.py script to give out prediction + accuracies per ML model
#### (prediction of model with highest accuracy wins)
#### add Generated text fields



