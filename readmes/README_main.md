# Documentation for `main.py`

## Overview
`main.py` is the "Master Controller" of the entire project development lifecycle. It provides a unified command structure to execute any phase of the pipeline, from data collection to final analysis.

## Line-by-Line / Section Analysis

### 9-27: CLI Argument Definition
- Uses `argparse` subparsers to define the project phases:
  - `setup`: Dataset collection (Phase 1).
  - `label`: Rule-based labeling (Phase 2).
  - `assemble`: Feature & data merging (Phase 3).
  - `train`: Model training (Phase 4).
  - `analyze`: The final static analysis tool (Phase 5).

### 30-32: Command `setup`
- Imports and runs `dataset_builder.clone_and_extract`.

### 33-35: Command `label`
- Imports and runs `dataset_builder.label_smells`.

### 36-38: Command `assemble`
- Imports and runs `feature_extraction.dataset_assembler`.

### 39-41: Command `train`
- Imports and runs `evaluation.train_models`.

### 42-45: Command `analyze`
- Instantiates the `CodeSmellCompilerModule` and triggers the analysis on the user-provided path.

## Key Functions

### `main()`
Acts as a router, importing the necessary modules lazily (only when the specific command is called) to reduce startup time and avoid dependency conflicts for developers only working on one phase.
