# Documentation for `pipeline.py`

## Overview
`pipeline.py` is the central orchestrator of the Static Analysis engine. It integrates the ML model, the feature extractor, the security scanner, and the SHAP explainer into a unified `CodeSmellCompilerModule`.

## Line-by-Line / Section Analysis

### 16-25: `CodeSmellCompilerModule.__init__`
- Sets the path to the trained ML model (`python_code_smell_model.pkl`).
- Initializes internal state variables for the `model`, `explainer` (SHAP), and `le` (Label Encoder).
- Triggers `load_artifacts()`.

### 27-48: `load_artifacts()`
- **Line 32:** Uses `joblib.load` to bring the trained SKLearn pipeline into memory.
- **Line 37:** Loads the label encoder (which maps numbers like 0, 1, 2 back to names like "SQL_INJECTION").
- **Line 40:** Initializes the `SHAPExplainer` using the loaded model.

### 50-113: `predict_smells(filepath)`
- **Line 56:** Calls `extract_features_from_file` to get the numerical profile of the code.
- **Line 61:** Wraps features in a Pandas DataFrame (as the ML model expects tabular data).
- **Line 68:** Runs `model.predict()` to get the most likely code smell class.
- **Line 70:** Extracts the probability of that class to determine "Confidence".
- **Lines 74-83:** Uses the label encoder to translate the numeric prediction into a human-readable string.
- **Line 97:** Triggers the SHAP engine to generate a "Contribution Analysis" plot.
- **Lines 101-111:** If the prediction is not "Clean", it constructs a result object containing the smell type, severity, and the SHAP explanation image.

### 115-148: `analyze(target_path)`
- The primary method called by CLI or Web UI.
- **Line 129:** Executes the ML-based prediction.
- **Line 135:** Executes the rule-based security scan (from `scanner.py`).
- **Line 147:** Prints a summary of findings to the console.

### 163-172: `main()`
- Allows the pipeline to be run directly from the terminal with a file path as an argument.

## Key Functions

### `CodeSmellCompilerModule.analyze`
The main entry point for analysis. It performs both modern (ML) and classic (Rule-based) detection and returns a consolidated report.

### `predict_smells`
Handles the interaction between the source code, the feature extractor, the ML model, and the SHAP explainability engine.
