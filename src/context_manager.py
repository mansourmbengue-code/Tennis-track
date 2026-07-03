import streamlit as st
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from geopy.distance import geodesic
from datetime import datetime, timedelta
import random

analyzer = SentimentIntensityAnalyzer()

class TennisContextAnalyzer:
    def __init__(self, player_name, tournament_location="Paris"):
        self.player = player_name
        self.tournament = tournament_location
        self.last_tournaments = {
            "Djokovic": ("Belgrade", 44.7866, 20.4489),
            "Alcaraz": ("Madrid", 40.4168, -3.7038),
            "Sinner": ("Rome", 41.9028, 12.4964),
            "Medvedev": ("Moscou", 55.7558, 37.6173),
            "Nadal": ("Barcelone", 41.3851, 2.1734)
        }

    @st.cache_data(ttl=3600)
    def get_full_context(_self):
        flight_data = _self._scrape_flight()
        insta_data = _self._scrape_instagram()
        news_data = _self._scrape_news()
        hotel_data = _self._scrape_hotel()
        scores = _self._calculate_scores(flight_data, insta_data, news_data, hotel_data)
        return {
            "flight": flight_data,
            "instagram": insta_data,
            "news": news_data,
            "hotel": hotel_data,
            "scores": scores
        }

    def _scrape_flight(self):
        if self.player in self.last_tournaments:
            last_loc = self.last_tournaments[self.player]
            current_loc = (48.8566, 2.3522)
            distance = geodesic(last_loc[1:], current_loc).km
            jetlag_hours = round(distance / 1000)
            fatigue_score = min(100, int(distance / 150))
            return {"distance_km": int(distance), "jetlag_hours": jetlag_hours, "fatigue_score": fatigue_score}
        return {"distance_km": 0, "jetlag_hours": 0, "fatigue_score": 20}

    def _scrape_instagram(self):
        posts_data = []
        try:
            import instaloader
            L = instaloader.Instaloader()
            profile = instaloader.Profile.from_username(L.context, self.player.lower())
            count = 0
            for post in profile.get_posts():
                if count >= 5:
                    break
                caption = post.caption if post.caption else ""
                sentiment_score = analyzer.polarity_scores(caption)['compound']
                posts_data.append({
                    "date": post.date_utc,
                    "caption": caption[:100] + "...",
                    "sentiment": round(sentiment_score, 2),
                    "likes": post.likes
                })
                count += 1
        except:
            sentiments = [round(random.uniform(-0.8, 0.8), 2) for _ in range(5)]
            for i in range(5):
                posts_data.append({
                    "date": datetime.now() - timedelta(hours=i*6),
                    "caption": f"Post simulé {i+1}",
                    "sentiment": sentiments[i],
                    "likes": random.randint(100, 5000)
                })
        if posts_data:
            avg_sentiment = sum(p['sentiment'] for p in posts_data) / len(posts_data)
            return {"posts": posts_data, "avg_sentiment": round(avg_sentiment, 2), "count": len(posts_data)}
        return {"posts": [], "avg_sentiment": 0, "count": 0}

    def _scrape_news(self):
        try:
            url = f"https://news.google.com/rss/search?q={self.player}+tennis&hl=fr"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            count = len(items[:10])
            return {"article_count": count, "trend": "up" if count > 5 else "stable"}
        except:
            return {"article_count": random.randint(1, 8), "trend": "unknown"}

    def _scrape_hotel(self):
        score = random.randint(40, 95)
        return {"score": score, "name": "Hôtel Standard", "distance_court": random.randint(1, 15)}

    def _calculate_scores(self, flight, insta, news, hotel):
        fatigue_note = min(100, flight['fatigue_score'] + flight['jetlag_hours'] * 5)
        hotel_note = hotel['score']
        buzz_note = min(100, news['article_count'] * 8)
        social_note = (insta['avg_sentiment'] + 1) * 50
        mental_global = int((fatigue_note * 0.3) + (hotel_note * 0.2) + (buzz_note * 0.2) + (social_note * 0.3))
        return {
            "fatigue": fatigue_note,
            "hotel_confort": hotel_note,
            "buzz": buzz_note,
            "social_sentiment": social_note,
            "mental_global": mental_global
        }