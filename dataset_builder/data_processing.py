import os
import ast
import hashlib
import logging
import sys
import typing

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore

# Setup logging for invalid files
logging.basicConfig(
    filename=os.path.join(config.REPORTS_DIR, 'data_processing_errors.log'),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_file_hash(filepath):
    """Calculate MD5 hash of a file for deduplication."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing {filepath}: {e}")
        return None

def validate_ast(filepath):
    """Check if the Python file is parsable using AST."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        ast.parse(source)
        return True
    except Exception as e:
        logging.error(f"AST Parsing failed for {filepath}: {e}")
        return False

def process_dataset():
    """Main processing loop for Phase 2: Deduplication and Validation."""
    print("[*] Starting Phase 2: Data Processing & Validation...")
    
    if not os.path.exists(config.PYTHON_CODE_DIR):
        print("[-] Python code directory not found. Run 'clone_and_extract.py' first.")
        return

    files = [f for f in os.listdir(config.PYTHON_CODE_DIR) if f.endswith('.py')]
    print(f"[*] Found {len(files)} files to validate.")

    seen_hashes = set()
    valid_count: int = 0
    duplicate_count: int = 0
    invalid_ast_count: int = 0

    for filename in files:
        filepath = os.path.join(config.PYTHON_CODE_DIR, filename)
        
        # 1. Reject non-python (redundant check but safe)
        if not filename.endswith('.py'):
            os.remove(filepath)
            continue
    
        # 2. Validate AST Parsing
        if not validate_ast(filepath):
            invalid_ast_count = int(typing.cast(int, invalid_ast_count) + 1)
            os.remove(filepath)
            continue
    
        # 3. Deduplication
        f_hash = get_file_hash(filepath)
        if f_hash in seen_hashes:
            duplicate_count = int(typing.cast(int, duplicate_count) + 1)
            os.remove(filepath)
            continue
        
        seen_hashes.add(f_hash)
        valid_count = int(typing.cast(int, valid_count) + 1)

    print(f"[+] Processing complete:")
    print(f"    -> Valid Files: {valid_count}")
    print(f"    -> Invalid AST: {invalid_ast_count} (Logged to REPORTS_DIR)")
    print(f"    -> Duplicates Removed: {duplicate_count}")
    print(f"    -> Total Files In Dataset: {len(seen_hashes)}")

if __name__ == "__main__":
    process_dataset()
