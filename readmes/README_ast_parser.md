# Documentation for `ast_parser.py`

## Overview
`ast_parser.py` is responsible for converting raw Python source code into a numerical feature vector that the ML model can understand. It calculates complexity metrics, counts structural elements, and computes advanced software engineering metrics like Halstead and the Maintainability Index.

## Line-by-Line / Section Analysis

### 5-51: Class `CodeSmellFeatureExtractor.__init__`
- **Lines 7-45:** Initializes a comprehensive dictionary of features (38+ features), including counts for functions, classes, loops, conditionals, imports, etc.
- **Lines 41-44:** Placeholders for Halstead and Maintainability Index metrics.
- **Lines 49-50:** Defines lists of "dangerous APIs" and "sensitive keywords" for security-related feature counts.

### 56-89: `visit_FunctionDef`
- Increments the function count and adds the parameters count to the global tally.
- **Line 59:** Increments Cyclomatic Complexity (starts at 1 per function).
- **Lines 63-65:** Tracks function lengths to calculate averages and maximums.
- **Lines 67-83:** Heuristic check for unauthenticated web routes by looking for decorators like `@route` without corresponding `@login_required` or similar.

### 93-120: `visit_Call`
- **Lines 104-105:** Checks if the function called is in the `dangerous_apis` set (e.g., `eval`, `exec`).
- **Lines 108-110:** Tallies dynamic file `open()` calls where the filename is not a constant string.
- **Lines 113-118:** Looks for string concatenation within database `execute()` calls (a classic SQL injection signature).

### 122-130: `visit_Constant`
- Tallies literal values and checks if they contain sensitive strings like "password" or "api_key".

### 132-144: `visit_Try`
- Tallies try-except blocks.
- **Lines 135-138:** Specifically flags "except: pass" or "except: return" as indicators of poor error handling.

### 194-206: `visit_Assign`
- Tracks variable assignments and checks variable names against the `sensitive_keywords` list.

### 254-315: `calculate_halstead(source_code)`
- Implements the mathematical formulas for Halstead Metrics.
- **Lines 269-282:** Counts the number of unique operators (`n1`), unique operands (`n2`), total operators (`N1`), and total operands (`N2`).
- **Line 293:** Calculates **Volume** (Size of software representation).
- **Line 294:** Calculates **Difficulty** (Error proneness).
- **Lines 305-306:** Calculates the **Maintainability Index (MI)**, a complex metric combining Volume, Complexity, and Lines of Code into a 0-100 score.

## Key Functions

### `extract_features_from_code(source_code)`
The high-level entry point. It parses the code, runs the visitor to collect raw counts, and then triggers the Halstead/MI calculations.

### `CodeSmellFeatureExtractor`
The core engine extending `ast.NodeVisitor` to perform a single-pass extraction of structural and security features.
