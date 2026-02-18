import pandas as pd
import os
from sqlalchemy.orm import Session
from src.etl.schema import Match, Player, BallByBall, BattingCard, BowlingCard, get_engine, create_schema

def load_data():
    engine = get_engine()
    create_schema(engine)
    
    raw_path = "data/raw"
    
    with Session(engine) as session:
        # Load Players
        print("Loading Players...")
        df_players = pd.read_csv(os.path.join(raw_path, "ipl_players_info.csv"))
        for _, row in df_players.iterrows():
            player = Player(
                player_id=row['player_id'],
                name=row['player_name'],
                batting_style=row['batting_style'],
                bowling_style=row['bowling_style'],
                image_url=row['image_url']
            )
            session.merge(player) # Use merge to handle duplicates/updates
        session.commit()

        # Load Matches
        print("Loading Matches...")
        df_matches = pd.read_csv(os.path.join(raw_path, "ipl_historical.csv"))
        # Clean date
        df_matches['match_date'] = pd.to_datetime(df_matches['match_date'], errors='coerce')
        
        for _, row in df_matches.iterrows():
            match = Match(
                match_id=row['match_id'],
                season=row['season'],
                match_date=row['match_date'],
                venue_stadium=row['match_venue_stadium'],
                venue_city=row['match_venue_city'],
                team1_name=row['team1_name'],
                team2_name=row['team2_name'],
                toss_winner=row['toss_winner'],
                toss_winner_choice=row['toss_winner_choice'],
                match_winner=row['match_winner'],
                result_margin=row['match_result_text'],
                team1_score=row['team1_runs_scored'],
                team2_score=row['team2_runs_scored']
            )
            session.merge(match)
        session.commit()

        # Load Batting Cards
        print("Loading Batting Cards...")
        df_bat = pd.read_csv(os.path.join(raw_path, "ipl_batting_card.csv"))
        
        # Handle NaN and types
        numeric_cols = ['runs', 'balls', 'fours', 'sixes', 'batsman_id', 'strikerate']
        for col in numeric_cols:
            df_bat[col] = pd.to_numeric(df_bat[col], errors='coerce').fillna(0)
            
        df_bat['batsman_id'] = df_bat['batsman_id'].astype(int)
        df_bat['runs'] = df_bat['runs'].astype(int)
        df_bat['balls'] = df_bat['balls'].astype(int)
        df_bat['fours'] = df_bat['fours'].astype(int)
        df_bat['sixes'] = df_bat['sixes'].astype(int)
        
        # isout might be boolean or string
        if df_bat['isout'].dtype == 'object':
             df_bat['isout'] = df_bat['isout'].astype(str).str.lower() == 'true'

        bat_objects = []
        for _, row in df_bat.iterrows():
            bat_objects.append(BattingCard(
                match_id=row['match_id'], # Keep as is, usually int
                team=row['team'],
                player_id=row['batsman_id'],
                runs=row['runs'],
                balls=row['balls'],
                fours=row['fours'],
                sixes=row['sixes'],
                strike_rate=row['strikerate'],
                is_out=row['isout'],
                wicket_type=row['wickettype'] if pd.notna(row['wickettype']) else None
            ))
        session.add_all(bat_objects)
        session.commit()
        
        # Load Bowling Cards
        print("Loading Bowling Cards...")
        df_bowl = pd.read_csv(os.path.join(raw_path, "ipl_bowling_card.csv"))
        bowl_objects = []
        for _, row in df_bowl.iterrows():
            bowl_objects.append(BowlingCard(
                match_id=row['match_id'],
                team=row['team'],
                player_id=row['bowler_id'],
                overs=row['overs'],
                runs_conceded=row['conceded'],
                wickets=row['wickets'],
                economy=row['economy']
            ))
        session.add_all(bowl_objects)
        session.commit()

        # Load Ball by Ball (Chunked because it's large)
        print("Loading Ball by Ball...")
        chunksize = 10000
        for chunk in pd.read_csv(os.path.join(raw_path, "ipl_ball_by_ball_data.csv"), chunksize=chunksize):
            # Clean chunk
            chunk['batsman_id'] = pd.to_numeric(chunk['batsman_id'], errors='coerce').fillna(0).astype(int)
            chunk['bowler_id'] = pd.to_numeric(chunk['bowler_id'], errors='coerce').fillna(0).astype(int)
            chunk['total_runs'] = pd.to_numeric(chunk['total_runs'], errors='coerce').fillna(0).astype(int)
            chunk['batsman_runs'] = pd.to_numeric(chunk['batsman_runs'], errors='coerce').fillna(0).astype(int)
            
            # Handle booleans
            for col in ['isfour', 'issix', 'iswicket']:
                if chunk[col].dtype == 'object':
                     chunk[col] = chunk[col].astype(str).str.lower() == 'true'
            
            bbb_objects = []
            for _, row in chunk.iterrows():
                bbb_objects.append(BallByBall(
                    match_id=row['match_id'],
                    innings_no=row['innings_no'],
                    over_number=row['over_number'],
                    ball_number=row['ball_number'],
                    batsman_id=row['batsman_id'],
                    bowler_id=row['bowler_id'],
                    total_runs=row['total_runs'],
                    batsman_runs=row['batsman_runs'],
                    is_four=row['isfour'],
                    is_six=row['issix'],
                    is_wicket=row['iswicket'],
                    dismissal_kind=row['dismissal_kind'] if 'dismissal_kind' in row and pd.notna(row['dismissal_kind']) else None
                ))
            session.add_all(bbb_objects)
            session.commit()
            print(f"Loaded {len(chunk)} balls...")

if __name__ == "__main__":
    load_data()
