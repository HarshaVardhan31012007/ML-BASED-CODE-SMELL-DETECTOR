import os
import sys

# Ensure we can import the pipeline
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from static_analyzer.pipeline import CodeSmellCompilerModule

def run_test():
    sample_file = "ultimate_smell_sample.py"
    if not os.path.exists(sample_file):
        print(f"Error: {sample_file} not found.")
        return

    print(f"[*] Running analysis on {sample_file}...\n")
    analyzer = CodeSmellCompilerModule()
    results = analyzer.analyze(sample_file)
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    ml_detected = [r['smell_type'] for r in results.get('ml_predictions', [])]
    sec_detected = [r['smell_type'] for r in results.get('security_smells', [])]
    
    print(f"ML Smells Detected: {', '.join(ml_detected) if ml_detected else 'None'}")
    print(f"Security Risks Detected: {len(sec_detected)}")
    for risk in sec_detected:
        print(f"  - {risk}")

if __name__ == "__main__":
    run_test()
