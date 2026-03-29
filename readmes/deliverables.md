# Project Deliverables: Phases 3, 4, and 5

This document outlines the deliverables and activities for the Core Development, Intelligence, and Evaluation phases of the ML-Driven Code Smell Detection Compiler.

## PHASE 3: CORE DEVELOPMENT PHASE

### Week 5: Language / Data Model Design
**Activities:**
- Define supported programming languages (Python focus).
- Design AST-based feature and data models.
- Establish input and output formats.

**Deliverables:**
- **Data model specification:** (See `feature_extraction/ast_parser.py`)
- **Sample inputs and outputs:** (See `config.py` for taxonomy)

**What to Tell & Show:**
- **Tell:** Explain why Python was chosen (high density of security samples) and how we use AST to represent code as nodes rather than just text.
- **Show Code:** `config.py` (specifically `SMELL_CATEGORIES`).
- **Show Output:** A sample dictionary of extracted features (run `python feature_extraction/ast_parser.py`).

**Commands to Run:**
```bash
python feature_extraction/ast_parser.py
```

### Week 6: Parsing & Data Ingestion
**Activities:**
- Implement parser and AST generation.
- Perform syntactic and basic semantic validation.
- Handle error detection and reporting.

**Deliverables:**
- **Parsing and data ingestion module:** (`dataset_builder/clone_and_extract.py`)
- **Syntax validation results:** (`reports/data_processing_errors.log`)

**What to Tell & Show:**
- **Tell:** Discuss how we automate the collection of 10k+ files and how we use MD5 hashing to ensure data uniqueness.
- **Show Code:** `dataset_builder/data_processing.py` (the `validate_ast` function).
- **Show Output:** The logs in `reports/data_processing_errors.log` showing rejected, corrupted files.

**Commands to Run:**
```bash
python main.py setup
```

### Week 7: Core Static Analysis Implementation
**Activities:**
- Implement AST traversal algorithms.
- Extract static code features.
- Detect rule-based code smells.

**Deliverables:**
- **Functional static analysis engine:** (`dataset_builder/label_smells.py`)
- **Intermediate analysis logs:** (`dataset/metadata/labeled_dataset.json`)

**What to Tell & Show:**
- **Tell:** Explain the "Visitor Pattern" used to walk the AST and how we combine AST rules with Bandit security scans for high-confidence labels.
- **Show Code:** `dataset_builder/label_smells.py` (specifically the `RuleBasedLabeler` class).
- **Show Output:** Snippets from `labeled_dataset.json` showing a code block mapped to a `smell_type`.

**Commands to Run:**
```bash
python main.py label
```

### Week 8: Intermediate Representation & Analysis
**Activities:**
- Design intermediate representations.
- Perform control flow and data flow analysis.
- Identify insecure coding patterns.

**Deliverables:**
- **IR design documentation:** (The feature vector in `ast_parser.py`)
- **Analysis results:** (`dataset/metadata/ml_dataset.csv`)

**What to Tell & Show:**
- **Tell:** Describe the "Feature Vector"—how we turn a code file into a row of 30+ numerical metrics (nesting depth, complexity, dangerous API counts).
- **Show Code:** `feature_extraction/dataset_assembler.py`.
- **Show Output:** Open `ml_dataset.csv` in Excel or VS Code to show the tabular data ready for ML.

**Commands to Run:**
```bash
python main.py assemble
```

---

## PHASE 4: INTELLIGENCE, OPTIMIZATION & SECURITY

### Week 9: ML Model Integration
**Activities:**
- Train ML models on labeled code smell datasets.
- Integrate ML predictions with static analysis engine.

**Deliverables:**
- **Trained ML model:** (`models/python_code_smell_model.pkl`)
- **Evaluation metrics:** (`reports/evaluation_metrics.json`)

**What to Tell & Show:**
- **Tell:** Discuss the Ensemble approach (Random Forest + XGBoost) and the F1-score achievements (>80% for critical smells).
- **Show Code:** `evaluation/train_models.py`.
- **Show Output:** `reports/confusion_matrix.png` to demonstrate model accuracy.

**Commands to Run:**
```bash
python main.py train
```

### Week 10: Optimization & Security Enforcement
**Activities:**
- Optimize performance and memory usage.
- Enforce secure coding constraints.

**Deliverables:**
- **Optimized implementation:** (`static_analyzer/pipeline.py`)
- **Security analysis report:** (Generated results from `cli.py analyze`)

**What to Tell & Show:**
- **Tell:** Explain how SHAP Explainability helps developers understand the *why* behind a prediction.
- **Show Code:** `explainability.py`.
- **Show Output:** Run `python verify_production.py` to show the final report with "Contribution Analysis" plots.

**Commands to Run:**
```bash
python main.py analyze example_file.py
# or
python cli.py analyze example_file.py
```

---

## PHASE 5: EVALUATION & VALIDATION

### Week 11: Testing & Validation
**Activities:**
- Functional testing of modules.
- Stress testing and corner case evaluation.

**Deliverables:**
- **Test cases and results:** (Run `pytest test_smells.py`)
- **Bug-fix documentation:** (`task.md` or `walkthrough.md`)

**What to Tell & Show:**
- **Tell:** Summarize the testing strategy—how we validated both the security rules and the ML model's generalization capabilities.
- **Show Code:** `test_smells.py`.
- **Show Output:** Terminal output of `pytest` showing all green passes.

**Commands to Run:**
```bash
pytest test_smells.py
# then
python verify_production.py
```
