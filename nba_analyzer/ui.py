"""GUI components for the NBA Data Analyzer."""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from . import api, analysis

class DataDisplayFrame(ttk.Frame):
    """A reusable frame for displaying data in a scrollable Treeview table."""
    def __init__(self, parent):
        super().__init__(parent, padding=5)
        self.tree = ttk.Treeview(self, show="headings")

        # Scrollbars
        ysb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def update_data(self, df: pd.DataFrame):
        """Clears the current view and populates it with new data from a DataFrame."""
        self.tree.delete(*self.tree.get_children())

        if df is None or df.empty:
            return

        self.tree["columns"] = list(df.columns)
        self.tree["displaycolumns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

class TeamAnalysisTab(ttk.Frame):
    """GUI Tab for Team Analysis."""
    def __init__(self, parent):
        super().__init__(parent)

        # --- Controls ---
        controls_frame = ttk.LabelFrame(self, text="Team Selection", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(controls_frame, text="Select Team:").pack(side=tk.LEFT, padx=(0, 5))
        team_names = sorted([t["full_name"] for t in api.get_all_teams()])
        self.team_selector = ttk.Combobox(controls_frame, values=team_names, width=30)
        self.team_selector.pack(side=tk.LEFT)
        self.team_selector.bind("<<ComboboxSelected>>", self.load_team_data)

        # --- Data Display ---
        self.data_frame = DataDisplayFrame(self)
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_team_data(self, event=None):
        team_name = self.team_selector.get()
        try:
            team_id = api.get_team_id(team_name)
            raw_stats_df = api.get_team_yearly_stats(team_id)
            display_df = analysis.get_team_win_loss_trend(raw_stats_df)
            self.data_frame.update_data(display_df)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load team data: {e}")
            self.data_frame.update_data(pd.DataFrame())

class PlayerAnalysisTab(ttk.Frame):
    """GUI Tab for Player Game Log Analysis."""
    def __init__(self, parent):
        super().__init__(parent)

        # --- Controls ---
        controls_frame = ttk.LabelFrame(self, text="Player Selection", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(controls_frame, text="Player:").pack(side=tk.LEFT, padx=(0, 5))
        player_names = sorted([p["full_name"] for p in api.get_active_players()])
        self.player_combo = ttk.Combobox(controls_frame, values=player_names, width=25)
        self.player_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(controls_frame, text="Season:").pack(side=tk.LEFT, padx=5)
        self.season_combo = ttk.Combobox(controls_frame, values=analysis.generate_seasons_list(), width=10)
        self.season_combo.pack(side=tk.LEFT, padx=5)
        if self.season_combo['values']:
            self.season_combo.set(self.season_combo['values'][0])

        ttk.Button(controls_frame, text="Get Stats", command=self.load_player_data).pack(side=tk.LEFT, padx=5)

        # --- Data Display ---
        self.data_frame = DataDisplayFrame(self)
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_player_data(self):
        player_name = self.player_combo.get()
        season = self.season_combo.get()

        if not player_name or not season:
            messagebox.showwarning("Input Required", "Please select a player and a season.")
            return

        try:
            player_info = api.find_player(player_name)
            raw_log_df = api.get_player_game_log(player_info['id'], season)
            processed_df = analysis.process_player_gamelog(raw_log_df)

            # Select and reorder columns for better readability
            cols_to_show = [
                'GAME_DATE', 'MATCHUP', 'LOCATION', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', 'FG_PCT',
                'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'MIN'
            ]
            display_df = processed_df[[c for c in cols_to_show if c in processed_df.columns]]
            self.data_frame.update_data(display_df)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load player data: {e}")
            self.data_frame.update_data(pd.DataFrame())

class MainApplication(tk.Tk):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.title("NBA Data Analyzer")
        self.geometry("1200x700")

        # Create a Notebook (tab container)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        team_tab = TeamAnalysisTab(notebook)
        player_tab = PlayerAnalysisTab(notebook)

        # Add tabs to the notebook
        notebook.add(team_tab, text="Team Analysis")
        notebook.add(player_tab, text="Player Game Logs")

def start_app():
    """Initializes and runs the main application."""
    app = MainApplication()
    app.mainloop()