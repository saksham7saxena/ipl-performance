import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.ml.features import load_training_data, prepare_features, calculate_rolling_features
import joblib
import os
import numpy as np

def train_model():
    print("Loading data...")
    raw_data = load_training_data()
    
    print("Calculating features...")
    data = calculate_rolling_features(raw_data)
    
    # Time-based split using Season
    # Train: < 2022
    # Test: >= 2022
    
    train_mask = data['season'] < 2022
    test_mask = data['season'] >= 2022
    
    train_data = data[train_mask]
    test_data = data[test_mask]
    
    X_train, y_train = prepare_features(train_data)
    X_test, y_test = prepare_features(test_data)
    
    print(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples")
    
    # Baseline: Season Average of Training Data
    baseline_pred = np.full(len(y_test), y_train.mean())
    mae_baseline = mean_absolute_error(y_test, baseline_pred)
    print(f"Baseline (Global Avg) MAE: {mae_baseline:.2f}")
    
    # XGBoost
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae_xgb = mean_absolute_error(y_test, preds)
    rmse_xgb = np.sqrt(mean_squared_error(y_test, preds))
    
    print(f"XGBoost MAE: {mae_xgb:.2f}")
    print(f"XGBoost RMSE: {rmse_xgb:.2f}")
    
    # Feature Importance
    importance = model.feature_importances_
    features = X_train.columns
    print("\nFeature Importance:")
    for f, i in zip(features, importance):
        print(f"{f}: {i:.4f}")
        
    # Save Model
    os.makedirs("src/ml/artifacts", exist_ok=True)
    joblib.dump(model, "src/ml/artifacts/model.pkl")
    print("Model saved to src/ml/artifacts/model.pkl")

if __name__ == "__main__":
    train_model()
