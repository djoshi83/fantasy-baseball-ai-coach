
import pandas as pd
import requests
import datetime

# Automatically add UTIL for hitters
def ensure_util(pos_list):
    if "SP" not in pos_list and "RP" not in pos_list:
        if "UTIL" not in pos_list:
            pos_list.append("UTIL")
    return pos_list

# Load and parse the roster
def load_roster(file_path="roster.csv"):
    df = pd.read_csv(file_path)

    # Parse position lists and add UTIL where needed
    df["Eligible_Positions"] = df["Eligible_Positions"].apply(
        lambda x: ensure_util([pos.strip() for pos in x.split(",")])
    )

    # Separate hitters and pitchers
    pitchers = df[df["Eligible_Positions"].apply(lambda pos_list: any(p in ["SP", "RP"] for p in pos_list))]
    hitters = df[~df.index.isin(pitchers.index)]

    # 🔍 Print for debugging
   # print("\n🧪 Parsed Eligible Positions:")
   # print(df[["Name", "Eligible_Positions", "Team"]])
    
    return hitters, pitchers

# Display it
def display_roster():
    hitters, pitchers = load_roster()

    print("\n📋 Your Hitters:")
    for _, row in hitters.iterrows():
        print(f"{row['Name']} — {', '.join(row['Eligible_Positions'])} ({row['Team']})")

    print("\n⚾ Your Pitchers:")
    for _, row in pitchers.iterrows():
        print(f"{row['Name']} — {', '.join(row['Eligible_Positions'])} ({row['Team']})")


def get_probable_pitchers():
    today = "2024-07-09" #datetime.datetime.today().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&hydrate=probablePitcher(note,stats)"

    response = requests.get(url)
    data = response.json()

    pitcher_lookup = {}

    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            teams = game.get("teams", {})

            # Home pitcher
            home_team = teams["home"]["team"]["name"]
            home_pitcher = teams["home"].get("probablePitcher", {})
            print("\n🔍 Home Pitcher Raw JSON:")
            print(home_pitcher)
            break  # Just stops the loop after first game
            if home_pitcher:
                pitcher_lookup[home_team] = {
                    "name": home_pitcher.get("fullName", "Unknown"),
                    "hand": home_pitcher.get("hand", {}).get("description", "?"),
                    "era": extract_era(home_pitcher)
                }

            # Away pitcher
            away_team = teams["away"]["team"]["name"]
            away_pitcher = teams["away"].get("probablePitcher", {})
            if away_pitcher:
                pitcher_lookup[away_team] = {
                    "name": away_pitcher.get("fullName", "Unknown"),
                    "hand": home_pitcher.get("hand", {}).get("description", "?"),
                    "era": extract_era(away_pitcher)
                }

    return pitcher_lookup

def extract_era(pitcher):
    stats = pitcher.get("stats", [])
    for entry in stats:
        # Some versions use 'type': {'displayName': 'statsSingleSeason'}
        if entry.get("type", {}).get("displayName", "").lower() in ["season", "statssingleseason"]:
            era = entry.get("stats", {}).get("era")
            if era is not None:
                try:
                    return float(era)
                except ValueError:
                    return -1
    return -1



if __name__ == "__main__":
    display_roster()

pitchers = get_probable_pitchers()
print("\n🎯 Today's Probable Pitchers by Team:")
for team, info in pitchers.items():
    print(f"{team}: {info['name']} ({info['hand']}-handed, ERA: {info['era']})")