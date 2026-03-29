import os
import sys
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
import config

def evaluate_file(file_path):
    print(f"[*] Evaluating Model on: {file_path}")
    
    # 1. Load Model and labels
    model_path = os.path.join(config.MODELS_DIR, "python_code_smell_model.pkl")
    le_path = os.path.join(config.MODELS_DIR, "label_encoder.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(le_path):
        print("[!] Model or Label Encoder not found. Please train first.")
        return

    model = joblib.load(model_path)
    le = joblib.load(le_path)

    # 2. Extract Features (Simplified for this demonstration)
    # Note: In a real scenario, we'd use the same extractor used for training.
    # For now, we'll try to find this file's features in the existing ml_dataset.csv
    # if it's already part of the dataset.
    dataset_path = os.path.join(config.METADATA_DIR, "ml_dataset.csv")
    df = pd.read_csv(dataset_path)
    
    # Match the file (using the relative path from the dataset root)
    rel_path = os.path.relpath(file_path, config.BASE_DIR)
    # The dataset might have different path formats, let's try a fuzzy match
    match = df[df['file_path'].str.contains(os.path.basename(file_path), na=False)]
    
    if match.empty:
        print(f"[!] File {file_path} not found in the training dataset's features.")
        print("    (Feature extraction for new files requires running the assembler again)")
        return

    print(f"[+] Found {len(match)} code snippets in this file from the dataset.")
    
    X = match.drop(["file_path", "smell_type", "severity"], axis=1)
    y_true = match["smell_type"]
    
    # 3. Predict
    y_pred_encoded = model.predict(X)
    # The pipeline already returns labels if it's a Pipeline
    # If it's a raw classifier, we'd need le.inverse_transform
    # Based on evaluate_results.py, model.predict(X) works correctly.
    
    print("\n[=] RESULTS FOR THIS FILE:")
    results_df = pd.DataFrame({
        'Line': match['line'] if 'line' in match.columns else ['N/A'] * len(match),
        'Actual Smell': y_true.values,
        'Predicted Smell': y_pred_encoded
    })
    print(results_df.to_string(index=False))
    
    # Calculate local "accuracy" for this file
    if len(results_df) > 0:
        correct = (results_df['Actual Smell'] == results_df['Predicted Smell']).sum()
        total = len(results_df)
        accuracy = correct / total
        print(f"\n[+] File-specific Accuracy: {accuracy:.2%} ({correct}/{total})")
    else:
        print("\n[!] No snippets to evaluate.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluate_single_file.py <path_to_python_file>")
    else:
        evaluate_file(sys.argv[1])
