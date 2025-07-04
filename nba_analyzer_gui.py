import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import teamyearbyyearstats, playergamelog, leagueleaders
from nba_api.stats.library.parameters import SeasonAll
import logging
from rich.console import Console
from rich.panel import Panel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nba_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nba_analyzer")

console = Console()

class NBADataAnalyzer:
    def __init__(self):
        """Initialize the NBA Data Analyzer"""
        self.teams = teams.get_teams()
        self.players = players.get_players()
    
    def get_team_by_name(self, team_name):
        """Find a team's ID by its name"""
        matching_teams = [team for team in self.teams 
                         if team_name.lower() in team['full_name'].lower()]
        return matching_teams[0] if matching_teams else None
    
    def get_player_by_name(self, player_name):
        """Find a player's ID by their name"""
        matching_players = [player for player in self.players 
                          if player_name.lower() in player['full_name'].lower()]
        return matching_players[0] if matching_players else None
    
    def analyze_team_history(self, team_name):
        """Analyze a team's historical performance"""
        team = self.get_team_by_name(team_name)
        if not team:
            raise ValueError(f"Team {team_name} not found")
        
        team_history = teamyearbyyearstats.TeamYearByYearStats(team_id=team['id'])
        return team_history.get_data_frames()[0] # get_data_frames returns a list of dataframes
    
    def player_game_logs(self, player_name, season):
        """Retrieve game logs for a specific player"""
        player = self.get_player_by_name(player_name)
        if not player:
            raise ValueError(f"Player {player_name} not found")
        
        logs = playergamelog.PlayerGameLog(player_id=player['id'], season=season)
        return logs.get_data_frames()[0] # get_data_frames returns a list of dataframes
    
    def get_league_leaders(self, season='2022-23', top_n=5):
        """Get league leaders for various statistics"""
        leaders = leagueleaders.LeagueLeaders(season=season)
        return leaders.get_data_frames()[0]

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]NBA Data Analyzer[/bold blue]\n"
        "A tool for analyzing NBA team and player statistics",
        title="Welcome",
        subtitle="Starting command-line analysis..."
    ))

    analyzer = NBADataAnalyzer()

    # Example: Analyze a team's history
    team_name_to_analyze = 'Los Angeles Lakers'
    console.print(f"\nAnalyzing historical data for [bold]{team_name_to_analyze}[/bold]...")
    try:
        team_data = analyzer.analyze_team_history(team_name_to_analyze)
        if team_data is not None:
            console.print(f"\nHistorical Data for [bold]{team_name_to_analyze}[/bold]:")
            console.print(team_data.head()) # Print the first few rows
        else:
            console.print(f"Could not retrieve data for [bold]{team_name_to_analyze}[/bold].")
    except ValueError as e:
        console.print(f"Error: {e}")

    # Example: Get game logs for a player
    player_name_to_analyze = 'LeBron James'
    season_to_analyze = '2022-23'
    console.print(f"\nGetting game logs for [bold]{player_name_to_analyze}[/bold] in season [bold]{season_to_analyze}[/bold]...")
    try:
        player_logs = analyzer.player_game_logs(player_name_to_analyze, season_to_analyze)
        if player_logs is not None:
            console.print(f"\nGame Logs for [bold]{player_name_to_analyze}[/bold] ({season_to_analyze}):")
            console.print(player_logs.head()) # Print the first few rows
        else:
            console.print(f"Could not retrieve game logs for [bold]{player_name_to_analyze}[/bold].")
    except ValueError as e:
        console.print(f"Error: {e}")

    # Example: Get league leaders
    leaders_season = '2022-23'
    top_n_leaders = 10 # Get top 10 leaders
    console.print(f"\nGetting top [bold]{top_n_leaders}[/bold] league leaders for season [bold]{leaders_season}[/bold]...")
    try:
        league_leaders_data = analyzer.get_league_leaders(leaders_season, top_n_leaders)
        if league_leaders_data is not None:
            console.print(f"\nTop [bold]{top_n_leaders}[/bold] League Leaders ({leaders_season}):")
            console.print(league_leaders_data.head(top_n_leaders)) # Print the top N rows
        else:
            console.print(f"Could not retrieve league leaders for season [bold]{leaders_season}[/bold].")
    except Exception as e:
        console.print(f"Error: {e}")
