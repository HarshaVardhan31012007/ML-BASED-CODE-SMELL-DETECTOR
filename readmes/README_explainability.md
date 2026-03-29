# Documentation for `explainability.py`

## Overview
`explainability.py` implements Model Explainability using SHAP (SHapley Additive exPlanations). It provides insights into *why* the ML model predicted a specific code smell by visualizing the most influential features.

## Line-by-Line / Section Analysis

### 1-8: Imports
- **Lines 2-6:** Imports standard ML libraries (`joblib`, `pandas`, `numpy`) and the `shap` library.
- **Lines 7-8:** `BytesIO` and `base64` are used to convert graphical plots into a format that can be sent to the web UI.

### 10-23: Class `SHAPExplainer.__init__`
- **Line 11:** Accepts the trained `pipeline` object.
- **Line 20:** Extracts the specific `classifier` step from the SKLearn pipeline (as SHAP's TreeExplainer needs the model object directly).
- **Line 21:** Initializes the `shap.TreeExplainer`.

### 25-87: Method `explain_prediction`
- **Line 25:** Accepts a DataFrame `df` representing the features of a single code snippet.
- **Line 33:** Transforms the input using the pipeline's preprocessor (one-hot encoding, scaling, etc.) to match the format the model saw during training.
- **Lines 36-41:** Calculates SHAP values. It handles both older `shap_values()` calls and the newer callable SHAP API.
- **Lines 49-63:** Prepares the plot data. It specifically extracts the values for the predicted class index (`pred_idx`).
- **Lines 66-70:** Attempts to get human-readable feature names (e.g., "cyclomatic_complexity") from the preprocessor.
- **Lines 72-78:** Ranks features by importance and selects the top 10 for a horizontal bar chart.
- **Lines 81-84:** Saves the `matplotlib` figure to a buffer, encodes it in Base64, and returns a string starting with the image data.

## Key Functions

### `SHAPExplainer.__init__(self, pipeline)`
Initializes the SHAP engine. It must extract the raw classifier from the pipeline to work with tree-based explainers.

### `explain_prediction(self, df)`
The core logic. It:
1. Preprocesses the data.
2. Computes feature contributions.
3. Generates a "Contribution Analysis" bar chart.
4. Returns the chart as a Base64 string for the frontend.
