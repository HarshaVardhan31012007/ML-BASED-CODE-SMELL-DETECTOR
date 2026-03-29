# Documentation for `scanner.py`

## Overview
`scanner.py` provides the immediate, rule-based security scanning capability. It combines a professional security linter (Bandit) with custom Regex and AST patterns to detect vulnerabilities like SQL Injection, hardcoded secrets, and overly deep logic nesting.

## Line-by-Line / Section Analysis

### 16-63: `run_bandit(target_path)`
- **Lines 26-30:** Uses `subprocess.run` to execute the Bandit module (`python -m bandit`) on the target file or directory.
- **Line 31-47:** Error handling for the JSON output. Includes a safeguard for decoding issues.
- **Lines 51-59:** Formats Bandit's findings into a standardized dictionary containing file, line, severity, and confidence levels.

### 65-88: `scan_for_secrets(filepath)`
- **Lines 67-71:** Defines regular expression patterns for common secrets like passwords, AWS keys, and generic API keys.
- **Lines 75-85:** Performs a line-by-line scan of the file to find matches, marking them as `HIGH` severity.

### 90-137: `scan_for_structural_smells(filepath)`
- **Lines 97-103:** Parses the file with AST and builds a `parents` dictionary for upward traversal.
- **Lines 107-122:** **Deep Nesting Check:** For every control structure (If, For, While), it walks up the parents to calculate the current depth. If depth > 4, it flags a "Deeply nested logic" smell.
- **Lines 125-134:** **Magic Values Check:** Looks for numeric constants (other than 0, 1, -1) used directly in comparisons or math operations instead of named variables.

### 139-161: `security_scan(target_path)`
- The main coordinator function.
- **Line 144:** Triggers the Bandit linter.
- **Lines 147-157:** Triggers the manual pattern-based checks for both secrets and structural smells.
- **Line 159:** Merges all results into a single list of findings.

## Key Functions

### `run_bandit`
Wraps the industry-standard Bandit tool to leverage its extensive security rule library.

### `scan_for_structural_smells`
Uses AST to detect complexity issues (Nesting) and maintainability issues (Magic Numbers) that aren't strictly security holes but impact code quality.

### `security_scan`
The primary API used by the rest of the application to perform a full security audit on a codebase.
