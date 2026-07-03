import streamlit as st
import pandas as pd
import random
from src.context_manager import TennisContextAnalyzer
from src.visualizers.charts import create_gauge
from src.odds_fetcher import get_daily_matches

st.set_page_config(page_title="Tennis Edge Aladdin", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .main { background-color: #0A0E17; }
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stSelectbox, .stRadio { background-color: #141A26; border-radius: 8px; }
    h1, h2, h3 { color: #E8EDF2 !important; }
    .alert-box {
        background: linear-gradient(90deg, #FF4757, #F5A623);
        padding: 0.8rem;
        border-radius: 12px;
        color: black;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        border-left: 5px solid white;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🎾 Trading Tennis")
st.sidebar.markdown("---")

# ---- RÉCUPÉRATION DES MATCHS RÉELS ----
matches = get_daily_matches()

if matches is None or len(matches) == 0:
    st.sidebar.warning("⚠️ Aucun match ATP/WTA trouvé aujourd'hui. Utilisation de joueurs simulés pour la démo.")
    players_list = ["Djokovic", "Alcaraz", "Sinner", "Medvedev", "Nadal"]
    col1, col2 = st.sidebar.columns(2)
    with col1:
        player_a = st.selectbox("Joueur A", players_list, index=0)
    with col2:
        player_b = st.selectbox("Joueur B", players_list, index=1)
    tournament = st.sidebar.selectbox("🏆 Tournoi", ["Roland Garros", "Wimbledon", "US Open"])
else:
    # Création de la liste déroulante avec les vrais matchs
    match_labels = [f"{m['home_team']} vs {m['away_team']} - {m['commence_time'].strftime('%H:%M')}" for m in matches]
    selected_match_label = st.sidebar.selectbox("📅 Match du jour (ATP/WTA)", match_labels)
    
    selected_index = match_labels.index(selected_match_label)
    match_info = matches[selected_index]
    player_a = match_info['home_team']
    player_b = match_info['away_team']
    tournament = "Tournoi en cours"  # L'API ne donne pas le nom du tournoi directement, on garde un placeholder

st.sidebar.markdown("---")
st.sidebar.caption(f"🕒 Dernière mise à jour : {pd.Timestamp.now().strftime('%H:%M:%S')}")

# ---- INITIALISATION DES CONTEXTES ----
analyzer_a = TennisContextAnalyzer(player_a, tournament)
analyzer_b = TennisContextAnalyzer(player_b, tournament)
data_a = analyzer_a.get_full_context()
data_b = analyzer_b.get_full_context()

# ---- ALERTE VALUE ----
diff_mental = data_a['scores']['mental_global'] - data_b['scores']['mental_global']
if abs(diff_mental) > 15:
    st.markdown(f"""
    <div class="alert-box">
        ⚡ ALERTE VALUE : {player_a if diff_mental > 0 else player_b} 
        a un avantage contextuel de {abs(diff_mental)}% sur son adversaire.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("---")

# ---- ONGLETS ----
tab1, tab2 = st.tabs(["📊 Prix & Marché", "🧠 Profil & Contexte (Aladdin)"])

with tab1:
    st.subheader(f"Analyse des Cotes : {player_a} vs {player_b}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"📈 Cote {player_a}", value=f"{random.uniform(1.5, 3.0):.2f}", delta="Edge +3.2%")
        st.progress(0.65, text="Probabilité estimée : 65%")
    with col2:
        st.metric(label=f"📈 Cote {player_b}", value=f"{random.uniform(1.5, 3.0):.2f}", delta="Edge -1.8%")
        st.progress(0.45, text="Probabilité estimée : 45%")
    st.caption("💡 Pinnacle (référence sans foule) vs Bookmakers Soft")

with tab2:
    st.subheader(f"🧠 Contexte détaillé : {player_a} vs {player_b}")
    
    # Joueur A
    st.markdown(f"### 🔵 Profil de {player_a}")
    cols_a = st.columns(4)
    scores_a = data_a['scores']
    with cols_a[0]:
        st.plotly_chart(create_gauge(scores_a['fatigue'], "✈️ Fatigue Voyage", max_val=100, reverse=True), use_container_width=True)
    with cols_a[1]:
        st.plotly_chart(create_gauge(scores_a['hotel_confort'], "🏨 Confort Hôtel", max_val=100), use_container_width=True)
    with cols_a[2]:
        st.plotly_chart(create_gauge(scores_a['buzz'], "🔥 Buzz Média", max_val=100), use_container_width=True)
    with cols_a[3]:
        st.plotly_chart(create_gauge(scores_a['social_sentiment'], "📱 Sentiment Social", max_val=100), use_container_width=True)
    
    with st.expander(f"📸 Voir les 5 derniers posts Instagram de {player_a}"):
        posts_a = data_a['instagram']['posts']
        if posts_a:
            for i, post in enumerate(posts_a):
                sentiment_color = "🟢" if post['sentiment'] > 0.1 else "🔴" if post['sentiment'] < -0.1 else "🟡"
                st.write(f"{sentiment_color} **Post {i+1}** : Sentiment {post['sentiment']:.2f}")
                st.caption(f"Légende : {post['caption'][:80]}...")
        else:
            st.write("Aucun post récupéré.")
    
    st.markdown("---")
    
    # Joueur B
    st.markdown(f"### 🔴 Profil de {player_b}")
    cols_b = st.columns(4)
    scores_b = data_b['scores']
    with cols_b[0]:
        st.plotly_chart(create_gauge(scores_b['fatigue'], "✈️ Fatigue Voyage", max_val=100, reverse=True), use_container_width=True)
    with cols_b[1]:
        st.plotly_chart(create_gauge(scores_b['hotel_confort'], "🏨 Confort Hôtel", max_val=100), use_container_width=True)
    with cols_b[2]:
        st.plotly_chart(create_gauge(scores_b['buzz'], "🔥 Buzz Média", max_val=100), use_container_width=True)
    with cols_b[3]:
        st.plotly_chart(create_gauge(scores_b['social_sentiment'], "📱 Sentiment Social", max_val=100), use_container_width=True)

    with st.expander(f"📸 Voir les 5 derniers posts Instagram de {player_b}"):
        posts_b = data_b['instagram']['posts']
        if posts_b:
            for i, post in enumerate(posts_b):
                sentiment_color = "🟢" if post['sentiment'] > 0.1 else "🔴" if post['sentiment'] < -0.1 else "🟡"
                st.write(f"{sentiment_color} **Post {i+1}** : Sentiment {post['sentiment']:.2f}")
                st.caption(f"Légende : {post['caption'][:80]}...")
        else:
            st.write("Aucun post récupéré.")
    
    st.markdown("---")
    col_final1, col_final2, col_final3 = st.columns(3)
    with col_final1:
        st.metric("🏅 Score Contextuel Global", f"{data_a['scores']['mental_global']}/100", f"{data_a['scores']['mental_global'] - data_b['scores']['mental_global']:.1f} vs {player_b}")
    with col_final2:
        st.metric("📰 Articles récents", f"{data_a['news']['article_count']}", f"{data_b['news']['article_count']} pour {player_b}")
    with col_final3:
        st.metric("📱 Sentiment Instagram Moyen", f"{data_a['instagram']['avg_sentiment']:.2f}", f"{data_b['instagram']['avg_sentiment']:.2f} pour {player_b}")