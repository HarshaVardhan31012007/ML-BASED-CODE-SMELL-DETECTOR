# Documentation for `dataset_assembler.py`

## Overview
`dataset_assembler.py` handles Phase 3: Dataset Assembly. It bridges the gap between the labeled code snippets (from Phase 2) and the numerical features (from the AST parser), creating the final `ml_dataset.csv` required for model training.

## Line-by-Line / Section Analysis

### 7-11: `assemble_dataset()` Overview
- This is the main function that reads the JSON labels and produces a tabular (CSV) dataset.

### 23-27: Loading Labels
- **Line 24-25:** Reads `labeled_dataset.json`. This file contains the results of the rule-based labeling and Bandit scans.

### 33-48: `zero_features` Fallback
- Defines a default dictionary where all feature counts are 0 and Maintainability Index is 100. This is used as a fallback if a specific code snippet fails to parse during the assembly phase.

### 50-75: The Assembly Loop
- **Line 52:** Resolves the absolute path to the source file for the current record.
- **Line 56:** Calls `extract_features_from_file` (from `ast_parser.py`) to generate the numerical vector for that file.
- **Lines 59-65:** Creates a `combined_record` that includes both metadata (filename, snippet, label) and the raw AST features.
- **Line 68:** Merges the dictionaries using `.update()`.

### 82-94: CSV Generation
- **Line 83:** Converts the list of combined records into a Pandas DataFrame.
- **Lines 86-87:** Ensures any null values in numeric columns are filled with 0 to prevent ML training errors.
- **Line 90:** Exports the final dataset to `metadata/ml_dataset.csv`.

### 97-98: Final Summary
- Prints the distribution of classes (smell types) to help the developer identify class imbalances (e.g., too many "Clean" samples vs. "SQL Injection").

## Key Functions

### `assemble_dataset`
The data-joining engine that converts unstructured code labels into a structured machine-learning-ready spreadsheet.
