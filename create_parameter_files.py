import os
import re
import numpy as np

# script that ready in param_prediction, if not available instrument, if not 
# available sets default parameters in a {mzml_file}_paramams.txt, that we can
# call to run CometAdapter for each file respectively

# parse information from parameter prediction via param_medic library
def parse_txt_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    CHECK_PRED_EXISTENT = False
    
    for line in lines:
        if CHECK_PRED_EXISTENT:
            pred_vals = line.strip().split('\t')
            return cols, pred_vals
        elif line.startswith('file\tprecursor_prediction_ppm'):
            CHECK_PRED_EXISTENT = True
            cols = line.strip().split('\t')
    return None, None

# information from OpenMS fileinfo
def parse_fileinfo_file(file_path):
    instrument = None
    activation_method = None

    with open(file_path, 'r') as f:
        content = f.read()
        FOUND_INSTR = False
        # Search for 'Instrument' in the content
        instrument_match = re.search(r'Instrument:\s*(.*)', content)
        if instrument_match and not FOUND_INSTR:
            instrument = instrument_match.group(1).split("Instrument: ")[-1].strip()
            FOUND_INSTR = True

        # Search for 'Activation methods' in the content
        activation_match = re.search(r'Activation methods\s*(.*?)\s*(MS-Level.*)', content, re.DOTALL)
        if activation_match:
            # Find the part starting from 'Activation methods'
            activation_method_start = activation_match.group(1).split(":")[0].split('MS-Level 2 & ')[-1].strip()
            # Collect all MS-Level entries following the initial 'Activation methods'
            additional_activation_methods = []
            # Start collecting all lines that start with 'MS-Level'
            for line in content.splitlines():
                if line.strip().startswith("MS-Level"):
                    additional_activation_methods.append(line.split(":")[0].split('MS-Level 2 & ')[-1].strip())

            # Combine all the activation methods into one string
            activation_method = " ".join([activation_method_start] + additional_activation_methods).strip()


    return instrument, activation_method

# High-resolution instruments
high_res_instruments = np.array([
    'Bruker Daltonics maXis series', 'LTQ Orbitrap Elite', 'LTQ Orbitrap Velos', 'LTQ Orbitrap XL', 
    'Orbitrap Fusion', 'Orbitrap Fusion Lumos', 'Q Exactive', 'Q Exactive HF-X', 'Q Exactive Plus', 
    'TripleTOF 5600', 'TripleTOF 6600'
])

# Low-resolution instruments
low_res_instruments = np.array([
    '4800 Proteomics Analyzer', 'Agilent instrument model', 'Bruker Daltonics instrument model', 
    'LTQ', 'MS levels: 1, 2', 'MS levels: 2',
    'Mass Analyzer: Ion trap (resolution: 0)', 'Mass Analyzer: Quadrupole (resolution: 0)', 
    'Mass Analyzer: Unknown (resolution: 0)', 'SCIEX instrument model', 'Waters instrument model'
])

# Single specified activation method
single_act_method = np.array(['CID (Collision-induced dissociation)',
 'ETD (Electron transfer dissociation)',
 'HCID (High-energy collision-induced dissociation)',
 'LCID (Low-energy collision-induced dissociation)'])

def create_param_file(pred_vals, output_path, instrument, activation_method):
    with open(output_path, 'w') as f:
        f.write("# Comet MS/MS search engine parameters file.\n")

        #f.write("database_name = ../data/proteomes/uniref90_with_decoys.fasta\n")
        f.write("decoy_search = 1\n") # # 0=no (default), 1=internal decoy concatenated, 2=internal decoy separate
        f.write("decoy_prefix = DECOY_\n")
        if pred_vals:
            if(pred_vals[1] != 'ERROR' and pred_vals[2] != "ERROR"):
                f.write(f"peptide_mass_tolerance =  {float(pred_vals[1]) + float(pred_vals[2])}\n")
                # peptide_mass_tolerance =  precursor_prediction_ppm + precursor_sigma_ppm, default: 10 ppm # upper bound of the precursor mass tolerance
            if(pred_vals[3] != 'ERROR'):
                f.write(f"fragment_mass_tolerance =  {float(pred_vals[3])/2}\n")
                # fragment_mass_tolerance = fragment_prediction_th/2, default: 0.01 # because Comet bins fragment masses symmetrically around peaks

        # if(activation_method/fragmentation_method == ...):
        #    f.write("activation_method = ...\n") # (default: 'ALL') (valid: 'ALL', 'CID', 'ECD', 'ETD', 'PQD', 'HCD', 'IRMPD')

        # add more parameters based on data
        # ...
        if np.isin(instrument, high_res_instruments):
            f.write(f"instrument = high_res\n")  # Use the instrument extracted from fileinfo
        if np.isin(instrument, low_res_instruments):
            f.write(f"instrument = low_res\n")  # Use the instrument extracted from fileinfo
        if np.isin(activation_method, single_act_method):
            if(activation_method == 'ETD (Electron transfer dissociation)'):
                f.write(f"activation_method = ETD\n")  # Use the activation method extracted from fileinfo
            elif(activation_method == 'CID (Collision-induced dissociation)'):
                f.write(f"activation_method = CID\n")  # Use the activation method extracted from fileinfo
            elif(activation_method == 'HCID (High-energy collision-induced dissociation)'):
                f.write(f"activation_method = HCD\n")  # Use the activation method extracted from fileinfo
            elif(activation_method == 'LCID (Low-energy collision-induced dissociation)'):
                f.write(f"activation_method = LCID\n")  # Use the activation method extracted from fileinfo



def process_files_in_directory(directory_path, output_dir, fileinfo_dir):
    # Durchlaufe alle .txt-Dateien im Ordner
    instruments = []
    act_methods = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(directory_path, file_name)
            data_cols, data_pred_vals = parse_txt_file(file_path)
            # Get corresponding fileinfo
            fileinfo_path = os.path.join(fileinfo_dir, os.path.splitext(file_name)[0].replace('_params', ''))
            instrument, activation_method = None, None
            if os.path.exists(fileinfo_path):
                instrument, activation_method = parse_fileinfo_file(fileinfo_path)
                instruments.append(instrument)
                act_methods.append(activation_method)
            
            # Generate the output file path based on the directory and filename
            output_file_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_comet_params.txt")
            create_param_file(data_pred_vals, output_file_path, instrument, activation_method)
    return np.array(instruments), np.array(act_methods)

def create_parameter_files(data_dir, output_dir):
    pred_dir = os.path.join(output_dir, "tolerances/")
    fileinfo_dir = os.path.join(output_dir, "fileinfo/")
    param_files_dir = os.path.join(output_dir, "param_files/")
    if not os.path.exists(param_files_dir):
        os.makedirs(param_files_dir)
        print(f"Created directory: {param_files_dir}")

    ins, actm = process_files_in_directory(pred_dir, param_files_dir, fileinfo_dir)
    # print('Possible entries for instrument: ',np.unique(ins[ins!= None]))
    # print('\n')
    # print('Possible entries for activation method: ',np.unique(actm[actm!= None]))
