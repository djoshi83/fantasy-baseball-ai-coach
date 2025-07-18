import streamlit as st
import pandas as pd
import requests
import datetime

TEAM_NAME_MAP = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KC":  "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SD":  "San Diego Padres",
    "SEA": "Seattle Mariners",
    "SF":  "San Francisco Giants",
    "STL": "St. Louis Cardinals",
    "TB":  "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSH": "Washington Nationals"
}

def get_opponent_team(team_name, schedule_data):
    for date_info in schedule_data.get("dates", []):
        for game in date_info.get("games", []):
            home = game["teams"]["home"]["team"]["name"]
            away = game["teams"]["away"]["team"]["name"]
            if team_name == home:
                return away
            elif team_name == away:
                return home
    return "Unknown"
# @st.cache_data
# def get_pitcher_details(pitcher_id: int):
 #   url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}?hydrate=stats(group=[pitching],type=[season])"
#    response = requests.get(url)
 #   data = response.json()

#    person = data.get("people", [{}])[0]
#    name = person.get("fullName", "Unknown")
#    hand = person.get("pitchHand", {}).get("abbreviation", "?")
#    st.text(f"{name}: hand = {hand}")
#    era = None
@st.cache_data
def get_pitcher_details(pitcher_id: int):
    url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}?hydrate=stats(group=[pitching],type=[season])"
    response = requests.get(url)
    data = response.json()

    person = data.get("people", [{}])[0]
    name = person.get("fullName", "Unknown")

    # ✅ Correct way to pull hand (we now know it's "code")
    hand = person.get("pitchHand", {}).get("code", "?")

    # ERA handling (already working)
    era = None
    for stat in person.get("stats", []):
        for split in stat.get("splits", []):
            era = split.get("stat", {}).get("era", None)
            break

    return {
        "name": name,
        "hand": hand,
        "era": era
    }


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
                pitcher_lookup[home_team] = {
                "name": home_pitcher.get("fullName", "Unknown"),
                "id": home_pitcher.get("id", -1)
}


            # Away team
            away_team = teams["away"]["team"]["name"]
            away_pitcher = teams["away"].get("probablePitcher", {})
            if away_pitcher:
                pitcher_lookup[away_team] = {
                "name": away_pitcher.get("fullName", "Unknown"),
                "id": away_pitcher.get("id", -1)
}


    return pitcher_lookup, data
    # 🚀 Pull and display pitchers
#st.subheader("🎯 Probable Pitchers")
#pitchers = get_probable_pitchers(formatted_date)

#for team, pitcher_name in pitchers.items():
#    st.write(f"{team}: {pitcher_name}")
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
st.subheader("🎯 Probable Pitchers")

for team, pitcher_data in pitchers.items():
    if isinstance(pitcher_data, dict) and "name" in pitcher_data:
        st.write(f"{team}: {pitcher_data['name']}")
    else:
        st.write(f"{team}: {pitcher_data}")


st.subheader("🧠 Matchups: Your Hitters vs Opposing Pitchers")
for _, row in hitters.iterrows():
    team = row["Team"]
    name = row["Name"]
    full_team_name = TEAM_NAME_MAP.get(team, "Unknown")
    opponent = get_opponent_team(full_team_name, schedule_data)

    pitcher_info = pitchers.get(opponent, None)

    if pitcher_info and pitcher_info["id"] != -1:
        pitcher_stats = get_pitcher_details(pitcher_info["id"])
        display = f"{name} ({team}) is facing {opponent} — {pitcher_stats['name']} ({pitcher_stats['hand']}HP, {pitcher_stats['era']} ERA)"
    else:
        display = f"{name} ({team}) is facing {opponent} — Unknown Pitcher"

    st.write(display)


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

