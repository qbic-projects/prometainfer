### Infer Missing Metadata from Proteomics Data Using Machine Learning and Database Search

import os
import argparse

# Set up the argument parser for input and output directories
def parse_arguments():
    parser = argparse.ArgumentParser(description="Infer missing metadata from proteomics data using ML and database search.")
    parser.add_argument('--mzml_dir', type=str, required=True, help="Folder path containing mzML files.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory where the metadata CSV will be stored.")
    parser.add_argument('--idxml_dir', type=str, help="Optional: Folder path for protein/peptide identification files (idXML).")
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

# Main function to execute the script logic
def main():
    args = parse_arguments()
    
    # Check for mzML files in the mzML folder
    mzml_files = check_mzml_files(args.mzml_dir)
    
    # Create necessary directories for output and idXML files
    create_directories(args.output_dir, args.idxml_dir)
    
    # Placeholder for the next step in processing (e.g., metadata inference)
    # TODO: call next scripts here

    # === FEATURE GENERATION ===

    # 1. 
    # call param_medic -> input mzML files, output: param_medic files
    # abfangen: wenn param_medic dir angegeben mit files enthalten für jede file: skippen 
    # (nur files erstellen wenn flag (nicht) angegeben ist)

    # 2.
    # call create fileinfo files, ebenso wie bei param_medic nur ausführen 
    # wenn noch nicht geschehen

    # 3. 
    # call create param files (als Input notwendig für ML predictions)
    # might also call this function in ML predictions directly where df is built

    # 4. 
    # 05/06? call protein identifications via Comet (small db)
    # throw warning of no db given 
    # add input parameter for this with giving database direction, otherwise prot id cannot be
    # performed/ must be skipped

    # === ML PREDICTIONS === 

    # call ml scripts for predicting metadata
    # dont train model here just load pkl files with trained models
    # (still upload training code if anybody wants to build up on this/ train with own files)
    # separate function for this: train_metadata_model -> for this facet files also
    # need to be generated etc.

    # give out predictions as csv files, also indicating estimated accuracy of the prediction
    # per entry

if __name__ == '__main__':
    main()
