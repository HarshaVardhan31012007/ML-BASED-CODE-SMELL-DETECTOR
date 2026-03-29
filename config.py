import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
REPOS_DIR = os.path.join(DATASET_DIR, "repositories")
PYTHON_CODE_DIR = os.path.join(DATASET_DIR, "python_code")
METADATA_DIR = os.path.join(DATASET_DIR, "metadata")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# List of repositories to clone for the dataset
REPOSITORIES = [
    "https://github.com/snoopysecurity/Vulnerable-Code-Snippets",
    "https://github.com/github/codeql",
    "https://github.com/pallets/flask",
    "https://github.com/django/django",
    "https://github.com/tiangolo/fastapi",
    "https://github.com/psf/requests",
    "https://github.com/pallets/jinja",
    "https://github.com/OWASP/WebGoat",
    "https://github.com/pyupio/safety",
    "https://github.com/tonybaloney/vulnerable-python-app",
    "https://github.com/PyCQA/pylint",
    "https://github.com/PyCQA/bandit",
    "https://github.com/PyCQA/flake8",
    "https://github.com/python-security/pyt",
    "https://github.com/scikit-learn/scikit-learn",
    "https://github.com/pandas-dev/pandas",
    "https://github.com/numpy/numpy",
    "https://github.com/keras-team/keras"
]

# Code Smell Taxonomy (13 smells + 1 auxiliary)
SMELL_CATEGORIES = {
    # Security-Critical
    "SQL_INJECTION": "SQL Injection",
    "UNVALIDATED_INPUT": "Unvalidated User Input",
    "HARDCODED_CREDENTIALS": "Hard-Coded Credentials",
    "UNSAFE_API": "Unsafe API Usage (eval, exec)",
    "MISSING_SANITIZATION": "Missing Input Sanitization",
    "MISSING_AUTH": "Missing Authentication Check",
    "IMPROPER_ERROR_HANDLING": "Improper Error Handling",
    "INSECURE_FILE_HANDLING": "Insecure File Handling",
    
    # Structural
    "LONG_METHOD": "Long Method",
    "DUPLICATE_CODE": "Duplicate Code",
    "GOD_CLASS": "God Class",
    "DEAD_CODE": "Dead Code",
    "MAGIC_VALUE": "Magic Strings & Numbers",
    "DEEP_NESTING": "Deeply Nested Logic", 
    
    "CLEAN": "Clean"
}

# Files/directories to ignore during extraction
IGNORE_PATHS = [
    "tests", "test", "docs", "doc", "generated", "venv", "env",
    ".git", ".github", "third_party", "vendor", "migrations", ".tox",
    "__pycache__"
]

# Random seed for reproducibility
RANDOM_SEED = 42

# Training Configuration
DEBUG_MODE = False  
DEBUG_SUBSET_SIZE = 20000
MAJORITY_CLASS_LIMIT = 20000  # Cap major classes at 20k for better representation
OVERSAMPLE_MINORITY = True    # Enable random oversampling for rare classes

# XGBoost Optimization (Section 10)
XGB_PARAMS = {
    'max_depth': 8,
    'learning_rate': 0.1,
    'n_estimators': 1000,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,   # L1
    'reg_lambda': 1.0,  # L2
    'tree_method': 'hist',
    'n_jobs': -1,
    'random_state': RANDOM_SEED
}

# Ensure directories exist
for path in [DATASET_DIR, REPOS_DIR, PYTHON_CODE_DIR, METADATA_DIR, MODELS_DIR, REPORTS_DIR]:
    os.makedirs(path, exist_ok=True)
