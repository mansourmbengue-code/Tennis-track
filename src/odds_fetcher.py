import requests
import streamlit as st
from datetime import datetime, timezone

API_KEY = "835644b28280f9bce15c122e8118e843"
BASE_URL = "https://api.the-odds-api.com/v4"

@st.cache_data(ttl=300)
def get_daily_matches():
    """Récupère les matchs de tennis du jour (ATP & WTA)."""
    url = f"{BASE_URL}/sports/tennis/events?apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        today = datetime.now(timezone.utc).date()
        matches = []
        for event in events:
            commence_time = datetime.fromisoformat(event['commence_time'].replace('Z', '+00:00'))
            # Garde les matchs d'aujourd'hui et de demain (au cas où le calendrier est vide)
            if commence_time.date() >= today:
                matches.append({
                    'id': event['id'],
                    'home_team': event['home_team'],
                    'away_team': event['away_team'],
                    'commence_time': commence_time,
                    'sport_title': event.get('sport_title', 'Tennis')
                })
        if not matches:
            return None  # Pas de match aujourd'hui
        return matches
    except Exception as e:
        st.error(f"Erreur API: {e}")
        return None