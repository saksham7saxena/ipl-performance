const API_URL = "http://localhost:8000/api";

function showSection(id) {
    // Hide all sections
    document.querySelectorAll('main > section').forEach(el => {
        el.classList.remove('active');
        // setTimeout(() => el.style.display = 'none', 300); // Optional fade out
    });

    // Show target section
    const target = document.getElementById(id);
    target.classList.add('active');

    // Update Nav
    document.querySelectorAll('nav button').forEach(btn => btn.classList.remove('active'));
    const navBtn = document.getElementById(`nav-${id}`);
    if (navBtn) navBtn.classList.add('active');
}

async function searchPlayers() {
    const query = document.getElementById('player-search').value;
    const resultsDiv = document.getElementById('player-results');

    if (query.length < 3) {
        resultsDiv.innerHTML = '';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/players?search=${query}`);
        if (!res.ok) throw new Error("API not reachable");
        const players = await res.json();

        resultsDiv.innerHTML = '';

        if (players.length === 0) {
            resultsDiv.innerHTML = '<div style="color:#888; cursor:default;">No players found</div>';
            return;
        }

        players.forEach(p => {
            const div = document.createElement('div');
            div.textContent = p.name;
            div.onclick = () => loadPlayerStats(p.player_id, p.name);
            resultsDiv.appendChild(div);
        });
    } catch (e) {
        console.error(e);
        resultsDiv.innerHTML = '<div style="color:red; font-size:0.9rem; padding:10px;">Error connecting to API. Is the backend running?</div>';
    }
}

async function loadPlayerStats(id, name) {
    const detailsDiv = document.getElementById('player-details');
    try {
        // Show loading state or placeholder
        document.getElementById('p-name').textContent = "Loading...";
        detailsDiv.style.display = 'block';

        const res = await fetch(`${API_URL}/players/${id}/stats`);
        const stats = await res.json();

        document.getElementById('p-name').textContent = name;
        document.getElementById('p-matches').textContent = stats.matches;
        document.getElementById('p-runs').textContent = stats.runs;
        document.getElementById('p-avg').textContent = stats.average || stats.avg; // Handle potential naming diffs
        document.getElementById('p-sr').textContent = stats.strike_rate;
        document.getElementById('p-100s').textContent = stats.hundreds;
        document.getElementById('p-50s').textContent = stats.fifties;

        document.getElementById('player-results').innerHTML = ''; // Clear search results
        document.getElementById('player-search').value = ''; // Clear input

    } catch (e) {
        console.error(e);
        document.getElementById('p-name').textContent = "Error loading stats";
    }
}

async function predictRuns(e) {
    e.preventDefault();
    const resultDiv = document.getElementById('prediction-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = "Calculating odds...";
    resultDiv.style.background = "#e3f2fd";
    resultDiv.style.color = "#1a237e";

    const team = document.getElementById('pred-team').value;
    const opp = document.getElementById('pred-opp').value;
    const venue = document.getElementById('pred-venue').value;
    const innings = parseInt(document.getElementById('pred-innings').value);

    // Mock vars for now
    const tossWinner = team;
    const tossChoice = "bat";

    try {
        // Build payload
        const payload = {
            season: 2024,
            venue: venue,
            team: team,
            opposition: opp,
            toss_winner: tossWinner,
            toss_choice: tossChoice,
            innings: innings
        };

        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Prediction service unavailable");

        const data = await response.json();

        // Success UI
        resultDiv.innerHTML = `
            <div style="font-size:0.9rem; color:#666; margin-bottom:5px;">Projected Score</div>
            <div style="font-size:2.5rem; color:#ff6f00; font-weight:bold;">${Math.round(data.predicted_runs)}</div>
            <div style="font-size:0.8rem; margin-top:5px;">vs ${opp} at ${venue}</div>
        `;

    } catch (e) {
        resultDiv.innerHTML = `
            <span style="color:red">⚠️ Connection Failed</span><br>
            <small>Backend is offline. Please start the API server.</small>
        `;
    }
}
