from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    
    match_id = Column(Integer, primary_key=True)
    season = Column(Integer)
    match_date = Column(Date)
    venue_stadium = Column(String)
    venue_city = Column(String)
    team1_name = Column(String)
    team2_name = Column(String)
    toss_winner = Column(String)
    toss_winner_choice = Column(String)
    match_winner = Column(String)
    result_margin = Column(String) # Derived or from raw?
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    
class Player(Base):
    __tablename__ = 'players'
    
    player_id = Column(Integer, primary_key=True)
    name = Column(String)
    batting_style = Column(String)
    bowling_style = Column(String)
    image_url = Column(String)

class BallByBall(Base):
    __tablename__ = 'ball_by_ball'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'), index=True)
    innings_no = Column(Integer)
    over_number = Column(Integer)
    ball_number = Column(Integer)
    batsman_id = Column(Integer, ForeignKey('players.player_id'))
    bowler_id = Column(Integer, ForeignKey('players.player_id'))
    total_runs = Column(Integer)
    batsman_runs = Column(Integer)
    is_four = Column(Boolean)
    is_six = Column(Boolean)
    is_wicket = Column(Boolean)
    dismissal_kind = Column(String, nullable=True) # inferred
    
    # Relationships
    match = relationship("Match")
    batsman = relationship("Player", foreign_keys=[batsman_id])
    bowler = relationship("Player", foreign_keys=[bowler_id])

class BattingCard(Base):
    __tablename__ = 'batting_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    team = Column(String)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    runs = Column(Integer)
    balls = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    strike_rate = Column(Float)
    is_out = Column(Boolean)
    wicket_type = Column(String)

class BowlingCard(Base):
    __tablename__ = 'bowling_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'))
    team = Column(String)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    overs = Column(Float)
    runs_conceded = Column(Integer)
    wickets = Column(Integer)
    economy = Column(Float)

def get_engine(db_path='sqlite:///data/ipl.db'):
    return create_engine(db_path)

def create_schema(engine):
    Base.metadata.create_all(engine)
