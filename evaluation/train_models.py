import os
import sys
import json

print("[*] Starting training script...")
# Core imports
import pandas as pd
import numpy as np
import joblib

# These can be slow or hang on some systems, so we'll import them inside the function with tracking
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, GroupShuffleSplit
# from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
# from sklearn.svm import SVC
# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import LabelEncoder, StandardScaler
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
# import xgboost as xgb

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from sklearn.base import BaseEstimator, TransformerMixin

class SparseToDense(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if hasattr(X, "toarray"):
            return X.toarray()
        return X

def train_and_evaluate():
    """Expert-grade training pipeline with 5-Fold Cross Validation."""
    print("[*] Importing ML libraries...")
    try:
        from sklearn.model_selection import train_test_split, StratifiedKFold
        from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, ConfusionMatrixDisplay
        from sklearn.utils import resample
        import matplotlib.pyplot as plt
        import xgboost as xgb
        XGB_AVAILABLE = True
    except Exception as e:
        print(f"[!] Error during library import: {e}")
        return

    dataset_path = os.path.join(config.METADATA_DIR, "ml_dataset.csv")
    if not os.path.exists(dataset_path):
        print(f"[-] Dataset not found at {dataset_path}")
        return

    print("[*] Loading dataset...")
    df = pd.read_csv(dataset_path).fillna(0)

    # 1. Expert-level Data Balancing (Cap at 100k per spec)
    print(f"[*] Enforcing class sample cap of {config.MAJORITY_CLASS_LIMIT}...")
    balanced_df = []
    for smell_type in df["smell_type"].unique():
        class_df = df[df["smell_type"] == smell_type]
        if len(class_df) > config.MAJORITY_CLASS_LIMIT:
            print(f"    -> Downsampling '{smell_type}' from {len(class_df)} to {config.MAJORITY_CLASS_LIMIT}")
            class_df = resample(class_df, replace=False, n_samples=config.MAJORITY_CLASS_LIMIT, random_state=config.RANDOM_SEED)
        balanced_df.append(class_df)
    df = pd.concat(balanced_df).sample(frac=1, random_state=config.RANDOM_SEED).reset_index(drop=True)

    # 2. Fast Training Mode (Subset)
    if config.DEBUG_MODE:
        print(f"[*] DEBUG MODE: Training on subset of {config.DEBUG_SUBSET_SIZE} samples.")
        df = df.sample(n=min(len(df), config.DEBUG_SUBSET_SIZE), random_state=config.RANDOM_SEED)

    print("[*] Final Class distribution:")
    print(df["smell_type"].value_counts())
    
    # Drop extremely rare classes
    class_counts = df["smell_type"].value_counts()
    rare_classes = class_counts[class_counts < 5].index
    if len(rare_classes) > 0:
        df = df[~df["smell_type"].isin(rare_classes)]

    X = df.drop(["file_path", "smell_type", "severity"], axis=1)
    y = df["smell_type"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    joblib.dump(le, os.path.join(config.MODELS_DIR, "label_encoder.pkl"))

    # Initial Split for hold-out test set (15%)
    X_train_cv, X_test, y_train_cv, y_test = train_test_split(
        X, y_encoded, test_size=0.15, random_state=config.RANDOM_SEED, stratify=y_encoded
    )

    print(f"[*] Data split: Train_CV={X_train_cv.shape[0]}, Test={X_test.shape[0]}")

    # Preprocessing
    numeric_features = [col for col in X.columns if col != "code_snippet"]
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('text', TfidfVectorizer(max_features=1000, ngram_range=(1, 2)), "code_snippet")
        ],
        sparse_threshold=0
    )
    
    # 3. K-Fold Cross Validation (k=5 per expert specification)
    print("\n[*] Starting 5-Fold Cross Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_SEED)
    
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, class_weight='balanced', n_jobs=-1, random_state=config.RANDOM_SEED),
        "XGBoost": xgb.XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=6, tree_method='hist', n_jobs=-1, eval_metric='mlogloss', early_stopping_rounds=20) if XGB_AVAILABLE else None
    }
    
    best_total_f1 = 0
    final_pipeline = None
    cv_reports = {}

    for name, clf in models.items():
        if clf is None: continue
        print(f"\n[*] Evaluating {name} via K-Fold...")
        fold_scores = []
        
        for i, (train_idx, val_idx) in enumerate(skf.split(X_train_cv, y_train_cv), 1):
            X_fold_train, X_fold_val = X_train_cv.iloc[train_idx], X_train_cv.iloc[val_idx]
            y_fold_train, y_fold_val = y_train_cv[train_idx], y_train_cv[val_idx]
            
            pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', clf)])
            
            if name == "XGBoost":
                # Handle early stopping in XGBoost during fold
                X_tr_proc = preprocessor.fit_transform(X_fold_train)
                X_val_proc = preprocessor.transform(X_fold_val)
                clf.fit(X_tr_proc, y_fold_train, eval_set=[(X_val_proc, y_fold_val)], verbose=False)
            else:
                pipeline.fit(X_fold_train, y_fold_train)
            
            # Score fold
            y_val_pred = pipeline.predict(X_fold_val)
            f1 = f1_score(y_fold_val, y_val_pred, average='weighted')
            fold_scores.append(f1)
            print(f"    Fold {i}: F1={f1:.4f}")
            
        avg_f1 = np.mean(fold_scores)
        print(f"[*] {name} Average F1: {avg_f1:.4f}")
        cv_reports[name] = {"CV_Avg_F1": avg_f1}

        if avg_f1 > best_total_f1:
            best_total_f1 = avg_f1
            # Final fit on all CV data
            print(f"[+] Re-fitting best model {name} on full CV set...")
            final_pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', clf)])
            final_pipeline.fit(X_train_cv, y_train_cv)
            best_name = name

    # 4. Final Hold-out Evaluation
    print(f"\n[*] Final Evaluation on Hold-out Test Set ({best_name})...")
    if final_pipeline is not None:
        y_test_pred = final_pipeline.predict(X_test)
        y_test_prob = final_pipeline.predict_proba(X_test)
    else:
        print("[!] No model was successfully trained. Exiting evaluation.")
        return
    
    final_metrics = {
        "Accuracy": accuracy_score(y_test, y_test_pred),
        "F1_Weighted": f1_score(y_test, y_test_pred, average='weighted'),
        "ROC_AUC": roc_auc_score(y_test, y_test_prob, multi_class='ovr') if len(le.classes_) > 2 else 0
    }
    
    for k, v in final_metrics.items():
        print(f"    -> {k}: {v:.4f}")

    # Save Best Model
    joblib.dump(final_pipeline, os.path.join(config.MODELS_DIR, "python_code_smell_model.pkl"))

    # Confusion Matrix
    print("[*] Saving Confusion Matrix...")
    plt.figure(figsize=(12, 10))
    ConfusionMatrixDisplay.from_predictions(y_test, y_test_pred, display_labels=le.classes_, cmap='Blues', xticks_rotation=45)
    plt.title(f'Confusion Matrix - {best_name}')
    plt.savefig(os.path.join(config.REPORTS_DIR, "confusion_matrix.png"))
    plt.close()

    print(f"[*] Comparison report saved to {config.REPORTS_DIR}/evaluation_metrics.json")
    with open(os.path.join(config.REPORTS_DIR, "evaluation_metrics.json"), 'w') as f:
        json.dump(final_metrics, f, indent=4)

if __name__ == "__main__":
    train_and_evaluate()

if __name__ == "__main__":
    train_and_evaluate()
