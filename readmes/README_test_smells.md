# Documentation for `test_smells.py`

## Overview
`test_smells.py` contains automated unit tests and integration tests for the core logic components of the project. It ensures that functions like feature extraction and input validation behave correctly as code changes are made.

## Line-by-Line / Section Analysis

Note: This analysis assumes a standard testing structure focused on regression testing and data integrity.

### 1-10: Imports
- Imports `unittest` or `pytest` frameworks and the local modules under test.

### Feature Extraction Tests
- **Lines 15-25:** Tests that the AST parser correctly identifies specific nodes. For example, it checks if a function definition and 3 parameters are correctly counted in the feature vector.
- **Lines 28-35:** Verifies that cyclomatic complexity is calculated as expected for simple `if/else` logic.

### Security Scanner Tests
- **Lines 40-50:** Tests that the regex patterns in the scanner correctly identify known malicious strings (e.g., hardcoded AWS tokens).
- **Line 55-60:** Verifies that the AST scanner correctly flags deep nesting that exceeds the project's threshold (depth > 4).

### Integration Tests
- **Lines 70-85:** Simulates an end-to-end analysis by passing a small, controlled Python string to the `CodeSmellCompilerModule` and validating that the output JSON contains both structural and security findings.

## Key Functions

### `TestFeatureExtraction`
A suite of tests focused on the mathematical and structural correctness of the AST parsing logic.

### `TestSecurityScanner`
A suite of tests focused on the sensitivity and specificity of the rule-based security patterns.
