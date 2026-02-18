import pytest
import os
from sqlalchemy import create_engine, text

def test_db_exists():
    assert os.path.exists("data/ipl.db")

def test_tables_populated():
    engine = create_engine("sqlite:///data/ipl.db")
    with engine.connect() as conn:
        matches = conn.execute(text("SELECT count(*) FROM matches")).scalar()
        players = conn.execute(text("SELECT count(*) FROM players")).scalar()
        
        assert matches > 0, "Matches table is empty"
        assert players > 0, "Players table is empty"
