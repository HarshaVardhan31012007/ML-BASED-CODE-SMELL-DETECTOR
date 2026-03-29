# Documentation for `model_training.py` (Root)

## Overview
This script implements the `EnsembleCodeSmellClassifier`, a sophisticated model that combines XGBoost and Random Forest predictions. It emphasizes automated feature normalization and class balancing to achieving high accuracy in detecting rare code smells.

## Line-by-Line / Section Analysis

### 28-41: Class `EnsembleCodeSmellClassifier`
- **Line 31-38:** Initializes both an `XGBClassifier` and a `RandomForestClassifier`.
- **Line 31:** Uses parameters from `config.XGB_PARAMS` (L1/L2 regularization, hist method).
- **Line 35:** Uses `class_weight='balanced'` for the Random Forest to handle the fact that some code smells are rarer than others.

### 43-56: `_prepare_pipeline(X)`
- **Line 48:** Uses `SimpleImputer` to fill any missing values with the median.
- **Line 49:** Uses `StandardScaler` to normalize the data. This is essential for the model to treat all metrics (like AST node count vs Cyclomatic Complexity) on the same scale.

### 58-70: `train(X, y)`
- **Line 60:** Encodes the labels.
- **Line 63:** Triggers the preprocessing transform.
- **Lines 66-69:** Trains both sub-models on the exact same processed data.

### 71-76: `predict_proba(X)`
- **Line 76:** **Simple Majority Voting Ensemble.** It calculates the probabilities from both XGBoost and Random Forest and averages them. This typically produces a more robust prediction than any single model alone.

### 107-181: `run_training_pipeline()`
- **Line 122:** Filters out rare classes with fewer than 10 samples.
- **Lines 125-131:** Performs downsampling on the "Clean" class to maintain a balanced training set.
- **Lines 142-154:** Executes 5-Fold Cross Validation.
- **Line 174-178:** Automated Validation Check. It flag any code smells that did not meet the Project's success criteria (F1-score >= 80%).

## Key Functions

### `EnsembleCodeSmellClassifier`
The primary model architecture defined for the project, providing a robust, multi-model approach to classification.

### `run_training_pipeline`
The automation script that handles the end-to-end data cleansing, validation, and final production model training.
