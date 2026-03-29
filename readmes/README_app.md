# Documentation for `app.py`

## Overview
`app.py` is the web gateway for the project. Built using **FastAPI**, it serves as a JSON API and a web interface, allowing users to paste code into a browser and see analysis results instantly.

## Line-by-Line / Section Analysis

### 3-8: Imports
- Imports FastAPI components, Pydantic for data validation, and Uvicorn for the ASGI server.

### 10-20: Path Resolution
- Dynamically ensures that the script can find the internal `static_analyzer` module regardless of whether it's run from the root or a subdirectory.

### 22-28: FastAPI Initialization
- **Line 22:** Creates the `app` instance.
- **Lines 25-28:** Configures the web server to serve static assets (CSS/JS) and HTML templates (Jinja2).

### 31: Analyzer Initialization
- **Line 31:** Instantiates the `CodeSmellCompilerModule`. This loads the ML model into server memory at startup, ensuring fast analysis.

### 33-34: `CodeSnippet` Data Model
- Defines the expected JSON structure for the API: `{ "code": "string" }`.

### 36-38: Route `/`
- Serves the main `index.html` page to the user's browser.

### 40-61: Route `/analyze` (The Core API)
- **Line 41:** Accepts a `CodeSnippet` object.
- **Line 45-47:** Saves the received code to a temporary file. This is necessary because the `analyzer` is designed to read files from disk.
- **Line 50:** Triggers the `analyzer.analyze()` pipeline.
- **Line 53-54:** Immediately cleans up (deletes) the temporary file after analysis.
- **Line 56:** Returns the analysis results (ML predictions + security smells) as JSON.
- **Lines 57-61:** Robust error handling. If anything fails, it logs a traceback and returns a 500 status code.

### 63-64: Server Launch
- Starts the production server on port 8000 using `uvicorn`.

## Key Functions

### `analyze_snippet`
The primary endpoint for the web frontend. It bridges the gap between the HTTP request and the local file-based analysis engine.
