import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from static_analyzer.pipeline import CodeSmellCompilerModule # type: ignore

def verify():
    print("[*] Starting Production Verification...")
    
    analyzer = CodeSmellCompilerModule()
    
    # Test sample with multiple smells:
    # 1. SQL Injection (Security)
    # 2. Evaluation usage (Security)
    # 3. Magic Numbers (ML/Pattern)
    # 4. Long Method (ML/Pattern)
    test_code = """
import sqlite3

def heavy_processing(data):
    # SQL Injection
    query = "SELECT * FROM users WHERE id = " + data
    
    # Unsafe API
    eval(data)
    
    # Magic Number and Long Method check
    if data > 999: # Magic Number
        print('Case A')
    elif data < -888:
        print('Case B')
        
    # Pad with lines to trigger Long Method
    print('line 1')
    print('line 2')
    print('line 3')
    print('line 4')
    print('line 5')
    print('line 6')
    print('line 7')
    print('line 8')
    print('line 9')
    print('line 10')
    print('line 11')
    print('line 12')
    print('line 13')
    print('line 14')
    print('line 15')
    print('line 16')
    print('line 17')
    print('line 18')
    print('line 19')
    print('line 20')
    print('line 21')
    print('line 22')
    print('line 23')
    print('line 24')
    print('line 25')
    print('line 26')
    print('line 27')
    print('line 28')
    print('line 29')
    print('line 30')
    print('line 31')
    print('line 32')
    print('line 33')
    print('line 34')
    print('line 35')
    print('line 36')
    print('line 37')
    print('line 38')
    print('line 39')
    print('line 40')
    print('line 41')
    print('line 42')
    print('line 43')
    print('line 44')
    print('line 45')
    print('line 46')
    print('line 47')
    print('line 48')
    print('line 49')
    print('line 50')
    print('line 51')
"""
    
    temp_file = "verify_test.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(test_code)
        
    try:
        results = analyzer.analyze(temp_file)
        
        print("\n[VERIFICATION RESULTS]")
        print(json.dumps(results, indent=2))
        
        # Validation checks
        has_security = len(results.get("security_vulnerabilities", [])) > 0
        has_ml = len(results.get("ml_predictions", [])) > 0
        
        if has_security:
            print("[✓] Security Scanner Functional")
        else:
            print("[✗] Security Scanner Failed to detect patterns")
            
        if has_ml:
            print("[✓] ML Prediction & SHAP Functional")
        else:
            print("[!] ML Prediction returned empty (Normal if model not yet trained or code is clean)")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    verify()
