from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from src.etl.schema import get_engine, Player, BattingCard, Match, BowlingCard
from src.ml.predict import Predictor
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()
predictor = Predictor()

def get_db():
    engine = get_engine()
    with Session(engine) as session:
        yield session

class PlayerSchema(BaseModel):
    player_id: int
    name: str = ""
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class PlayerStats(BaseModel):
    matches: int
    runs: int
    balls: int
    avg: float
    strike_rate: float
    hundreds: int
    fifties: int

class PredictionRequest(BaseModel):
    season: int = 2024
    venue: str
    team: str
    opposition: str
    toss_winner: str
    toss_choice: str
    innings: int

class PredictionResponse(BaseModel):
    predicted_runs: float

@router.get("/players", response_model=List[PlayerSchema])
def list_players(search: Optional[str] = None, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Player)
    if search:
        query = query.filter(Player.name.ilike(f"%{search}%"))
    return query.limit(limit).offset(offset).all()

@router.get("/players/{player_id}/stats", response_model=PlayerStats)
def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    # Aggregated stats
    stats = db.query(
        func.count(BattingCard.match_id).label('matches'),
        func.sum(BattingCard.runs).label('runs'),
        func.sum(BattingCard.balls).label('balls'),
        func.sum(case((BattingCard.runs >= 100, 1), else_=0)).label('hundreds'),
        func.sum(case((BattingCard.runs >= 50, 1), else_=0)).label('fifties')
    ).filter(BattingCard.player_id == player_id).first()
    
    matches = stats.matches or 0
    runs = stats.runs or 0
    balls = stats.balls or 0
    hundreds = stats.hundreds or 0
    fifties = stats.fifties or 0 - hundreds
    
    outs = db.query(func.count(BattingCard.id)).filter(
        BattingCard.player_id == player_id, 
        BattingCard.is_out == True
    ).scalar() or 0
    
    avg = runs / outs if outs > 0 else runs
    sr = (runs / balls * 100) if balls > 0 else 0.0
    
    return {
        "matches": matches,
        "runs": runs,
        "balls": balls,
        "avg": round(float(avg), 2),
        "strike_rate": round(float(sr), 2),
        "hundreds": hundreds,
        "fifties": fifties
    }

@router.post("/predict", response_model=PredictionResponse)
def predict_runs(request: PredictionRequest):
    try:
        runs = predictor.predict(
            season=request.season,
            venue=request.venue,
            team=request.team,
            opposition=request.opposition,
            toss_winner=request.toss_winner,
            toss_choice=request.toss_choice,
            innings=request.innings
        )
        return {"predicted_runs": round(runs, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
