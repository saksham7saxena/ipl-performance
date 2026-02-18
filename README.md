# ipl-performance

# IPL Performance Analytics & Prediction System (2008–2023)

A reproducible data analytics and machine learning system for analyzing and predicting Indian Premier League (IPL) batting performance using match-level data from 2008–2023.

This project converts a visualization-first analysis into a **code-based system** with:
- a clean data ingestion and normalization pipeline,
- an analytics API for querying historical performance and trends,
- a machine learning module to predict next-innings runs,
- and a lightweight web UI for exploration and forecasts.

---

## Project Goals

### Engineering
- Build a reproducible ETL pipeline (raw CSV → normalized database)
- Define stable, testable performance metrics
- Expose analytics and predictions via a clean REST API
- Keep concerns separated: data, analytics, ML, API, UI

### Analytics & ML
- Analyze player, team, season, and venue trends
- Predict expected runs for a team or player in a future innings
- Avoid data leakage via time-aware training and evaluation
- Provide interpretable predictions (feature importance)

---

## Dataset

- Source: IPL batting dataset (2008–2023) from Kaggle
- Each row represents a player’s batting performance in a single match
- ~15k rows, ~18 columns

Typical fields include:
- season, match_id
- player, team, opponent
- venue
- runs, balls_faced, fours, sixes, strike_rate

Raw data is **not committed** to the repo.

### Local data path
