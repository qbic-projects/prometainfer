import os
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

def ml_prediction(output_dir, feature_file):

    models = ["mlp_200_nokey", "mlp_400_nokey"]

    for model in models:
        feature_df = pd.read_csv(feature_file)
        filename_col = feature_df['Filename'].copy()
        software_col  = feature_df['software'].copy()
        activation_method = feature_df['activation_method'].copy()
        feature_pattern = pd.read_csv(f"models/{model}_train_features.csv")
        # Load model, preprocessor and label-encoders
        clf = joblib.load(f"models/{model}_model.pkl")
        preprocessor = joblib.load(f"models/{model}_preprocessor.pkl")
        label_encoders = joblib.load(f"models/{model}_label_encoders.pkl")
        ml_metrics = pd.read_csv(f"models/{model}_metrics.csv")

        # preprocess feature df
        new_fea_cols = feature_df.columns
        for col in feature_pattern.columns:
            if col not in new_fea_cols:
                if "avgevalhits" in col:
                    feature_df[col] = np.mean(feature_pattern[col])
                elif "counthits" in col:
                    feature_df[col] = np.mean(feature_pattern[col])
                elif "precursor" in col:
                    feature_df[col] = np.mean(feature_pattern[col])
            if col in new_fea_cols:
                if "avgevalhits" in col:
                    feature_df[col].fillna(np.mean(feature_pattern[col]))
                elif "counthits" in col:
                    feature_df[col].fillna(np.mean(feature_pattern[col]))
                elif "precursor" in col:
                    feature_df[col].fillna(np.mean(feature_pattern[col]))

        for fea_df_col in feature_df.columns:
            if fea_df_col not in feature_pattern.columns:
                feature_df = feature_df.drop(columns = [fea_df_col]).copy()
        
        # Sort feature_df as feature_pattern from training process
        feature_df = feature_df[feature_pattern.columns]

        X = feature_df.copy() 
        
        label_columns = ["Domain","Organism", "Organism part", "Diseases", "Modification", 
                 "Experiment Type", "Instrument", "Quantification", "Software"]
        
        # Apply preprocessing to X
        X_preprocessed = preprocessor.transform(X)
        y_pred = clf.predict(X_preprocessed)

        # Decode predictions
        y_pred_decoded = pd.DataFrame(y_pred, columns=label_columns)


        for i, col in enumerate(label_columns):
            y_pred_decoded[col] = label_encoders[col].inverse_transform(y_pred[:, i])

        ### Todo: only story one metadata.csv (w model for best accuracy per column)
        y_pred_decoded.insert(0, 'Filename', filename_col) 
        y_pred_decoded["Parsed Software"] = software_col
        y_pred_decoded["Activation Method"] = activation_method
        y_pred_decoded.to_csv(os.path.join(output_dir, f"{model}_predicted_metadata.csv"), index = False)
