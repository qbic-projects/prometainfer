import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

# List of relevant keywords
keywords = [
    "iTRAQ", "SILAC", "SWATH",
    "phospho", "acetyl", "methyl", "glygly",
    "human", "mouse", "yeast", "virus",
    "liver", "kidney", "brain", "heart", "lung", "plasma", "serum",
    "cancer"
]

# non differential keywords that were removed as they were found in all or no mzML files:
#  Label-Free, DIA, TMT, Organismen & Modifikationen, alle Krankheiten außer cancer
# "Oxidation": "oxidation" in content or "+15.99" in content,
# "Phosphorylation": "phospho" in content or "+79.97" in content,
# "Acetylation": "acetyl" in content or "+42.01" in content,
# "Methylation": "methyl" in content or "+14.02" in content,
# "Ubiquitination": "glygly" in content or "+114.04" in content,
# "Carbamidomethylation": "carbamidomethyl" in content or "+57.02" in content,

def process_mzml(file, mzml_folder, keywords):
    """Reads an mzML file line by line and searches for keywords."""
    file_path = os.path.join(mzml_folder, file)
    print(f"Processing {file}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read().lower()
        
        # Check if keywords are present
        keyword_presence = {kw: int(kw.lower() in content) for kw in keywords}
        
        return {"Filename": file, **keyword_presence}
    
    except Exception as e:
        print(f"Error processing {file}: {e}")
        return None

def parse_keywords(mzml_folder, keywords_dir):
    """Function to parse mzML files for specific keywords and save the results to a CSV file."""
    
    # Ensure that the keyword directory exists
    if not os.path.exists(keywords_dir):
        os.makedirs(keywords_dir)
        print(f"Created directory: {keywords_dir}")
    
    # Define output file
    output_file = os.path.join(keywords_dir, "keyword_parsing_results.csv")
    
    if not os.path.exists(output_file):
        # Process all mzML files in parallel
        mzml_files = [f for f in os.listdir(mzml_folder) if f.endswith(".mzML")]
    
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_mzml, mzml_files, [mzml_folder]*len(mzml_files), [keywords]*len(mzml_files)))
    
        # Remove None values (failed files)
        results = [r for r in results if r is not None]
    
        # Create DataFrame and save to CSV
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
    
        print(f"Keyword parsing completed. Results saved to {output_file}")
    else:
        print(f"Keyword parsing results already created and stored in {output_file}. Proceeding with next step.")
