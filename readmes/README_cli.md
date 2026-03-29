# Documentation for `cli.py`

## Overview
`cli.py` is the power-user interface. It provides a command-line tool for bulk analysis of local directories and files, using Python's `multiprocessing` to handle large codebases efficiently.

## Line-by-Line / Section Analysis

### 7-19: Root Path Configuration
- Ensures the CLI can find the `config.py` and `static_analyzer` modules.

### 21-26: `list_smells()`
- Prints a clean list of all smell categories defined in the project configuration.

### 28-31: `analyze_file(filepath)`
- A simple wrapper function. Each worker process in the multiprocessing pool will execute this function to analyze a single file.

### 33-85: `main()` (CLI Router)
- **Line 34-45:** Sets up `argparse`. defines commands: `analyze` (with a `--recursive` flag) and `list-smells`.
- **Lines 48-53:** Logic for analyzing a single file.
- **Lines 54-80:** Logic for analyzing a directory.
  - **Lines 56-63:** Walks the directory (optionally recursively) to find all `.py` files.
  - **Line 73-74:** **Parallel Processing:** Initializes a `multiprocessing.Pool` with a process count matching the machine's CPU cores. It then maps the `analyze_file` function across all collected files. This is significantly faster than sequential processing.
  - **Lines 76-77:** Reports the total time taken and the average performance per file.

## Key Functions

### `main`
Handles argument parsing and orchestrates both single-file and multi-file (parallel) analysis.

### `analyze_file`
The unit of work for parallel execution, isolating the analysis of one file into its own process.
