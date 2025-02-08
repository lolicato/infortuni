import streamlit as st
import pandas as pd
import random
import os

def extract_team_and_player(filename):
    """Extract team and player names from the filename."""
    parts = filename.replace("-", " ").split("_")
    if len(parts) < 2:
        return None, None
    team = parts[0]
    player = os.path.splitext(parts[1])[0]  # Remove file extension
    return team, player

def process_files(directory):
    """Processes files from a specified server directory and organizes data by team."""
    team_players = {}
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            team, player = extract_team_and_player(filename)
            if team and player:
                if team not in team_players:
                    team_players[team] = []
                
                # Read file and extract relevant columns, ignoring the first row
                for encoding in ['utf-8', 'ISO-8859-1', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, header=None, skiprows=1, encoding=encoding, dtype=str)
                        df.iloc[:, 1] = df.iloc[:, 1].dropna().astype(str).map(lambda x: x.encode(encoding, errors='ignore').decode('utf-8', errors='ignore')
                        df.iloc[:, 2] = df.iloc[:, 2].dropna().astype(str).map(lambda x: x.replace(" ", "").strip())
                        break
                    except (UnicodeDecodeError, IndexError):
                        continue
                
                if df.shape[1] > 2:  # Ensure the third column exists
                    df = df.dropna(subset=[1, 2])  # Ensure valid rows
                    df = df[df.iloc[:, 2] != "PT"]  # Exclude players marked as PT
                    players_list = df.apply(lambda row: f"{row.iloc[1]}({row.iloc[2]})", axis=1).tolist()
                    players_list = [p.replace("TM(", " (") for p in players_list]  # Fix formatting issue
                    team_players[team].extend(players_list)
    
    return team_players

def select_random_players(team_players, min_players, max_players):
    """Randomly selects a variable number of players per team."""
    selected_players = {}
    for team, players in team_players.items():
        num_selected = random.randint(min_players, max_players)
        selected_players[team] = random.sample(players, min(num_selected, len(players)))
    return selected_players

# Streamlit UI
st.title("Random Team Player Selector")

directory = "./server_files"  # Update with actual path to server files
team_players = process_files(directory)

# Interactive selection of min and max players
min_players = st.slider("Minimum Players to Select", 0, 3, 0)
max_players = st.slider("Maximum Players to Select", 0, 3, 3)

target_button = st.button("Generate Random Players")

if target_button:
    selected_players = select_random_players(team_players, min_players, max_players)
    
    # Format results with each selected player in a different column
    max_players_selected = max(len(players) for players in selected_players.values()) if selected_players else 0
    columns = ["Team"] + [f"Player {i+1}" for i in range(max_players_selected)]
    result_data = []
    
    for team, players in selected_players.items():
        row = [team] + players + ["" for _ in range(max_players_selected - len(players))]  # Fill empty columns
        result_data.append(row)
    
    result_df = pd.DataFrame(result_data, columns=columns)
    st.write("## Selected Players")
    
    # Display full table without scrolling
    st.dataframe(result_df, height=800, use_container_width=True)

