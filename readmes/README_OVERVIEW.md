# Project Documentation Overview

This directory contains detailed, line-by-line and function-level documentation for every major file in the ML-Driven Code Smell Detection Compiler project.

## Project Deliverables
- [Deliverables Phases 3-5](deliverables.md) - Weekly breakdown of activities and milestones.

## Core Modules
- [config.py](README_config.md) - Global settings and taxonomy.
- [pipeline.py](README_pipeline.md) - The main analysis orchestrator.
- [explainability.py](README_explainability.md) - SHAP-based feature contribution analysis.
- [ast_parser.py](README_ast_parser.md) - Feature extraction engine.
- [scanner.py](README_scanner.md) - Rule-based security and structural scanner.

## Dataset Building
- [clone_and_extract.py](README_clone_and_extract.md) - Phase 1: Data collection.
- [data_processing.py](README_data_processing.md) - Phase 2: Deduplication and validation.
- [label_smells.py](README_label_smells.md) - Phase 2: Automated labeling.
- [dataset_assembler.py](README_dataset_assembler.md) - Phase 3: Feature merging.

## Training & Evaluation
- [train_models.py](README_train_models.md) - Standard training & CV pipeline.
- [model_training.py](README_model_training.md) - Ensemble classifier implementation.
- [verify_production.py](README_verify_production.md) - End-to-end integration test.
- [test_smells.py](README_test_smells.md) - Unit and regression tests.

## Entry Points
- [main.py](README_main.md) - Master pipeline controller.
- [app.py](README_app.md) - FastAPI Web Server.
- [cli.py](README_cli.md) - Command Line Interface.
