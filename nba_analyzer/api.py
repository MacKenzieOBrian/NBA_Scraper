"""Functions for interacting with the NBA API."""

from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import teamyearbyyearstats, playergamelog
from functools import lru_cache


@lru_cache(maxsize=1)
def get_all_teams():
    """Fetches all NBA teams.
    
    Uses caching to avoid repeated API calls.
    """
    return teams.get_teams()

@lru_cache(maxsize=1)
def get_all_players():
    """Fetches all players."""
    return players.get_players()

@lru_cache(maxsize=1)
def get_active_players():
    """Fetches all active NBA players."""
    return players.get_active_players()

def get_team_id(team_name: str) -> int:
    """Gets the ID for a given team name."""
    team_list = get_all_teams()
    team_info = [t for t in team_list if t["full_name"] == team_name]
    if not team_info:
        raise ValueError(f"Team '{team_name}' not found.")
    return team_info[0]["id"]

def find_player(player_name: str) -> dict:
    """Find a player's info by their full name."""
    player_info = players.find_players_by_full_name(player_name)
    if not player_info:
        raise ValueError(f"Player '{player_name}' not found.")
    return player_info[0]


def get_team_yearly_stats(team_id: int):
    """Fetches year-by-year stats for a given team ID."""
    stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
    return stats.get_data_frames()[0]

def get_player_game_log(player_id: int, season: str):
    """
    Fetches the game log for a specific player and season.
    Returns a pandas DataFrame.
    """
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        return gamelog.get_data_frames()[0]
    except Exception as e:
        raise ConnectionError(f"Could not fetch game log for player ID {player_id}: {e}")