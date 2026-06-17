import shap
import numpy as np
import pandas as pd

class SHAPExplainer:
    def __init__(self, model, feature_names: list[str]):
        self.explainer = shap.TreeExplainer(model)
        self.feature_names = feature_names

    def explain(self, input_df: pd.DataFrame) -> dict:
        shap_values = self.explainer.shap_values(input_df)
        if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
            values = shap_values[:, :, 1].flatten()
        elif isinstance(shap_values, list):
            values = shap_values[1][0]
        else:
            values = shap_values[0]
        contributions = {
            name: round(float(val), 4)
            for name, val in zip(self.feature_names, values.tolist() if hasattr(values, 'tolist') else values)
        }
        sorted_contribs = dict(
            sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        )
        expected = self.explainer.expected_value
        if isinstance(expected, np.ndarray):
            base_value = round(float(expected[1]), 4) if expected.ndim == 1 and len(expected) == 2 else round(float(expected), 4)
        elif isinstance(expected, (list, tuple)):
            base_value = round(float(expected[1]), 4)
        else:
            base_value = round(float(expected), 4)
        return {
            "contributions": sorted_contribs,
            "base_value": base_value,
            "top_factor": list(sorted_contribs.keys())[0] if sorted_contribs else None,
        }
