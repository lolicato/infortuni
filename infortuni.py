import streamlit as st
import pandas as pd
import random
import os
import re

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
            # Skip empty files
            if os.path.getsize(filepath) == 0:
                st.warning(f"Skipping empty file: {filename}")
                continue

            team, player = extract_team_and_player(filename)
            if team and player:
                if team not in team_players:
                    team_players[team] = []

                df = None
                for encoding in ['utf-8', 'ISO-8859-1', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, header=None, skiprows=1, encoding=encoding, dtype=str)
                        break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError, IndexError):
                        continue

                if df is None or df.shape[1] <= 2:
                    st.warning(f"Skipping file due to format issues: {filename}")
                    continue

                try:
                    df.iloc[:, 1] = df.iloc[:, 1].dropna().astype(str).map(
                        lambda x: x.encode(encoding, errors='ignore').decode('utf-8', errors='ignore').strip()
                    )
                    df.iloc[:, 2] = df.iloc[:, 2].dropna().astype(str).map(lambda x: x.strip())

                    df = df.dropna(subset=[1, 2])
                    df = df[df.iloc[:, 2] != "PT"]
                    players_list = df.apply(lambda row: f"{row.iloc[1]} ({row.iloc[2]})", axis=1).tolist()

                    players_list = [p.replace("TM(", " (") for p in players_list]
                    players_list = [p.replace(" ", "") for p in players_list]
                    players_list = [re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', p) for p in players_list]

                    team_players[team].extend(players_list)

                except Exception as e:
                    st.warning(f"Failed processing file {filename}: {e}")

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

directory = "./server_files"  # Update this path as needed
team_players = process_files(directory)

# Interactive selection of min and max players
min_players = st.slider("Minimum Players to Select", 0, 10, 0)
max_players = st.slider("Maximum Players to Select", 0, 10, 2)

if min_players > max_players:
    st.error("Minimum players cannot be greater than maximum players.")

target_button = st.button("Generate Random Players")

if target_button:
    selected_players = select_random_players(team_players, min_players, max_players)

    if not selected_players:
        st.info("No players found or selected.")
    else:
        max_players_selected = max(len(players) for players in selected_players.values())
        columns = ["Team"] + [f"Player {i+1}" for i in range(max_players_selected)]
        result_data = []

        for team, players in selected_players.items():
            row = [team] + players + [""] * (max_players_selected - len(players))
            result_data.append(row)

        result_df = pd.DataFrame(result_data, columns=columns)
        st.write("## Selected Players")
        st.dataframe(result_df, height=800, use_container_width=True)