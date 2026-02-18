# IPL Performance Analytics System

A comprehensive system for analyzing and predicting IPL match outcomes using historical data (2008-2023).

## Features

- **ETL Pipeline**: Ingests raw CSV data into a normalized SQLite database.
- **Analytics API**: FastAPI-based backend serving player stats, leaderboards, and predictions.
- **ML Module**: XGBoost model to predict team scores based on venue, innings, toss decisions, and opposition.
- **Web UI**: Modern, responsive frontend (Glassmorphism design) for exploring stats and running match simulations.

## Project Structure

```
ipl-performance/
├── data/               # SQLite database and raw CSVs
├── src/
│   ├── api/            # FastAPI backend
│   ├── etl/            # Data ingestion scripts
│   ├── ml/             # Machine Learning training & inference
│   └── ui/             # HTML/CSS/JS frontend
├── tests/              # Unit tests
├── config/             # Configuration files
└── requirements.txt    # Python dependencies
```

## Setup & Installation

**Prerequisites**: Python 3.10+

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/saksham7saxena/ipl-performance.git
   cd ipl-performance
   ```

2. **Set up Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database (ETL)**:
   This processes the raw CSV data into `data/ipl.db`.
   ```bash
   # Windows (PowerShell)
   $env:PYTHONPATH="."; python src/etl/ingest.py
   
   # Linux/Mac
   PYTHONPATH=. python src/etl/ingest.py
   ```

## Usage

### 1. Train the Prediction Model
Before running predictions, train the XGBoost model:
```bash
python -m src.ml.train
```

### 2. Start the API Server
Launch the backend server:
```bash
uvicorn src.api.main:app --reload
```
The API will be running at `http://127.0.0.1:8000`.

### 3. Open the Dashboard
Open `src/ui/index.html` in your web browser. You can now:
- View Orange/Purple Cap leaderboards.
- Search for player statistics.
- Predict match scores using the ML model.

## Testing

To verify the system integrity:
```bash
pytest tests
```
