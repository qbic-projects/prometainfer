import os
import re
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import os
import pandas as pd
import numpy as np
import pyopenms as oms
from pyopenms import *
import pickle

# === 1. EXTRACT FEATURES FROM OpenMS FILEINFO TXT FILES ===
def extract_features_from_txt(file_path):
    """Extracts features from an OpenMS FileInfo text file."""
    features = {
        "instrument_model": "Not available",
        "organism": "Not available",
        "tissue": "Not available",
        "disease": "Not available",
        "software": "Not available",
        "activation_method": "",
        "experiment_type": "Not available",
        "fraction_identifier": "Not available",
        "quantification_method": "Not available",
        "cleavage_agent": "Not available",
    }

    with open(file_path, "r") as f:
        content = f.readlines()
    
    if not content:
        print("empty file")

    for line in content:
        line = line.strip()

        # Extract retention time range
        if "retention time:" in line:
            match = re.findall(r"([\d\.]+)", line)
            if len(match) == 2:
                features["rt_min"] = float(match[0])
                features["rt_max"] = float(match[1])
        
        # Extract mass-to-charge (m/z) range
        elif "mass-to-charge:" in line:
            match = re.findall(r"([\d\.]+)", line)
            if len(match) == 2:
                features["mz_min"] = float(match[0])
                features["mz_max"] = float(match[1])
        
        # Extract intensity range
        elif "intensity:" in line:
            match = re.findall(r"([\d\.e\+]+)", line)  # Handle scientific notation
            if len(match) == 2:
                features["intensity_min"] = float(match[0])
                features["intensity_max"] = float(match[1])
        
        # Extract precursor charge distribution
        elif "charge" in line and "x" in line:
            match = re.search(r"charge (\d+): (\d+)x", line)
            if match:
                charge, count = int(match.group(1)), int(match.group(2))
                features[f"precursor_charge_{charge}"] = count
        
        # Extract instrument model
        elif "Instrument:" in line:
            if features["instrument_model"] == "Not available":
                if(line.split("Instrument: ")[-1].strip() != "Instrument:"):
                    features["instrument_model"] = line.split("Instrument: ")[-1].strip()
        
        # Extract total number of peaks
        elif "Total number of peaks:" in line:
            match = re.search(r"(\d+)", line)
            if match:
                features["total_peaks"] = int(match.group(0))
        
        # Extract number of spectra
        elif "Number of spectra:" in line:
            match = re.search(r"(\d+)", line)
            if match:
                features["num_spectra"] = int(match.group(0))
        
        # Extract organism, tissue, and disease (if available)
        elif "organism:" in line.lower():
            if line.split(": ")[-1].strip() != 'organism:':
                features["organism"] = line.split(": ")[-1].strip() 
        elif "tissue:" in line.lower():
            features["tissue"] = line.split(": ")[-1].strip()
        elif "disease:" in line.lower():
            features["disease"] = line.split(": ")[-1].strip()
        
        # Extract software information
        elif "software name:" in line.lower():
            if(line.split(": ")[-1].strip() != 'software name:'):
                features["software"] = line.split(": ")[-1].strip()

        elif(features["activation_method"] == 'Not available'):
            features["activation_method"] = line.split(':')[0].split("MS-Level 2 & ")[-1].strip()
        
        # Extract activation method
        elif "activation methods" in line.lower():
            features["activation_method"] = 'Not available'
        
        # Extract experiment type (e.g., bottom-up, top-down)
        elif "experiment type:" in line.lower():
            features["experiment_type"] = line.split(": ")[-1].strip()
        
        # Extract fraction identifier
        elif "fraction identifier:" in line.lower():
            features["fraction_identifier"] = line.split(": ")[-1].strip()
        
        # Extract quantification method
        elif "quantification:" in line.lower():
            features["quantification_method"] = line.split(": ")[-1].strip()
        
        # Extract cleavage agent details
        elif "cleavage agent:" in line.lower():
            features["cleavage_agent"] = line.split(": ")[-1].strip()
    if(features["activation_method"] == ""):
        features["activation_method"] = "Not available"
    return features


def get_pephit_stats(idxml_path):
    """Reads a idXML file and returns statistics of its peptide identifications."""
    
    protein_ids = []
    peptide_ids = []
    oms.IdXMLFile().load(idxml_path, protein_ids, peptide_ids)

    protein_bypep = []
    protein_by_eval = []

    # Go through peptide identifications
    for peptide in peptide_ids:
        for hit in peptide.getHits():
            if hit.getScore() <= 0.00001:  # E-Value Cutoff: 1e-5
                for prot_acc in hit.extractProteinAccessionsSet():
                    organism_suffix = str(prot_acc).split("|")[-1].split("_")[-1].split("'")[0]
                    protein_bypep.append(organism_suffix)
                    protein_by_eval.append((organism_suffix, hit.getScore()))

    # Count hits below threshold per organism
    suffix_counts = Counter(protein_bypep)
    
    # Calculate average e-value per organism
    eval_sums = defaultdict(float)
    eval_counts = defaultdict(int)

    for suffix, e_value in protein_by_eval:
        eval_sums[suffix] += e_value
        eval_counts[suffix] += 1

    avg_evals = {suffix: eval_sums[suffix] / eval_counts[suffix] for suffix in eval_sums}

    return suffix_counts, avg_evals

def extract_features_from_idxml(idxml_dir):
    # Dictionary for storage of results
    results = {}

    # Go through all idXML files
    for file in os.listdir(idxml_dir):
        if file.endswith(".idXML"):
            mzML_filename = file.split("_CometAdapter.idXML")[0] + ".mzML"
            idxml_path = os.path.join(idxml_dir, file)

            if os.path.exists(idxml_path) and os.path.getsize(idxml_path) == 0:
                continue
            suffix_counts, avg_evals = get_pephit_stats(idxml_path)
            

            # Create dictionary for file
            file_data = {"Filename": mzML_filename}

            for suffix, count in suffix_counts.items():
                file_data[f"{suffix}_counthits"] = count
                file_data[f"{suffix}_avgevalhits"] = avg_evals.get(suffix, np.nan)

            results[mzML_filename] = file_data


    # Create df
    df_results = pd.DataFrame.from_dict(results, orient="index").reset_index(drop=True)

    # Fehlende Werte mit Mittelwerten der Spalten füllen
    df_results.fillna(df_results.mean(numeric_only=True), inplace=True)

    return(df_results)


def create_feature_file(idxml_dir, output_dir):
    fileinfo_df_file = os.path.join(output_dir,"fileinfo/fileinfo_extracted_features.csv")
    features_df_file = os.path.join(output_dir,"extracted_features.csv")
    if not os.path.exists(features_df_file):
        # === 2. PROCESS ALL FILEINFO TXT FILES ===
        txt_files = os.path.join(output_dir, "fileinfo")
        data = []
        for txt_file in os.listdir(txt_files):
            if txt_file.endswith(".txt"):
                features = extract_features_from_txt(os.path.join(txt_files,txt_file))
                features["Filename"] = str(txt_file).split(".txt")[0]+".mzML"
                data.append(features)

        # Convert to DataFrame
        features_df = pd.DataFrame(data)
        features_df.to_csv(fileinfo_df_file, index=False)

        peptide_stats_df = extract_features_from_idxml(idxml_dir)

        # Merge peptide stats and features over Filename
        merged_df = features_df.merge(peptide_stats_df, on="Filename", how="left")

        # Fill missing values after merge with nans
        merged_df.fillna(merged_df.mean(numeric_only=True), inplace=True)

        # Move "Filename" column to beginning
        merged_df.insert(0, "Filename", merged_df.pop("Filename"))

        merged_df.to_csv(features_df_file, index=False)


