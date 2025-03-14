import os
import subprocess
import time
import re

# Function to read parameters from file
def read_comet_params(file_path,
                      precursor_mass_tolerance_val =  10.0,
                      fragment_mass_tolerance_val =  0.01,
                      activation_method_val = 'ALL',
                      instrument_val = 'high_res'):
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines and comments
                continue
            if line.startswith("peptide_mass_tolerance"):
                match = re.search(r"peptide_mass_tolerance\s*=\s*([\d.]+)", line)
                if match:
                    precursor_mass_tolerance_val = float(match.group(1))
            elif line.startswith("fragment_mass_tolerance"):
                match = re.search(r"fragment_mass_tolerance\s*=\s*([\d.]+)", line)
                if match:
                    fragment_mass_tolerance_val = float(match.group(1))
            elif line.startswith("instrument"):
                match = re.search(r"instrument\s*=\s*(\S+)", line)
                if match:
                    instrument_val = match.group(1)
            elif line.startswith("activation_method"):
                match = re.search(r"activation_method\s*=\s*(\S+)", line)
                if match:
                    activation_method_val = match.group(1)
    return precursor_mass_tolerance_val, fragment_mass_tolerance_val, activation_method_val, instrument_val
            

def run_comet_adapter(data_dir, output_dir, db, cometexe):
    param_dir = os.path.join(output_dir, "param_files")
    prot_id_dir = os.path.join(output_dir, "idxml/")
    if not os.path.exists(prot_id_dir):
        os.makedirs(prot_id_dir)
        print(f"Created directory: {prot_id_dir}")
    
    # Read mzML files ending with '.mzML'
    mzml_files = [f for f in os.listdir(data_dir) if f.endswith('.mzML')]

    # Process each mzML file
    for mzml_file in mzml_files:
        pride_id = mzml_file.split('_')[0]  # Extract part before the first '_'
        filename = mzml_file.split('.mzML')[0]
        idxml_file = f"{filename}_CometAdapter.idXML"
 
        # Run Comet only if no corresponding idXML file exists
        if not os.path.exists(os.path.join(prot_id_dir, idxml_file)):

            # Perform param search for file to receive adequate Comet results
            param_filename = filename + '_params_comet_params.txt'
            param_filepath = os.path.join(param_dir, param_filename)
        
            # Read and update parameters from the file
            precursor_mass_tolerance_val, fragment_mass_tolerance_val, activation_method_val, instrument_val = read_comet_params(param_filepath)
            print(fragment_mass_tolerance_val)

            cmd = [
                "CometAdapter",
                "-in", os.path.join(data_dir, mzml_file),
                "-out", os.path.join(prot_id_dir, idxml_file),
                #"-default_params_file", param_filepath,
                #"-database", "../data/proteomes/uniprot_sprot.fasta",
                "-database", db,
                #"-comet_executable", "/mnt/volume/elisa/orphan_test/master_thesis/Comet/comet.exe",
                "-comet_executable", cometexe,
                "-spectrum_batch_size", "0",
                "-precursor_mass_tolerance", str(precursor_mass_tolerance_val),
                "-fragment_mass_tolerance", str(fragment_mass_tolerance_val),
                "-instrument", instrument_val,
                "-activation_method", activation_method_val,
                #"-decoy_string", "DECOY_",
                "-threads", str(16),
                "-force"
            ]
        
            print(f"Running: {' '.join(cmd)}")
            start_time = time.time()
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                with open(os.path.join(prot_id_dir, idxml_file), "w") as f:
                    pass
                print(f"Error processing {mzml_file}. Skipping to the next file.")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken for {mzml_file}: {elapsed_time:.2f} seconds")