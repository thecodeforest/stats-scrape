from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import requests

def _scrape_player_ids(url: str, season_year: int) -> Tag:
    """Scrapes player ids from the given url and season year.

    Args:
        url (str): The url to scrape player ids from.
        season_year (int): The season year to scrape player ids from.

    Returns:
        Tag: The BeautifulSoup tag of the player table.
    """
    response = requests.get(f"{url}/years/{season_year}/fantasy.htm")
    soup = BeautifulSoup(response.content, "html.parser")
    player_table = soup.find_all("table")[0]
    return player_table


def _extract_player_ids(player_table: Tag, season_year: int) -> pd.DataFrame:
    """Extracts player ids from the given player table.

    Args:
        player_table (Tag): The BeautifulSoup tag of the player table.
        season_year (int): The season year to extract player ids from.

    Returns:
        pd.DataFrame: The player names and ids as a dataframe.
    """
    column_names = ["player_name", "player_id"]
    nfl_player_ids = []
    # skip header fields 0-1
    for row in player_table.find_all("tr")[2:]:
        player_data = row.find("td", attrs={"data-stat": "player"})
        if player_data:
            player_name = player_data.a.get_text()
            player_id = player_data.a.get("href")
            player_id_fmt = player_id.split("/")[-1].replace(".htm", "")
            nfl_player_ids.append([player_name, player_id_fmt])
    player_df = pd.DataFrame(nfl_player_ids, columns=column_names)
    player_df["season_year"] = season_year
    return player_df


def create_player_id_df(
    season_year: int, url: str = "https://www.pro-football-reference.com"
) -> pd.DataFrame:
    """Creates a dataframe of player ids and names.

    Args:
        season_year (int): Year of season to scrape player ids from.
        url (str, optional): The url to scrape player ids from. Defaults to "https://www.pro-football-reference.com".

    Returns:
        pd.DataFrame: The player names and ids as a dataframe.
    """
    player_table = _scrape_player_ids(url=url, season_year=season_year)
    player_df = _extract_player_ids(player_table=player_table, season_year=season_year)
    return player_df
