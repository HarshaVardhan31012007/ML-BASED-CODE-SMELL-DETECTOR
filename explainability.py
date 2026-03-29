import os
import joblib # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import shap # type: ignore
import matplotlib.pyplot as plt # type: ignore
from io import BytesIO
import base64

class SHAPExplainer:
    def __init__(self, pipeline):
        """
        pipeline: An SKLearn Pipeline containing 'preprocessor' and 'classifier'.
        """
        self.pipeline = pipeline
        self.explainer = None
        
        try:
            # Extract classifier from pipeline
            classifier = self.pipeline.named_steps['classifier']
            self.explainer = shap.TreeExplainer(classifier)
        except Exception as e:
            print(f"SHAP Init Error: {e}")

    def explain_prediction(self, df):
        """Generates SHAP values and returns a base64 plot."""
        explainer_obj = self.explainer
        if explainer_obj is None:
            return None
            
        try:
            # 1. Transform input using the pipeline's preprocessor
            X_transformed = self.pipeline.named_steps['preprocessor'].transform(df)
            
            # 2. Get SHAP values
            if hasattr(explainer_obj, 'shap_values'):
                shap_values = explainer_obj.shap_values(X_transformed)
            else:
                # Newer SHAP API - explainer is callable
                if callable(explainer_obj):
                    shap_values = explainer_obj(X_transformed).values
                else:
                    shap_values = None
            
            if shap_values is None:
                return None
            
            # 3. Create plot
            plt.figure(figsize=(10, 5))
            
            # Determine prediction index
            pred_idx = self.pipeline.predict(df)[0]
            
            # Handle multi-class shap_values formats
            if isinstance(shap_values, list):
                # For RF, shap_values is a list of [n_samples, n_features]
                vals = shap_values[pred_idx][0]
            elif len(shap_values.shape) == 3:
                # For some XGB versions, it might be [n_samples, n_features, n_classes]
                vals = shap_values[0, :, pred_idx]
            else:
                # Binary or flat
                vals = shap_values[0]

            # Get feature names from preprocessor
            try:
                all_features = self.pipeline.named_steps['preprocessor'].get_feature_names_out()
            except:
                all_features = [f"Feature {i}" for i in range(X_transformed.shape[1] if hasattr(X_transformed, 'shape') else 100)]

            # Sort and pick top 10
            indices = np.argsort(np.abs(vals))[-10:]
            
            plt.barh(range(10), vals[indices], color='#6366f1') # Brand color
            plt.yticks(range(10), [all_features[i] for i in indices])
            plt.title(f"Contribution Analysis")
            plt.xlabel("SHAP Value (Impact on Prediction)")
            plt.tight_layout()
            
            # Save to b64
            buf = BytesIO()
            plt.savefig(buf, format="png", transparent=True)
            plt.close()
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"SHAP Prediction Error: {e}")
            return None
