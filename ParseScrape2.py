#Parse into pandas data frame 
import os 
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

SCORES_DIR = "data/scores"
box_scores = os.listdir(SCORES_DIR)
box_scores = [os.path.join(SCORES_DIR, f) for f in box_scores if f.endswith(".html")]

def parse_html(box_score):
    with open(box_score, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, features="lxml")
    [s.decompose() for s in  soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thead")]
    return soup

def read_line_score(soup):
    line_score = pd.read_html(StringIO(str(soup)), attrs={'id': 'line_score'})[0]
    #print("Columns before renaming:", list(line_score.columns))  # Debug print

    cols = list(line_score.columns)
    cols[0] = "team"
    cols[-1] = "total"
    line_score.columns = cols

    #print("Columns after renaming:", list(line_score.columns))  # Debug print

    # Check if 'totals' column exists
    if "total" not in line_score.columns:
        raise KeyError("Column 'total' not found in line_score DataFrame")

    line_score = line_score[["team", "total"]]
    return line_score

def read_stats(soup, team, stat):
    df = pd.read_html(StringIO(str(soup)), attrs={"id": f"box-{team}-game-{stat}"}, index_col=0)[0]
    df = df.apply(pd.to_numeric, errors="coerce")
    return df

def read_season_info(soup):
    nav = soup.select("#bottom_nav_container")[0]
    hrefs = [a["href"] for a in nav.find_all("a")]
    season = os.path.basename(hrefs[1]).split("_")[0]
    return season


base_cols = None
games = []

if not box_scores:
    print("No box scores to process.")
else:
    for box_score in box_scores:
        soup = parse_html(box_score)
        line_score = read_line_score(soup)
        
        # Check if line_score is valid
        if line_score.empty:
            print(f"Line score is empty for box score: {box_score}")
            continue
        
        teams = list(line_score["team"])

        summaries = []
        for team in teams:
            basic = read_stats(soup, team, "basic")
            advanced = read_stats(soup, team, "advanced")
            
            # Check if basic and advanced stats are valid
            if basic.empty or advanced.empty:
                print(f"Stats are empty for team: {team} in box score: {box_score}")
                continue

            totals = pd.concat([basic.iloc[-1,:], advanced.iloc[-1,:]])
            totals.index = totals.index.str.lower()

            basic_max = pd.Series(basic.iloc[-1,:].max(), index=["basic_max"])
            advanced_max = pd.Series(advanced.iloc[-1,:].max(), index=["advanced_max"])

            maxes = pd.concat([basic_max, advanced_max])
            maxes.index = maxes.index.str.lower() + "_max"

            summary = pd.concat([totals, maxes])
            summaries.append(summary)
        
        if summaries:
            summary = pd.concat(summaries, axis=1).T
            game = pd.concat([summary, line_score], axis=1)
            game["home"] = [0, 1]
            game_opp = game.iloc[::-1].reset_index()
            game_opp.columns += "_opp"

            full_game = pd.concat([game, game_opp], axis=1)
            full_game["season"] = read_season_info(soup)
            full_game["date"] = os.path.basename(box_score)[:8]
            full_game["game_id"] = pd.to_datetime(full_game["date"], format="%Y%m%d")
            full_game["won"] = full_game["total"] > full_game["total_opp"]

            games.append(full_game)
            if len(games) % 100 == 0:
                print(f"{len(games)} / {len(box_scores)} processed")

# Check if games list is not empty before concatenating
if games:
    games = pd.concat(games, ignore_index=True)
    print("Writing to CSV...")
    output_csv_path = '/Users/mackenzieobrian/MacDoc/projects/NBA/output.csv'
    games.to_csv(output_csv_path, index=False)
    print(f"CSV file created at {output_csv_path}")
else:
    print("No games data to write to CSV.")




    







