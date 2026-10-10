import os
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.calibration import CalibratedClassifierCV

from src.features import KestrelFeatureExtractor, NUMERIC_FEATURES, CATEGORICAL_FEATURES

def create_preprocessing_pipeline() -> ColumnTransformer:
    """Create reusable scikit-learn ColumnTransformer for numeric & categorical features."""
    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    return ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERIC_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

def build_model_pipeline(model_type: str = "logistic", calibrated: bool = True) -> Pipeline:
    """
    Build a complete feature extraction, preprocessing, and classification pipeline.
    When calibrated=True, wraps the estimator in 5-fold CalibratedClassifierCV(method='sigmoid')
    to ensure output probabilities reflect true empirical return risk (Brier score < prevalence baseline).
    """
    preprocessor = create_preprocessing_pipeline()

    if model_type == "logistic":
        base_clf = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    elif model_type == "rf":
        base_clf = RandomForestClassifier(n_estimators=200, max_depth=10, class_weight='balanced', random_state=42)
    elif model_type == "hgb":
        base_clf = HistGradientBoostingClassifier(max_iter=150, class_weight='balanced', random_state=42)
    elif model_type == "dummy":
        base_clf = DummyClassifier(strategy='prior')
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    if calibrated and model_type != "dummy":
        clf = CalibratedClassifierCV(estimator=base_clf, cv=5, method='sigmoid')
    else:
        clf = base_clf

    pipeline = Pipeline([
        ('extractor', KestrelFeatureExtractor()),
        ('prep', preprocessor),
        ('clf', clf)
    ])

    return pipeline

def save_model(pipeline: Pipeline, filepath: str = "models/model_pipeline.joblib"):
    """Persist fitted model pipeline to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(pipeline, filepath)

def load_model(filepath: str = "models/model_pipeline.joblib") -> Pipeline:
    """Load fitted model pipeline from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fitted model artifact not found at {filepath}")
    return joblib.load(filepath)
