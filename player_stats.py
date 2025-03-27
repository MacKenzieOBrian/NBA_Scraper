import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import logging
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("player_stats.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("player_stats")

console = Console()

class PlayerStatsAnalyzer:
    def __init__(self):
        """Initialize the Player Stats Analyzer"""
        self.players = players.get_players()
        self.active_players = players.get_active_players()
        self.available_seasons = self._generate_seasons()
    
    def _generate_seasons(self):
        """Generate list of available seasons from 1996-97 to current season"""
        current_year = datetime.now().year
        seasons = []
        
        # Start from 1996-97 season
        for year in range(1996, current_year + 1):
            season = f"{year}-{str(year + 1)[-2:]}"
            seasons.append(season)
        
        return seasons
    
    def get_player_by_name(self, player_name):
        """Find a player's ID by their name using the NBA API's search methods"""
        # First try exact match with active players
        matching_players = players.find_players_by_full_name(player_name)
        if matching_players:
            return matching_players[0]
        
        # If no exact match, try partial match with active players
        for player in self.active_players:
            if player_name.lower() in player['full_name'].lower():
                return player
        
        # If still no match, try with all players
        for player in self.players:
            if player_name.lower() in player['full_name'].lower():
                return player
        
        return None
    
    def get_player_stats(self, player_name, season, game_type='all'):
        """Get game logs for a specific player"""
        if season not in self.available_seasons:
            raise ValueError(f"Season {season} is not available. Please select a season from 1996-97 to present.")
        
        player = self.get_player_by_name(player_name)
        if not player:
            raise ValueError(f"Player {player_name} not found")
        
        # Get game logs
        logs = playergamelog.PlayerGameLog(player_id=player['id'], season=season)
        
        # Get the data and convert to DataFrame
        df = pd.DataFrame(logs.get_normalized_dict()['PlayerGameLog'])
        
        # Add a column to indicate if it's a home or away game
        # The MATCHUP column format is either "TEAM vs. OPPONENT" (home) or "TEAM @ OPPONENT" (away)
        df['GAME_LOCATION'] = df.apply(lambda row: 'HOME' if 'vs.' in row['MATCHUP'] else 'AWAY', axis=1)
        
        # Log the distribution of home/away games
        home_games = len(df[df['GAME_LOCATION'] == 'HOME'])
        away_games = len(df[df['GAME_LOCATION'] == 'AWAY'])
        logger.debug(f"Total games: {len(df)}, Home games: {home_games}, Away games: {away_games}")
        
        # Filter based on game type if specified
        if game_type == 'home':
            df = df[df['GAME_LOCATION'] == 'HOME']
        elif game_type == 'away':
            df = df[df['GAME_LOCATION'] == 'AWAY']
        
        return df

class PlayerStatsGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NBA Player Stats")
        self.root.geometry("1000x600")
        self.analyzer = PlayerStatsAnalyzer()
        self.create_layout()
        
    def create_layout(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Player Selection", padding="5")
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Player selection
        ttk.Label(controls_frame, text="Select Player:").pack(side=tk.LEFT, padx=5)
        self.player_combo = ttk.Combobox(controls_frame, width=30)
        # Only show active players in the dropdown
        self.player_combo['values'] = [player['full_name'] for player in self.analyzer.active_players]
        self.player_combo.pack(side=tk.LEFT, padx=5)
        
        # Season selection
        ttk.Label(controls_frame, text="Season:").pack(side=tk.LEFT, padx=5)
        self.season_combo = ttk.Combobox(controls_frame, width=10)
        self.season_combo['values'] = self.analyzer.available_seasons
        # Set default to current season
        current_year = datetime.now().year
        self.season_combo.set(f"{current_year}-{str(current_year + 1)[-2:]}")
        self.season_combo.pack(side=tk.LEFT, padx=5)
        
        # Game type selection
        ttk.Label(controls_frame, text="Game Type:").pack(side=tk.LEFT, padx=5)
        self.game_type_combo = ttk.Combobox(controls_frame, width=10)
        self.game_type_combo['values'] = ['All Games', 'Home Games', 'Away Games']
        self.game_type_combo.set('All Games')
        self.game_type_combo.pack(side=tk.LEFT, padx=5)
        
        # Get Stats button
        ttk.Button(controls_frame, text="Get Stats", command=self.show_player_stats).pack(side=tk.LEFT, padx=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Player Statistics", padding="5")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create table for stats
        self.stats_tree = ttk.Treeview(stats_frame, show="headings")
        self.stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.HORIZONTAL, command=self.stats_tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.stats_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
    
    def show_player_stats(self):
        try:
            player_name = self.player_combo.get()
            season = self.season_combo.get()
            game_type = self.game_type_combo.get().lower().replace(' games', '')
            
            if not player_name or not season:
                messagebox.showerror("Error", "Please select a player and season")
                return
            
            # Get player stats
            df = self.analyzer.get_player_stats(player_name, season, game_type)
            
            # Update table
            self.stats_tree["columns"] = list(df.columns)
            for col in df.columns:
                self.stats_tree.heading(col, text=col)
                self.stats_tree.column(col, width=100)
            
            # Clear existing items
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # Add data
            for idx, row in df.iterrows():
                self.stats_tree.insert("", tk.END, values=list(row))
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]NBA Player Stats[/bold blue]\n"
        "A simple tool for viewing NBA player statistics",
        title="Welcome",
        subtitle="Loading application..."
    ))
    
    app = PlayerStatsGUI()
    app.run() 