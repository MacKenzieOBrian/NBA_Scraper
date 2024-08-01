# NBA Scraper

This project is designed to scrape and parse NBA game data from HTML files. It includes scripts for both scraping the data (`Scrape2.py`) and parsing the scraped data (`ParseScrape2.py`).

## Files

### Scrape2.py

The `Scrape2.py` script is responsible for scraping NBA game data from a specified source. It collects the raw HTML data for each game and saves it into a directory for further processing. This script ensures that all necessary game data is collected and stored in a structured manner.

### ParseScrape2.py

The `ParseScrape2.py` script is responsible for parsing the HTML files collected by `Scrape2.py`. It processes the HTML to extract meaningful game statistics and compiles them into a structured format, such as a DataFrame. Key functions in this script include:

- **parse_html(box_score)**: Reads an HTML file and uses BeautifulSoup to parse the content, removing unnecessary headers.
- **read_line_score(soup)**: Extracts the line score table from the parsed HTML, renames columns for clarity, and ensures the presence of a 'total' column.

The script processes each HTML file in the specified directory, extracts relevant data, and compiles it into a structured format for analysis.

## Usage

1. **Scrape Data**: Run `Scrape2.py` to scrape the NBA game data and save the HTML files.
2. **Parse Data**: Run `ParseScrape2.py` to parse the saved HTML files and extract game statistics.

## Requirements

- Python 3.x
- BeautifulSoup4
- pandas
- lxml

