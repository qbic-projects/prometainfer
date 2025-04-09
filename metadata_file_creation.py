import os
import pandas as pd

def metadata_file_creation(output_dir):

    model1 = "mlp_400_nokey"
    model2 = "mlp_200_nokey"

    model1_df = pd.read_csv(os.path.join(output_dir, f"{model1}_predicted_metadata.csv"))
    model2_df = pd.read_csv(os.path.join(output_dir, f"{model2}_predicted_metadata.csv"))

    # Metadatenkategorien
    categories = ["Domain", "Organism", "Organism part", "Diseases", "Modification", "Experiment Type", "Instrument", "Quantification", "Software"]

    # Accuracies von Model 1 und Model 2
    model_1 = [0.82, 0.41, 0.25, 0.59, 0.28, 0.56, 0.39, 0.44, 0.37]
    model_2 = [0.56, 0.28, 0.41, 0.37, 0.16, 0.47, 0.28, 0.22, 0.22]

    # Initialisiere meta_df als leeres DataFrame mit gleicher Zeilenanzahl
    meta_df = model1_df.copy()

    meta_df.drop(categories, axis = 1, inplace= True)

    # Choose better model per Category
    for i, category in enumerate(categories):
        acc1 = model_1[i]
        acc2 = model_2[i]
        if acc1 > acc2:
            meta_df[category] = model1_df[category]
            meta_df[f"{category}_Accuracy"] = str(acc1) + " Accuracy (Model 1)"
        else:
            meta_df[category] = model2_df[category]
            meta_df[f"{category}_Accuracy"] = str(acc2) + " Accuracy (Model 2)"

    # Insert descriptive texts
    def optional_text(label, value):
        return f", {label} {value}" if pd.notna(value) and value != "Not available" else ""

    # Iterate through meta_df rows und erstelle die Textfelder
    project_titles =[]
    descriptions = []
    sample_protocols = []
    data_protocols = []
    keywords_list = []


    for idx, row in meta_df.iterrows():
        # Werte extrahieren
        organism = row.get("Organism", "unknown")
        organism_part = row.get("Organism part", None)
        disease = row.get("Diseases", None)
        experiment = row.get("Experiment Type", "unknown")
        instrument = row.get("Instrument", "unknown")
        software = row.get("Software", "unknown")
        quant = row.get("Quantification", "unknown")
        mod = row.get("Modification", "unknown")
        activation = row.get("Activation Method", "unknown") if "Activation Method" in row else "unknown"

        # Project Title
        project_title = f"Orphan Proteomics Data: {experiment} Analysis of {organism}"
        
        # Description
        desc = (
            f"This project presents orphan proteomics data with predicted metadata, generated through machine learning-based annotation. "
            f"The dataset focuses on {experiment} proteomics of {organism}"
            f"{optional_text('specifically in', organism_part)}"
            f"{optional_text('associated with', disease)}. "
            f"The data was acquired using {instrument} and analyzed with {software}. "
            f"Predicted metadata includes {quant}, {mod}, Precursor Mass Tolerance, and Fragment Mass Tolerance. "
            f"Please note that these annotations are not manually curated and should be interpreted with caution."
        )
        
        # Sample Processing Protocol
        sample = (
            f"Samples were processed using {experiment}-based workflows, including {activation} fragmentation."
        )

        # Data Processing Protocol
        data = (
            f"Raw data was analyzed using {software}, applying {activation} for fragmentation. "
            f"{quant} was used for data analysis when applicable."
        )

        # Keywords
        keywords = [experiment, organism]
        if pd.notna(organism_part) and organism_part != "Not available":
            keywords.append(organism_part)
        if pd.notna(disease) and disease != "Not available":
            keywords.append(disease)
        keywords += [instrument, software, activation, mod, "orphan proteomics", "predicted metadata"]
        keywords_str = ", ".join([kw for kw in keywords if pd.notna(kw) and kw != "Not available"])

        # Append to lists
        descriptions.append(desc)
        sample_protocols.append(sample)
        data_protocols.append(data)
        keywords_list.append(keywords_str)
        project_titles.append(project_title)

    # Füge Spalten zum DataFrame hinzu
    meta_df["Project Title"] = project_titles
    meta_df["Description"] = descriptions
    meta_df["Sample Processing Protocol"] = sample_protocols
    meta_df["Data Processing Protocol"] = data_protocols
    meta_df["Keywords"] = keywords_list

    # Speichern mit den Textfeldern
    meta_df.to_csv(os.path.join(output_dir, f"metadata_result.csv"), index=False)

    # Optional anzeigen
    meta_df[["Description", "Sample Processing Protocol", "Data Processing Protocol", "Keywords"]].head()


    meta_df.to_csv(os.path.join(output_dir, f"metadata_result.csv"), index = False)