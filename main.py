import streamlit as st
import pandas as pd
import requests
import datetime

selected_date = st.date_input("Choose a date", datetime.date.today())
formatted_date = str(selected_date)

@st.cache_data(show_spinner=False)
def get_probable_pitchers(date_str: str):
    ...

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={formatted_date}&hydrate=probablePitcher"
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    response = requests.get(url)
    data = response.json()

    pitcher_lookup = {}

    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            teams = game.get("teams", {})

            # Home team
            home_team = teams["home"]["team"]["name"]
            home_pitcher = teams["home"].get("probablePitcher", {})
            if home_pitcher:
                pitcher_lookup[home_team] = home_pitcher.get("fullName", "Unknown")

            # Away team
            away_team = teams["away"]["team"]["name"]
            away_pitcher = teams["away"].get("probablePitcher", {})
            if away_pitcher:
                pitcher_lookup[away_team] = away_pitcher.get("fullName", "Unknown")

    return pitcher_lookup
    # 🚀 Pull and display pitchers
st.subheader("🎯 Probable Pitchers")
pitchers = get_probable_pitchers(formatted_date)
for team, pitcher_name in pitchers.items():
    st.write(f"{team}: {pitcher_name}")
st.title("Fantasy Baseball AI Agent")
st.write("This tool helps you decide who to start and sit based on daily matchups.")

# --- Load and parse roster.csv ---
@st.cache_data
def load_roster():
    df = pd.read_csv("roster.csv")
    df["Eligible_Positions"] = df["Eligible_Positions"].apply(lambda x: [pos.strip() for pos in x.split(",")])
    hitters = df[df["Eligible_Positions"].apply(lambda pos: "SP" not in pos and "RP" not in pos)].copy()
    pitchers = df[~df.index.isin(hitters.index)].copy()
    return hitters, pitchers

hitters, pitchers = load_roster()

# --- Display hitters ---
st.subheader("📋 Your Hitters")
for _, row in hitters.iterrows():
    st.write(f"{row['Name']} — {', '.join(row['Eligible_Positions'])} ({row['Team']})")

# --- Display pitchers ---
st.subheader("⚾ Your Pitchers")
for _, row in pitchers.iterrows():
    st.write(f"{row['Name']} — {', '.join(row['Eligible_Positions'])} ({row['Team']})")

# --- Display today's probable pitchers ---
st.subheader("🎯 Next Scheduled Probable Pitchers")
pitchers = get_probable_pitchers(formatted_date)

for team, pitcher_name in pitchers.items():
    st.write(f"{team}: {pitcher_name}")
# ==============================
# 🔒 Original Replit Logic Below
# ==============================

# """
# import requests
# import datetime

# def ensure_util(df):
#     df["Eligible_Positions"] = df["Eligible_Positions"].apply(lambda pos: [p.strip() for p in pos])
#     df["Eligible_Positions"] = df["Eligible_Positions"].apply(
#         lambda pos: pos + ["UTIL"] if "SP" not in pos and "RP" not in pos and "UTIL" not in pos else pos
#     )
#     return df

# def get_probable_pitchers():
#     today = datetime.datetime.today().strftime('%Y-%m-%d')
#     url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&hydrate=probablePitcher(note,stats)"
#     response = requests.get(url)
#     data = response.json()

#     pitcher_lookup = {}

#     for date_info in data.get("dates", []):
#         for game in date_info.get("games", []):
#             teams = game.get("teams", {})
#             home_team = teams["home"]["team"]["name"]
#             home_pitcher = teams["home"].get("probablePitcher", {})
#             if home_pitcher:
#                 pitcher_lookup[home_team] = {
#                     "name": home_pitcher.get("fullName", "Unknown"),
#                     "id": home_pitcher.get("id", -1)
#                 }
#             away_team = teams["away"]["team"]["name"]
#             away_pitcher = teams["away"].get("probablePitcher", {})
#             if away_pitcher:
#                 pitcher_lookup[away_team] = {
#                     "name": away_pitcher.get("fullName", "Unknown"),
#                     "id": away_pitcher.get("id", -1)
#                 }
#     return pitcher_lookup

# if __name__ == "__main__":
#     display_roster()
#     pitchers = get_probable_pitchers()
#     print(pitchers)
# """

