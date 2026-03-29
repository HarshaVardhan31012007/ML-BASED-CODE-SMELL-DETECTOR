# Documentation for `clone_and_extract.py`

## Overview
`clone_and_extract.py` is the first step in the data pipeline (Phase 1). It automates the collection of source code from a curated list of GitHub repositories, filters out irrelevant files, and flattens the directory structure for easier processing.

## Line-by-Line / Section Analysis

### 1-10: Imports and Path setup
- **Lines 1-6:** Imports `shutil` for file copying, `subprocess` for git commands, and `urlparse` for parsing repository links.
- **Line 9-10:** Adds the root directory to the system path to import the global `config` module.

### 13-30: `clone_repository(repo_url, target_dir)`
- **Line 15:** Extracts the repository name from the URL.
- **Lines 17-20:** Skips cloning if the repository already exists locally.
- **Line 25:** Executes `git clone --depth 1`. The `--depth 1` (shallow clone) is critical as we only need the latest code snapshot, not the entire history.

### 32-37: `should_ignore(path_parts)`
- Iterates through path components and checks if any match the `IGNORE_PATHS` defined in `config.py` (e.g., `tests`, `docs`). This ensures the dataset contains actual production logic.

### 40-83: `extract_python_files(repo_path, output_dir)`
- **Line 47:** Uses `os.walk` to traverse the cloned repository.
- **Lines 55-57:** Modifies `dirs` in-place (via `clear/extend`) to skip hidden directories like `.git`.
- **Line 60:** Filters for `.py` files.
- **Lines 62-63:** Specifically excludes `__init__.py` and `setup.py` as they rarely contain domain-specific code smells.
- **Lines 67-72:** Constructs a unique, flat filename by joining the original path parts with underscores (e.g., `flask_src_app.py`). This prevents filename collisions when merging multiple repositories.
- **Line 77:** Copies the file to the central `python_code` directory.

### 85-104: `main()` and Entry Point
- **Line 89:** Loops through the repository list in `config.py`.
- **Lines 90-93:** Orchestrates the clone -> extract flow for each repository.
- **Line 100:** Reports the total number of files successfully extracted.

## Key Functions

### `clone_repository`
Clones target repositories efficiently using shallow cloning.

### `extract_python_files`
The core logic for traversing a repository, applying filters, and producing a flat, unique dataset of Python source files.
