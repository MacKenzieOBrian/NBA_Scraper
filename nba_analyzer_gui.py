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
        return team_history.get_data_frame()
    
    def player_game_logs(self, player_name, season):
        """Retrieve game logs for a specific player"""
        player = self.get_player_by_name(player_name)
        if not player:
            raise ValueError(f"Player {player_name} not found")
        
        logs = playergamelog.PlayerGameLog(player_id=player['id'], season=season)
        return logs.get_data_frame()
    
    def get_league_leaders(self, season='2022-23', top_n=5):
        """Get league leaders for various statistics"""
        leaders = leagueleaders.LeagueLeaders(season=season)
        return leaders.get_data_frame()

class NBAAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NBA Data Analyzer")
        self.root.geometry("1200x800")
        self.analyzer = NBADataAnalyzer()
        self.create_layout()
        
    def create_layout(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.team_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.team_tab, text="Team Analysis")
        self.create_team_tab()
        
        self.player_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.player_tab, text="Player Stats")
        self.create_player_tab()
        
        self.leaders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.leaders_tab, text="League Leaders")
        self.create_leaders_tab()
    
    def create_team_tab(self):
        # Left frame for controls
        left_frame = ttk.Frame(self.team_tab, padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Team selection
        ttk.Label(left_frame, text="Select Team:").pack(pady=5)
        self.team_combo = ttk.Combobox(left_frame, width=30)
        self.team_combo['values'] = [team['full_name'] for team in self.analyzer.teams]
        self.team_combo.pack(pady=5)
        
        # Analyze button
        ttk.Button(left_frame, text="Analyze Team", command=self.analyze_team).pack(pady=10)
        
        # Right frame for results
        right_frame = ttk.Frame(self.team_tab, padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create figure for plotting
        self.team_fig, self.team_ax = plt.subplots(figsize=(8, 6))
        self.team_canvas = FigureCanvasTkAgg(self.team_fig, master=right_frame)
        self.team_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create table for stats
        self.team_tree = ttk.Treeview(right_frame, show="headings")
        self.team_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.team_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.team_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_player_tab(self):
        # Left frame for controls
        left_frame = ttk.Frame(self.player_tab, padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Player selection
        ttk.Label(left_frame, text="Select Player:").pack(pady=5)
        self.player_combo = ttk.Combobox(left_frame, width=30)
        self.player_combo['values'] = [player['full_name'] for player in self.analyzer.players]
        self.player_combo.pack(pady=5)
        
        # Season selection
        ttk.Label(left_frame, text="Select Season:").pack(pady=5)
        self.season_combo = ttk.Combobox(left_frame, width=30)
        self.season_combo['values'] = ['2022-23', '2021-22', '2020-21']
        self.season_combo.set('2022-23')
        self.season_combo.pack(pady=5)
        
        # Analyze button
        ttk.Button(left_frame, text="Get Player Stats", command=self.analyze_player).pack(pady=10)
        
        # Right frame for results
        right_frame = ttk.Frame(self.player_tab, padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create table for stats
        self.player_tree = ttk.Treeview(right_frame, show="headings")
        self.player_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.player_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.player_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_leaders_tab(self):
        # Left frame for controls
        left_frame = ttk.Frame(self.leaders_tab, padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Season selection
        ttk.Label(left_frame, text="Select Season:").pack(pady=5)
        self.leaders_season_combo = ttk.Combobox(left_frame, width=30)
        self.leaders_season_combo['values'] = ['2022-23', '2021-22', '2020-21']
        self.leaders_season_combo.set('2022-23')
        self.leaders_season_combo.pack(pady=5)
        
        # Number of players
        ttk.Label(left_frame, text="Number of Players:").pack(pady=5)
        self.top_n_var = tk.StringVar(value="5")
        ttk.Entry(left_frame, textvariable=self.top_n_var, width=10).pack(pady=5)
        
        # Analyze button
        ttk.Button(left_frame, text="Get League Leaders", command=self.show_leaders).pack(pady=10)
        
        # Right frame for results
        right_frame = ttk.Frame(self.leaders_tab, padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create table for stats
        self.leaders_tree = ttk.Treeview(right_frame, show="headings")
        self.leaders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.leaders_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.leaders_tree.configure(yscrollcommand=scrollbar.set)
    
    def analyze_team(self):
        try:
            team_name = self.team_combo.get()
            if not team_name:
                messagebox.showerror("Error", "Please select a team")
                return
            
            # Get team history
            df = self.analyzer.analyze_team_history(team_name)
            
            # Update table
            self.team_tree["columns"] = list(df.columns)
            for col in df.columns:
                self.team_tree.heading(col, text=col)
                self.team_tree.column(col, width=100)
            
            # Clear existing items
            for item in self.team_tree.get_children():
                self.team_tree.delete(item)
            
            # Add data
            for idx, row in df.iterrows():
                self.team_tree.insert("", tk.END, values=list(row))
            
            # Update plot
            self.team_ax.clear()
            self.team_ax.plot(df['YEAR'], df['WINS'], label='Wins', marker='o')
            self.team_ax.plot(df['YEAR'], df['LOSSES'], label='Losses', marker='o')
            self.team_ax.set_title(f'{team_name} Historical Performance')
            self.team_ax.set_xlabel('Year')
            self.team_ax.set_ylabel('Number of Games')
            self.team_ax.legend()
            self.team_ax.tick_params(axis='x', rotation=45)
            self.team_fig.tight_layout()
            self.team_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def analyze_player(self):
        try:
            player_name = self.player_combo.get()
            season = self.season_combo.get()
            
            if not player_name or not season:
                messagebox.showerror("Error", "Please select a player and season")
                return
            
            # Get player stats
            df = self.analyzer.player_game_logs(player_name, season)
            
            # Update table
            self.player_tree["columns"] = list(df.columns)
            for col in df.columns:
                self.player_tree.heading(col, text=col)
                self.player_tree.column(col, width=100)
            
            # Clear existing items
            for item in self.player_tree.get_children():
                self.player_tree.delete(item)
            
            # Add data
            for idx, row in df.iterrows():
                self.player_tree.insert("", tk.END, values=list(row))
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_leaders(self):
        try:
            season = self.leaders_season_combo.get()
            top_n = int(self.top_n_var.get())
            
            if not season:
                messagebox.showerror("Error", "Please select a season")
                return
            
            # Get league leaders
            df = self.analyzer.get_league_leaders(season, top_n)
            
            # Update table
            self.leaders_tree["columns"] = list(df.columns)
            for col in df.columns:
                self.leaders_tree.heading(col, text=col)
                self.leaders_tree.column(col, width=100)
            
            # Clear existing items
            for item in self.leaders_tree.get_children():
                self.leaders_tree.delete(item)
            
            # Add data
            for idx, row in df.iterrows():
                self.leaders_tree.insert("", tk.END, values=list(row))
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]NBA Data Analyzer[/bold blue]\n"
        "A tool for analyzing NBA team and player statistics",
        title="Welcome",
        subtitle="Loading application..."
    ))
    
    app = NBAAnalyzerGUI()
    app.run() 