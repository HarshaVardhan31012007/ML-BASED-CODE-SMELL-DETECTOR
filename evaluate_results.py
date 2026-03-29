import os
import sys
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb  # Required to load XGBoost-based pipelines
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import json
import config

def run_evaluation():
    print("[*] Loading Evaluation Script...")
    
    # Paths
    model_path = os.path.join(config.MODELS_DIR, "python_code_smell_model.pkl")
    le_path = os.path.join(config.MODELS_DIR, "label_encoder.pkl")
    dataset_path = os.path.join(config.METADATA_DIR, "ml_dataset.csv")
    
    if not os.path.exists(model_path):
        print(f"[!] Model not found at {model_path}. Please train the model first.")
        return
    if not os.path.exists(dataset_path):
        print(f"[!] Dataset not found at {dataset_path}.")
        return

    # Load Model and Encoder
    print("[*] Loading trained model and label encoder...")
    model_pipeline = joblib.load(model_path)
    le = joblib.load(le_path)
    
    # Load Dataset
    print("[*] Loading dataset for evaluation...")
    df = pd.read_csv(dataset_path).fillna(0)
    
    # Sample a manageable subset if it's very large for display purposes, 
    # but for accuracy we should use a decent amount.
    # We'll use 5000 samples for a quick but representative test.
    subset_size = 5000
    if len(df) > subset_size:
        print(f"[*] Sampling {subset_size} samples for demonstration...")
        df_eval = df.sample(n=subset_size, random_state=config.RANDOM_SEED)
    else:
        df_eval = df

    X = df_eval.drop(["file_path", "smell_type", "severity"], axis=1)
    y_true_labels = df_eval["smell_type"]
    y_true = le.transform(y_true_labels)

    # Predict
    print("[*] Running predictions...")
    y_pred = model_pipeline.predict(X)
    
    # Calculate Metrics
    print("\n" + "="*50)
    print("      CODE SMELL DETECTION EVALUATION RESULTS")
    print("="*50)
    
    accuracy = accuracy_score(y_true, y_pred)
    precision_weighted = precision_score(y_true, y_pred, average='weighted')
    recall_weighted = recall_score(y_true, y_pred, average='weighted')
    f1_weighted = f1_score(y_true, y_pred, average='weighted')
    
    print(f"Overall Accuracy:  {accuracy:.4f}")
    print(f"Precision (W):     {precision_weighted:.4f}")
    print(f"Recall (W):        {recall_weighted:.4f}")
    print(f"F1-Score (W):      {f1_weighted:.4f}")
    print("-" * 50)
    
    print("\nDetailed Per-Class Classification Report:")
    report = classification_report(y_true, y_pred, target_names=le.classes_)
    print(report)
    
    # Explanation of metrics
    print("-" * 50)
    print("METRIC EXPLANATIONS:")
    print("- Accuracy:  Percentage of correct predictions overall.")
    print("- Precision: How many 'detected' smells were actually smells (avoids false alarms).")
    print("- Recall:    How many 'actual' smells were correctly detected (avoids missing issues).")
    print("- F1-Score:  Harmonic mean of Precision and Recall (balanced view).")
    print("="*50)

    # Save results to a report
    results = {
        "accuracy": accuracy,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_weighted": f1_weighted,
        "per_class_report": classification_report(y_true, y_pred, target_names=le.classes_, output_dict=True)
    }
    
    report_output_path = os.path.join(config.REPORTS_DIR, "demonstration_metrics.json")
    with open(report_output_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\n[+] Detailed report saved to {report_output_path}")

if __name__ == "__main__":
    run_evaluation()
