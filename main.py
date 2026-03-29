import argparse
import sys
import os

# Add root to sys path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="ML-Driven Code Smell Detection Compiler")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: setup
    subparsers.add_parser("setup", help="Clone repositories and extract dataset (Phase 1)")

    # Command: label
    subparsers.add_parser("label", help="Run static analysis tools to label the dataset (Phase 2)")

    # Command: assemble
    subparsers.add_parser("assemble", help="Combine labels and AST features into ML dataset (Phase 3)")

    # Command: train
    subparsers.add_parser("train", help="Train ML models and save the best one (Phase 4)")

    # Command: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a Python file or directory (Phase 5 & 6)")
    analyze_parser.add_argument("path", help="Path to file or directory to analyze")

    args = parser.parse_args()

    if args.command == "setup":
        from dataset_builder.clone_and_extract import main as setup_main
        setup_main()
    elif args.command == "label":
        from dataset_builder.label_smells import main as label_main
        label_main()
    elif args.command == "assemble":
        from feature_extraction.dataset_assembler import assemble_dataset
        assemble_dataset()
    elif args.command == "train":
        from evaluation.train_models import train_and_evaluate
        train_and_evaluate()
    elif args.command == "analyze":
        from static_analyzer.pipeline import CodeSmellCompilerModule
        analyzer = CodeSmellCompilerModule()
        analyzer.analyze(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
