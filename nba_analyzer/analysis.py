"""Data analysis and manipulation functions."""

from datetime import datetime
import pandas as pd


def get_team_win_loss_trend(stats_df: pd.DataFrame) -> pd.DataFrame:
    """Extracts and formats win/loss data from a team's yearly stats."""
    # This is a placeholder for your analysis logic.
    return stats_df[["YEAR", "WINS", "LOSSES", "WIN_PCT"]]

def process_player_gamelog(stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a GAME_LOCATION column to the player game log DataFrame.
    The MATCHUP column is like 'BOS vs. PHI' (home) or 'BOS @ MIA' (away).
    """
    if 'MATCHUP' in stats_df.columns:
        stats_df['LOCATION'] = stats_df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')
    return stats_df

def generate_seasons_list() -> list[str]:
    """Generates a list of seasons from 1996-97 to the current season."""
    current_year = datetime.now().year
    # If it's before October, the current season is the previous year's
    start_year = current_year -1 if datetime.now().month < 10 else current_year
    seasons = [f"{year}-{str(year+1)[-2:]}" for year in range(1996, start_year + 1)]
    return sorted(seasons, reverse=True)