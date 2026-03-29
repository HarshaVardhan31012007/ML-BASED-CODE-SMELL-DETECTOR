import os
import sys
import tokenize
import io
import joblib # type: ignore
import pandas as pd # type: ignore
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore
from feature_extraction.ast_parser import extract_features_from_file, extract_features_from_code # type: ignore
from security_analysis.scanner import security_scan # type: ignore
from explainability import SHAPExplainer # type: ignore

class CodeSmellCompilerModule:
    def __init__(self):
        # Update path to match the actual file found in the models directory
        self.model_path = os.path.join(config.MODELS_DIR, "python_code_smell_model.pkl")
        
        self.model = None
        self.explainer = None
        self.le = None
        
        self.load_artifacts()

    def load_artifacts(self):
        """Loads trained ML pipeline and associated artifacts."""
        try:
            if os.path.exists(self.model_path):
                # The model is an SKLearn Pipeline containing preprocessor + classifier
                self.model = joblib.load(self.model_path)
                
                # Load label encoder
                le_path = os.path.join(config.MODELS_DIR, "label_encoder.pkl")
                if os.path.exists(le_path):
                    self.le = joblib.load(le_path)
                
                try:
                    self.explainer = SHAPExplainer(self.model)
                except Exception as se:
                    print(f"[!] Failed to initialize SHAP explainer: {se}")
                
                print("[*] Production Pipeline and SHAP artifacts loaded.")
            else:
                print(f"[!] Model not found at {self.model_path}. Predictions unavailable.")
        except Exception as e:
            print(f"[!] Error loading ML artifacts: {e}")

    def predict_smells(self, filepath):
        """Extracts features and predicts code smells using the Ensemble model."""
        if not self.model:
            return []

        # 1. Feature Extraction
        features = extract_features_from_file(filepath)
        if not features:
            return []

        # 2. Convert to DataFrame
        df = pd.DataFrame([features])
        
        # 3. Predict using the Ensemble Model
        try:
            # The model is an instance of EnsembleCodeSmellClassifier
            model_obj = self.model
            prediction_label = model_obj.predict(df)[0]
            proba = model_obj.predict_proba(df)[0]
            confidence = float(max(proba))
        except Exception as e:
            print(f"[!] ML Inference failed: {e}")
            return []

        prediction_results = []
        explanation_plot = None
        
        # Explain prediction via SHAP
        expl_obj = self.explainer
        if expl_obj is not None:
            try:
                # Need to use the preprocessor internally
                processed_df = model_obj.preprocessor.transform(df)
                feature_names = model_obj.preprocessor.get_feature_names_out()
                pdf = pd.DataFrame(processed_df, columns=feature_names)
                explanation_plot = expl_obj.explain_prediction(pdf)
            except Exception as e:
                print(f"[!] SHAP explanation failed: {e}")

        if prediction_label != "Clean":
            conf_val = float(f"{confidence:.2f}")
            prediction_results.append({
                "file": os.path.basename(filepath),
                "line": 1, 
                "smell_type": prediction_label,
                "severity": "High" if confidence > 0.8 else "Medium",
                "message": f"ML Prediction: {prediction_label} (Confidence: {conf_val})",
                "confidence": conf_val,
                "explanation": explanation_plot
            })
            
        return prediction_results

    def analyze(self, target_path):
        """Runs the complete analysis pipeline."""
        print(f"\n{'='*50}")
        print(f"[*] Analyzing: {target_path}")
        print(f"{'='*50}")

        results = {
            "ml_predictions": [],
            "security_smells": [] 
        }

        # 1. ML-Based Prediction
        if os.path.isfile(target_path):
            try:
                results["ml_predictions"].extend(self.predict_smells(target_path))
            except Exception as e:
                print(f"[!] ML prediction failed for {target_path}: {e}")
        
        # 2. Security Patterns / Rules
        try:
            vulnerabilities = security_scan(target_path)
            for vuln in vulnerabilities:
                 results["security_smells"].append({
                    "line": vuln.get("line"),
                    "smell_type": vuln.get("issue_text", "Security Risk"),
                    "severity": vuln.get("issue_severity"),
                    "message": vuln.get("issue_text")
                })
        except Exception as e:
            print(f"[!] Security scan failed for {target_path}: {e}")

        # 3. Output Report
        self.print_report(results)
        return results

    def print_report(self, results):
        print("\n[REPORT] Code Smell Predictions:")
        if not results["ml_predictions"]:
            print("  -> No significant code smells predicted.")
        for smell in results["ml_predictions"]:
            print(f"  [!] WARNING: {smell['smell_type']} detected (Confidence: {smell['confidence']})")

        print("\n[REPORT] Security Analysis:")
        if not results["security_smells"]:
            print("  -> No security vulnerabilities found.")
        for vuln in results["security_smells"]:
            print(f"  [!] {vuln['severity']}: {vuln['message']} at line {vuln['line']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python static_analyzer/pipeline.py <file_or_directory>")
        return

    analyzer = CodeSmellCompilerModule()
    analyzer.analyze(sys.argv[1])

if __name__ == "__main__":
    main()
