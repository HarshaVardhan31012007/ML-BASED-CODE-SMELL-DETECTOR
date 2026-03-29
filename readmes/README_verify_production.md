# Documentation for `verify_production.py`

## Overview
`verify_production.py` is a "Smoke Test" script designed to validate that the entire analysis pipeline is operational. It uses a hardcoded block of "vulnerable" code to ensure that both the ML predictions and the rule-based security scanners are triggering correctly.

## Line-by-Line / Section Analysis

### 8: Analyzer Import
- Imports the `CodeSmellCompilerModule` which is the same engine used by the Web UI and CLI.

### 20-88: `test_code` Definition
- Defines a Python string containing intentional code smells:
  - **SQL Injection:** `"SELECT ... " + data`
  - **Unsafe API:** `eval(data)`
  - **Magic Numbers:** `if data > 999:`
  - **Long Method:** A dummy function padded with over 50 `print` statements.

### 90-95: Analysis Execution
- **Line 91-92:** Writes the test code to a temporary file named `verify_test.py`.
- **Line 95:** Triggers `analyzer.analyze(temp_file)`.

### 97-112: Result Validation
- **Line 98:** Dumps the full JSON result to the console for inspection.
- **Lines 101-112:** Automated checks:
  - Verifies that `security_vulnerabilities` is not empty (checks if Bandit/Regex worked).
  - Verifies that `ml_predictions` is not empty (checks if the ML model is loaded and predicting).

### 114-116: Cleanup
- Uses a `finally` block to ensure `verify_test.py` is deleted even if the analysis crashes.

## Key Functions

### `verify()`
The primary test harness. It provides a quick way for developers to confirm that a "fresh" installation or a new model build is actually working in a real-world scenario.
