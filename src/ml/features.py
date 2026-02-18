import pandas as pd
import numpy as np
from src.etl.schema import get_engine

def load_training_data():
    engine = get_engine()
    
    # We need match details to calculate features
    query = """
    SELECT 
        m.match_id,
        m.season,
        m.match_date,
        m.venue_stadium,
        m.team1_name,
        m.team2_name,
        m.toss_winner,
        m.toss_winner_choice,
        m.team1_score,
        m.team2_score
    FROM matches m
    WHERE m.team1_score > 0 AND m.team2_score > 0
    ORDER BY m.match_date
    """
    
    df = pd.read_sql(query, engine)
    
    # Restructure into innings level (Target: Runs)
    # We want to predict runs for a specific team in a specific match
    
    innings1 = df[['match_id', 'season', 'match_date', 'venue_stadium', 'team1_name', 'team2_name', 'toss_winner', 'toss_winner_choice', 'team1_score']].copy()
    innings1.columns = ['match_id', 'season', 'match_date', 'venue', 'team', 'opposition', 'toss_winner', 'toss_choice', 'runs']
    innings1['innings'] = 1
    
    innings2 = df[['match_id', 'season', 'match_date', 'venue_stadium', 'team2_name', 'team1_name', 'toss_winner', 'toss_winner_choice', 'team2_score']].copy()
    innings2.columns = ['match_id', 'season', 'match_date', 'venue', 'team', 'opposition', 'toss_winner', 'toss_choice', 'runs']
    innings2['innings'] = 2
    
    data = pd.concat([innings1, innings2], ignore_index=True)
    data['match_date'] = pd.to_datetime(data['match_date'])
    data = data.sort_values(['match_date', 'match_id'])
    
    return data

def calculate_rolling_features(data):
    # Team Rolling Avg Runs (Last 5 games)
    data['team_avg_runs_5'] = data.groupby('team')['runs'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
    
    # Team Avg Runs (All time before this match)
    data['team_avg_runs_all'] = data.groupby('team')['runs'].transform(lambda x: x.shift(1).expanding().mean())

    # Venue Avg Runs (All time before this match)
    data['venue_avg_runs'] = data.groupby('venue')['runs'].transform(lambda x: x.shift(1).expanding().mean())
    
    # Opposition Runs Conceded Avg? (Maybe too complex for now, stick to simple features)
    
    # Fill NA (first matches) with global average
    global_avg = data['runs'].mean()
    data.fillna(global_avg, inplace=True)
    
    return data

def prepare_features(data):
    # Encode categoricals using codes
    # Note: In production, we need to save the encoding mapping. 
    # For this assignment, we will use pandas category codes and assume reliable mapping if data is static.
    # A better way for production is to use sklearn OrdinalEncoder and save it.
    
    data = data.copy()
    
    # Convert to category type first to ensure consistent encoding if we control categories
    # But here we just use what's in the data
    cat_cols = ['venue', 'team', 'opposition', 'toss_winner', 'toss_choice']
    for col in cat_cols:
        data[col] = data[col].astype('category').cat.codes
        
    features = ['season', 'venue', 'team', 'opposition', 'toss_winner', 'toss_choice', 'innings', 
                'team_avg_runs_5', 'team_avg_runs_all', 'venue_avg_runs']
    target = 'runs'
    
    return data[features], data[target]
