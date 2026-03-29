import os
import pandas as pd
import numpy as np
import joblib
import json
import logging
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import xgboost as xgb
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

# Setup logging
logging.basicConfig(
    filename=os.path.join(config.REPORTS_DIR, 'training.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EnsembleCodeSmellClassifier:
    """Ensemble model combining XGBoost and Random Forest as per Section 10/13 requirements."""
    def __init__(self):
        self.xgb = xgb.XGBClassifier(**config.XGB_PARAMS)
        self.rf = RandomForestClassifier(
            n_estimators=500,
            max_depth=15,
            min_samples_leaf=2,  # Added to prevent overfitting on noisy snippets
            class_weight='balanced',
            n_jobs=-1,
            random_state=config.RANDOM_SEED
        )
        self.le = LabelEncoder()
        self.preprocessor = None
        self.classes_ = None

    def _prepare_pipeline(self, X):
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Section 10: Normalize/Scale features
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features)
            ])
        return self.preprocessor

    def train(self, X, y):
        """Train the ensemble on a given dataset."""
        y_encoded = self.le.fit_transform(y)
        self.classes_ = self.le.classes_
        
        X_processed = self._prepare_pipeline(X).fit_transform(X)
        
        logging.info("Training XGBoost...")
        self.xgb.fit(X_processed, y_encoded)
        
        logging.info("Training Random Forest...")
        self.rf.fit(X_processed, y_encoded)
        
    def predict_proba(self, X):
        X_processed = self.preprocessor.transform(X)
        p_xgb = self.xgb.predict_proba(X_processed)
        p_rf = self.rf.predict_proba(X_processed)
        # Weighted Ensemble: Random Forest was found to be much stronger (0.73 vs 0.67)
        return (0.2 * p_xgb + 0.8 * p_rf)

    def predict(self, X):
        proba = self.predict_proba(X)
        indices = np.argmax(proba, axis=1)
        return self.le.inverse_transform(indices)

def evaluate_model(model, X_test, y_test, suffix="test"):
    """Evaluate performance metrics."""
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_weighted": f1_score(y_test, y_pred, average='weighted'),
        "precision_weighted": precision_score(y_test, y_pred, average='weighted'),
        "recall_weighted": recall_score(y_test, y_pred, average='weighted')
    }
    
    # Per-class F1 (Target: > 80%)
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics["per_class"] = report
    
    # Save confusion matrix data
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\n[=] Evaluation Results ({suffix}):")
    print(f"    -> Accuracy: {metrics['accuracy']:.4f}")
    print(f"    -> F1 (Weighted): {metrics['f1_weighted']:.4f}")
    
    return metrics

def run_training_pipeline():
    """Whole training workflow with Cross-Validation and Ensemble."""
    print("[*] Starting Production ML Training Pipeline...")
    
    dataset_path = os.path.join(config.METADATA_DIR, "ml_dataset.csv")
    if not os.path.exists(dataset_path):
        print(f"[-] Dataset not found at {dataset_path}. Run assembler first.")
        return

    df = pd.read_csv(dataset_path)
    
    # 1. Data Cleaning & Handling Imbalance (Section 6/9)
    # Filter rare classes
    counts = df['smell_type'].value_counts()
    rare_classes = counts[counts < 10].index
    df = df[~df['smell_type'].isin(rare_classes)]
    
    # Downsample Majority Classes (e.g. Magic Strings or Clean)
    if config.MAJORITY_CLASS_LIMIT:
        balanced_dfs = []
        for smell in df['smell_type'].unique():
            subset = df[df['smell_type'] == smell]
            if len(subset) > config.MAJORITY_CLASS_LIMIT:
                balanced_dfs.append(subset.sample(config.MAJORITY_CLASS_LIMIT, random_state=config.RANDOM_SEED))
            else:
                balanced_dfs.append(subset)
        df = pd.concat(balanced_dfs, ignore_index=True)

    X = df.drop(columns=['file_path', 'code_snippet', 'smell_type', 'severity', 'line'])
    y = df['smell_type']

    # 2. Split (70% Train, 15% Val, 15% Test)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=config.RANDOM_SEED
    )

    # 2. Oversample Minority Classes (Fixes Extreme Imbalance)
    from imblearn.over_sampling import RandomOverSampler
    if hasattr(config, 'OVERSAMPLE_MINORITY') and config.OVERSAMPLE_MINORITY:
        print("[*] Applying RandomOverSampler to balance all classes...")
        ros = RandomOverSampler(random_state=config.RANDOM_SEED)
        X_train_val, y_train_val = ros.fit_resample(X_train_val, y_train_val)
        print(f"[+] Balanced training set size: {len(X_train_val)}")

    # 3. K-Fold Cross-Validation (k=5) - Tracking Macro F1
    print(f"[*] Starting 5-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_SEED)
    fold_metrics = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train_val, y_train_val), 1):
        X_t, X_v = X_train_val.iloc[train_idx], X_train_val.iloc[val_idx]
        y_t, y_v = y_train_val.iloc[train_idx], y_train_val.iloc[val_idx]
        
        model = EnsembleCodeSmellClassifier()
        model.train(X_t, y_t)
        
        y_pred = model.predict(X_v)
        acc = accuracy_score(y_v, y_pred)
        f1_macro = f1_score(y_v, y_pred, average='macro')
        print(f"[=] Fold {fold} Results: Accuracy {acc:.4f}, Macro F1 {f1_macro:.4f}")
        fold_metrics.append(f1_macro)

    # 4. Final Training & Persistence
    print("\n[*] Training final production ensemble on full set...")
    final_model = EnsembleCodeSmellClassifier()
    
    # Custom training loop to get individual scores
    y_encoded = final_model.le.fit_transform(y_train_val)
    final_model.classes_ = final_model.le.classes_
    X_processed = final_model._prepare_pipeline(X_train_val).fit_transform(X_train_val)
    X_test_proc = final_model.preprocessor.transform(X_test)
    y_test_encoded = final_model.le.transform(y_test)

    print("\n[*] Evaluating individual models vs Ensemble...")
    results = []
    
    # XGBoost
    final_model.xgb.fit(X_processed, y_encoded)
    xgb_pred = final_model.xgb.predict(X_test_proc)
    results.append({
        "Model": "XGBoost",
        "Acc": accuracy_score(y_test_encoded, xgb_pred),
        "F1": f1_score(y_test_encoded, xgb_pred, average='weighted'),
        "Prec": precision_score(y_test_encoded, xgb_pred, average='weighted'),
        "Rec": recall_score(y_test_encoded, xgb_pred, average='weighted')
    })
    
    # RandomForest
    final_model.rf.fit(X_processed, y_encoded)
    rf_pred = final_model.rf.predict(X_test_proc)
    results.append({
        "Model": "RandomForest",
        "Acc": accuracy_score(y_test_encoded, rf_pred),
        "F1": f1_score(y_test_encoded, rf_pred, average='weighted'),
        "Prec": precision_score(y_test_encoded, rf_pred, average='weighted'),
        "Rec": recall_score(y_test_encoded, rf_pred, average='weighted')
    })
    
    # Ensemble
    ens_pred = final_model.le.transform(final_model.predict(X_test))
    results.append({
        "Model": "Ensemble",
        "Acc": accuracy_score(y_test_encoded, ens_pred),
        "F1": f1_score(y_test_encoded, ens_pred, average='weighted'),
        "Prec": precision_score(y_test_encoded, ens_pred, average='weighted'),
        "Rec": recall_score(y_test_encoded, ens_pred, average='weighted')
    })

    # Print Table
    print(f"{'Model':<15} | {'Acc':<7} | {'F1':<7} | {'Prec':<7} | {'Rec':<7}")
    print("-" * 55)
    for r in results:
        print(f"{r['Model']:<15} | {r['Acc']:.4f}  | {r['F1']:.4f}  | {r['Prec']:.4f}  | {r['Rec']:.4f}")

    test_metrics = evaluate_model(final_model, X_test, y_test, suffix="Ensemble Hold-out Test")
    
    # Save the model (Ensuring compatibility with pipeline.py)
    model_path = os.path.join(config.MODELS_DIR, "python_code_smell_model.pkl")
    # We save a dictionary containing the model and the labels for easy loading
    joblib.dump(final_model, model_path)
    print(f"[+] Model saved to {model_path}")
    
    # Save the label encoder separately as well
    le_path = os.path.join(config.MODELS_DIR, "label_encoder.pkl")
    joblib.dump(final_model.le, le_path)
    
    # Save metrics report
    report_path = os.path.join(config.REPORTS_DIR, "final_metrics.json")
    with open(report_path, 'w') as f:
        # Convert classification report to string if it's too nested for simple JSON dump
        json.dump(test_metrics, f, indent=4, default=str)
        
    # Check Acceptance Criteria (Section 11)
    failed_smells = [s for s, m in test_metrics["per_class"].items() 
                     if isinstance(m, dict) and m.get('f1-score', 1.0) < 0.80 and s != 'accuracy']
    
    if failed_smells:
        print(f"[!] WARNING: The following smells did not meet F1 >= 80%: {failed_smells}")
    else:
        print(f"[+] SUCCESS: All smells met the F1 >= 80% criteria.")

if __name__ == "__main__":
    run_training_pipeline()
