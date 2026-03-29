# Documentation for `data_processing.py`

## Overview
`data_processing.py` handles Phase 2 of the pipeline: Data Validation and Deduplication. It ensures that the collected Python files are syntactically correct and removes identical files that may have been present in different repositories.

## Line-by-Line / Section Analysis

### 1-10: Imports and Path setup
- **Line 2:** Imports `ast` (Abstract Syntax Trees) for syntax validation.
- **Line 3:** Imports `hashlib` for calculating file fingerprints.
- **Line 4:** Imports `logging` to track corrupted files.

### 13-17: Logging Configuration
- Sets up a log file in the `reports/` directory to record details about files that fail AST parsing.

### 19-29: `get_file_hash(filepath)`
- **Line 21:** Initializes an MD5 hasher.
- **Line 23-25:** Reads the file in binary mode (`rb`) and updates the hash.
- **Line 26:** Returns the hex digest. This string serves as a unique "fingerprint" for the file content.

### 31-40: `validate_ast(filepath)`
- **Line 35:** Reads the file content.
- **Line 36:** Executes `ast.parse(source)`. If the file contains a syntax error, this will raise an exception.
- **Line 37-40:** Returns `True` if valid, otherwise logs the error and returns `False`.

### 42-89: `process_dataset()`
- **Line 50:** Lists all `.py` files in the extraction directory.
- **Line 53:** `seen_hashes` is a set used to track unique fingerprints.
- **Line 67-70:** Calls `validate_ast`. If a file is corrupted (e.g., truncated download or invalid Python version), it is deleted.
- **Line 73-77:** Calls `get_file_hash`. If the hash is already in `seen_hashes`, the file is a duplicate and is deleted.
- **Line 79-80:** If unique and valid, adds the hash to the set and increments the `valid_count`.
- **Lines 82-86:** Outputs a summary of how many files were kept, rejected, or deduplicated.

## Key Functions

### `get_file_hash`
Generates a unique MD5 signature for identifying duplicate source files.

### `validate_ast`
Uses the standard Python `ast` module to ensure that every file in the dataset is a valid, parsable Python script.

### `process_dataset`
The main controller that iterates through the raw dataset and applies cleaning and deduplication rules.
