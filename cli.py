import argparse
import sys
import os
import multiprocessing
import time

# Add root directory to path to resolve config and static_analyzer
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    import config # type: ignore
    from static_analyzer.pipeline import CodeSmellCompilerModule # type: ignore
except ImportError:
    # Fallback for sub-directory execution
    sys.path.append(os.path.join(root_dir, '..'))
    import config # type: ignore
    from static_analyzer.pipeline import CodeSmellCompilerModule # type: ignore

def list_smells():
    """Implementation of 'code-smell-detector list-smells'."""
    print("\n[+] Supported Code Smells:")
    for key, name in config.SMELL_CATEGORIES.items():
        if key != "CLEAN":
            print(f"  - {name}")

def analyze_file(filepath):
    """Wrapper for parallel execution."""
    analyzer = CodeSmellCompilerModule()
    return analyzer.analyze(filepath)

def main():
    parser = argparse.ArgumentParser(prog="code-smell-detector", description="ML-Driven Code Smell Detection Compiler CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze file or directory")
    analyze_parser.add_argument("path", help="Path to Python file or directory")
    analyze_parser.add_argument("--recursive", action="store_true", help="Recursive directory scan")

    # Command: list-smells
    subparsers.add_parser("list-smells", help="List all detectable code smells")

    args = parser.parse_args()

    if args.command == "analyze":
        if os.path.isfile(args.path):
            if not args.path.endswith('.py'):
                print("[-] Error: Only Python (.py) files are supported.")
                return
            analyzer = CodeSmellCompilerModule()
            analyzer.analyze(args.path)
        elif os.path.isdir(args.path):
            # Collect files
            all_files = []
            if args.recursive:
                for root, _, files in os.walk(args.path):
                    for f in files:
                        if f.endswith('.py'):
                            all_files.append(os.path.join(root, f))
            else:
                all_files = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.py')]

            if not all_files:
                print("[-] No Python files found in directory.")
                return

            print(f"[*] Analyzing {len(all_files)} files using multiprocessing...")
            start_time = time.time()
            
            # Use pool for parallel analysis
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                results = pool.map(analyze_file, all_files)
            
            duration = time.time() - start_time
            print(f"\n[+] Analysis complete in {duration:.2f}s ({duration/len(all_files):.2f}s per file)")
        else:
            print("[-] Error: Invalid path.")

    elif args.command == "list-smells":
        list_smells()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
