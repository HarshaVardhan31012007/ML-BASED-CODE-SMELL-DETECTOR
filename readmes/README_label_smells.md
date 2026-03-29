# Documentation for `label_smells.py`

## Overview
`label_smells.py` is the core labeling engine. It uses Abstract Syntax Tree (AST) traversal, Regex patterns, and the Bandit security linter to automatically identify 13 types of code smells in the dataset, creating the "ground truth" labels for ML training.

## Line-by-Line / Section Analysis

### 19-38: Class `DeadCodeVisitor(ast.NodeVisitor)`
- **Lines 24-26:** Records all function definitions in a module.
- **Lines 28-37:** Records all names/attributes used in the code.
- This comparison allows identifying functions that are defined but never called.

### 39-182: Class `RuleBasedLabeler(ast.NodeVisitor)`
- This is the primary AST-based engine for finding structural smells.
- **Lines 49-56:** `visit_FunctionDef` checks method length (Long Method).
- **Lines 58-68:** Hashes the AST structure of methods to find identical logic (Duplicate Code).
- **Lines 70-84:** Checks routes (detected by `@route` decorators) for authentication guards (Missing Auth).
- **Lines 90-99:** `visit_ClassDef` counts methods in a class (God Class).
- **Lines 102-112:** `visit_Try` checks for empty `pass` handlers (Improper Error Handling).
- **Lines 114-169:** `visit_Call` checks for dangerous sinks (SQL injection, unsafe file permissions, `eval`).

### 183-217: `run_bandit(filepath)`
- Executes the `bandit` security linter as an external process.
- **Lines 202-214:** Parses Bandit's JSON output and maps its findings to our internal `SMELL_CATEGORIES`.

### 219-234: `scan_for_magic_values(source_code)`
- Uses Regex to find hardcoded literals (strings/numbers) used directly in assignments or logic instead of being defined as constants.

### 236-334: `label_file(filepath)`
- The main worker function for a single file.
- **Line 249-252:** Adds `parent_node` references to the AST to allow upward traversal (needed for nesting depth calculation).
- **Lines 256-279:** Calculates the maximum nesting depth of control structures (Deep Nesting).
- **Lines 301-332:** Compiles all findings.
  - If smells are found, it extracts a code snippet (line +/- 5 lines) for each.
  - If no smells are found, it labels the first 10 lines as "CLEAN".

### 338-366: `main()` and Entry Point
- Uses `multiprocessing.Pool` (Line 353) to parallelize labeling across all CPU cores, significantly speeding up the processing of thousands of files.
- **Lines 360-361:** Saves the final labeled data to `labeled_dataset.json`.

## Key Functions

### `RuleBasedLabeler`
An AST visitor that implements specific search rules for most structural and security smells.

### `label_file`
Orchestrates multiple detection techniques (AST, Bandit, Regex) on a single file to produce training data records.
