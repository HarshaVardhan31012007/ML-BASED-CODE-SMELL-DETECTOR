import os
import sys
import json
# Add parent directory to path to import config and feature modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def assemble_dataset():
    """
    Reads the labeled JSON dataset, extracts AST features for each code snippet,
    and produces a final structured tabular dataset for ML training.
    """
    import pandas as pd
    import config
    from feature_extraction.ast_parser import extract_features_from_code, extract_features_of_file_context

    labeled_file = os.path.join(config.METADATA_DIR, "labeled_dataset.json")
    
    if not os.path.exists(labeled_file):
        print(f"[-] Labeled dataset not found at {labeled_file}")
        print("[-] Please ensure Phase 2 (label_smells.py) has completed successfully.")
        return
        
    print(f"[*] Loading labeled dataset from {labeled_file}...")
    with open(labeled_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
        
    print(f"[*] Extracted {len(records)} records. Merging with AST features...")
    
    final_dataset = []
    failed_parse_indices: list = []
    
    # Pre-define a complete zeroed feature set for fallbacks
    zero_features = {
        "num_functions": 0, "num_classes": 0, "num_parameters": 0,
        "num_loops": 0, "num_conditionals": 0, "num_imports": 0,
        "num_returns": 0, "num_variables": 0, "num_literals": 0,
        "max_nesting_depth": 0, "ast_node_count": 0,
        "avg_func_length": 0, "max_func_length": 0,
        "avg_class_size": 0, "cyclomatic_complexity": 1,
        "num_try_except": 0, "num_comprehensions": 0,
        "num_yields": 0, "num_asserts": 0, "num_with_blocks": 0,
        "num_globals": 0, "num_lambda": 0, "num_raises": 0,
        "num_dangerous_calls": 0, "num_sensitive_literals": 0,
        "num_sql_concat": 0, "num_dynamic_open": 0,
        "num_unprotected_routes": 0, "has_except_pass": 0,
        "halstead_volume": 0.0, "halstead_difficulty": 0.0,
        "halstead_effort": 0.0, "maintainability_index": 100.0
    }

    for i, record in enumerate(records):
        code_snippet = record.get("code_snippet", "")
        ast_features = extract_features_from_code(code_snippet)
        
        # Fallback: If snippet fails to parse, try using the full file context
        if ast_features is None:
            filename = record.get("file_path", "")
            filepath = os.path.join(config.PYTHON_CODE_DIR, filename)
            
            if os.path.exists(filepath):
                try:
                    # Parse the whole file instead of just the snippet
                    # This provides the correct structural context
                    ast_features = extract_features_of_file_context(filepath, record.get("line", 1))
                except Exception:
                    ast_features = None
        
        if ast_features is None:
            failed_parse_indices.append(i)
            ast_features = zero_features.copy()
            
        # Combine labels and AST features
        combined_record = {
            "file_path": record["file_path"],
            "code_snippet": record.get("code_snippet", ""),
            "smell_type": record["smell_type"],
            "severity": record["severity"],
            "line": record.get("line", 0)
        }
        
        # Merge dicts
        combined_record.update(ast_features)
        
        # Ensure we have a label (smell_type) for the model
        final_dataset.append(combined_record)
        
        if (i + 1) % 500 == 0:
            print(f"    -> Processed {i + 1}/{len(records)} records...")
            
    print(f"[*] Finished processing. Failed AST parses: {len(failed_parse_indices)} / {len(records)}")
    
    if not final_dataset:
        print("[-] No valid records processed. Dataset assembly failed.")
        return

    # Convert to DataFrame and save
    df = pd.DataFrame(final_dataset)
    
    # Fill any missing numeric columns with zero
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    output_csv = os.path.join(config.METADATA_DIR, "ml_dataset.csv")
    df.to_csv(output_csv, index=False)
    
    print(f"[+] Final structured dataset successfully generated!")
    print(f"[+] Shape: {df.shape}")
    print(f"[+] Saved to: {output_csv}")
    
    # Print class distribution
    print("\nClass Distribution:")
    print(df["smell_type"].value_counts())

if __name__ == "__main__":
    assemble_dataset()
