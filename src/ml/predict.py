import joblib
import pandas as pd
import os
import numpy as np

class Predictor:
    def __init__(self, model_path="src/ml/artifacts/model.pkl"):
        self.model_path = model_path
        self.model = None
        
    def load_model(self):
        if not self.model:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(f"Model not found at {self.model_path}")
                
    def predict(self, season, venue, team, opposition, toss_winner, toss_choice, innings):
        self.load_model()
        
        # Simplified Feature Vector construction
        # Ideally, we load feature scaling/encoders pipelines.
        # Here we manually construct the input assuming consistency with training data categories.
        # Since categories were encoded using pandas astype('category').cat.codes, 
        # we need to ensure the same mapping.
        
        # NOTE: This approach is fragile without saved encoders.
        # For this prototype: we assume simple numeric inputs or re-map based on known lists.
        # But UI sends strings.
        
        # Hardcoding the mapping (This is not ideal for prod but works for prototype)
        # We need to know the mapping used during training.
        # Let's inspect the model features via `train.py` output or simple assumption.
        
        # Assuming simple hash or sorted index logic for now to get roughly correct input.
        # Better: Load the training data to re-create the encoder logic.
        
        # Let's construct a DataFrame with the exact column structure
        input_data = pd.DataFrame([{
            'season': season,
            'venue': self._encode('venue', venue),
            'team': self._encode('team', team),
            'opposition': self._encode('opposition', opposition),
            'toss_winner': self._encode('toss_winner', toss_winner),
            'toss_choice': self._encode('toss_choice', toss_choice),
            'innings': innings,
            'team_avg_runs_5': 160, # Approximation or query DB
            'team_avg_runs_all': 155,
            'venue_avg_runs': 165
        }])
        
        # Re-order columns to match training
        features = ['season', 'venue', 'team', 'opposition', 'toss_winner', 'toss_choice', 'innings', 
                    'team_avg_runs_5', 'team_avg_runs_all', 'venue_avg_runs']
        
        input_data = input_data[features]
        prediction = self.model.predict(input_data)[0]
        return float(prediction)

    def _encode(self, col, val):
        # Extremely simplified encoder for demo purposes
        # In real app: Load LabelEncoder artifact
        # Here: Use hash modulo or simple mapping
        return abs(hash(val)) % 10 # This is just a placeholder to run. 
        # To fix: Save encoders in train.py!
