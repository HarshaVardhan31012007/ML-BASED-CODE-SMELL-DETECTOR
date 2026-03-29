# Documentation for `config.py`

## Overview
`config.py` is the central configuration hub for the "ML-Driven Code Smell Detection Compiler". It defines directory structures, the taxonomy of code smells, training parameters, and external data sources.

## Line-by-Line / Section Analysis

### 1-10: Directory Setup
- **Line 1:** Imports `os` for path manipulations.
- **Line 4:** `BASE_DIR` dynamically captures the root directory of the project.
- **Lines 5-10:** Defines constant paths for datasets, repositories, ML models, and reports. This ensures consistency across all scripts.

### 13-32: Data Sources (`REPOSITORIES`)
- **REPOSITORIES:** A list of GitHub URLs containing both vulnerable and production-grade code. This list is used by `clone_and_extract.py` to build the initial raw dataset.

### 35-55: Code Smell Taxonomy (`SMELL_CATEGORIES`)
- Defines the 13 specific types of code smells the system identifies, split into:
  - **Security-Critical:** SQL Injection, Hard-Coded Credentials, etc.
  - **Structural:** Long Method, Deep Nesting, Magic Values, etc.
- **Line 54:** "CLEAN" acts as the negative class for the ML model.

### 58-62: Filtering (`IGNORE_PATHS`)
- Lists folder names (like `venv`, `tests`, `.git`) that should be skipped during file extraction to maintain a high-quality dataset.

### 65-84: ML Training Configuration
- **RANDOM_SEED (42):** Ensures that data splitting and model training results are reproducible.
- **DEBUG_MODE / SUBSET_SIZE:** Allows developers to run the pipeline on a small subset (e.g., 20k samples) for faster testing.
- **XGB_PARAMS:** Hyperparameters for the XGBoost classifier, including tree depth, learning rate, and L1/L2 regularization to prevent overfitting.

### 87-88: File System Initialization
- **Lines 87-88:** Iterates through all defined directory paths and creates them if they don't exist, preventing "File Not Found" errors during first-run.

## Key Functions
- No functions are defined here as this is a flat configuration file designed to be imported as a module (`import config`).
