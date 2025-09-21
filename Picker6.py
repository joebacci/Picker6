import requests
import pandas as pd
import numpy as np

# === CONFIG ===
API_KEY = "4e85c455929d4bdbbfc0bedea8d993aa"  # your The Odds API key
SPORT = "americanfootball_nfl"
REGIONS = "us"
ODDS_FORMAT = "american"
MARKETS = "h2h"

# === HELPER FUNCTIONS ===
def fetch_nfl_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT,
        "apiKey": API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching odds: {e}")
        return []

def american_to_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

def calculate_ev(odds):
    prob = american_to_prob(odds)
    payout = (odds / 100) if odds > 0 else (100 / -odds)
    stake = 1  # assume $1 stake
    return (prob * payout) - (1 - prob) * stake

# === MAIN ===
def main():
    games = fetch_nfl_odds()
    ev_list = []

    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        start_time = game['commence_time']

        for bookmaker in game['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    outcomes = market['outcomes']
                    for outcome in outcomes:
                        ev = calculate_ev(outcome['price'])
                        ev_list.append({
                            "game": f"{away_team} @ {home_team}",
                            "team": outcome['name'],
                            "odds": outcome['price'],
                            "bookmaker": bookmaker['title'],
                            "ev": ev,
                            "start_time": start_time
                        })

    df = pd.DataFrame(ev_list)
    df_sorted = df.sort_values(by="ev", ascending=False)
    print(df_sorted)

if __name__ == "__main__":
    main()
