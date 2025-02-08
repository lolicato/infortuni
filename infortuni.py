import streamlit as st
import pandas as pd
import random
import os
import chardet

def extract_team_and_player(filename):
    """Extract team and player names from the filename."""
    parts = filename.replace("-", " ").split("_")
    if len(parts) < 2:
        return None, None
    team = parts[0]
    player = os.path.splitext(parts[1])[0]  # Remove file extension
    return team, player

def detect_encoding(filepath):
    """Detects the encoding of a file."""
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

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
                
                # Detect encoding and read file
                encoding = detect_encoding(filepath)
                df = pd.read_csv(filepath, header=None, skiprows=1, encoding=encoding, dtype=str)
                
                if df.shape[1] > 1:
                    team_players[team].extend(df.iloc[:, 1].dropna().str.encode('latin1').decode('utf-8', 'ignore').tolist())
    
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
    
    # Display results in a table
    st.write("## Selected Players")
    result_df = pd.DataFrame([(team, ", ".join(players)) for team, players in selected_players.items()], columns=["Team", "Selected Players"])
    st.dataframe(result_df)

