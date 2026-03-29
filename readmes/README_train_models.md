# Documentation for `train_models.py` (Evaluation Module)

## Overview
Located in the `evaluation/` directory, this script implements a professional-grade training pipeline. It includes data balancing, 5-fold cross-validation, and an ensemble selection process to find the most accurate model for code smell detection.

## Line-by-Line / Section Analysis

### 30-36: `SparseToDense` Transformer
- A utility class used in the SKLearn pipeline to ensure that sparse matrices (produced by TF-IDF) are converted to dense arrays, which some models like XGBoost require in certain configurations.

### 38-55: Library Imports
- Uses a deferred import strategy inside the function. This prevents the script from hanging on startup if heavyweight libraries like `matplotlib` or `xgboost` are initialization-heavy.

### 65-74: Expert-level Data Balancing
- **Lines 69-72:** Implements **Downsampling**. If one class (like "Clean") has too many samples, it randomly selects only a subset (capped by `MAJORITY_CLASS_LIMIT`) to prevent the model from becoming biased towards the majority class.

### 93-95: Label Encoding
- Uses `LabelEncoder` to convert smell names (strings) into integers (0, 1, 2...). The encoder is saved as a `.pkl` file so it can be used for inverse transformation in the production pipeline.

### 105-112: Preprocessing Pipeline
- **Lines 108:** Applies `StandardScaler` to numeric features (complexity, node counts).
- **Line 109:** Applies `TfidfVectorizer` to the `code_snippet` text. This allows the model to "read" keywords like `eval` or `+` as additional signals.

### 115-154: 5-Fold Cross Validation
- **Line 116:** Splits the training data into 5 distinct "folds".
- **Lines 132-150:** Trains the model 5 separate times, each time using a different fold for validation. This provides a much more robust estimate of how the model will perform on unseen data.

### 164-180: Hold-out Evaluation
- After finding the best model via Cross-Validation, this section runs a final test on a 15% "hold-out" set that the model never saw during any part of the training or tuning. Reports Accuracy, F1, and ROC-AUC.

### 185-191: Visualization
- Generates a **Confusion Matrix** image and saves it to the `reports/` folder. This helps developers see which smells are being confused with others (e.g., "SQL Injection" being misclassified as "Missing Sanitization").

## Key Functions

### `train_and_evaluate`
The master function that executes the entire end-to-end ML lifecycle: preprocessing, balancing, validation, evaluation, and persistence.
