# statsscrape.py
import logging
from datetime import datetime
import argparse
import awswrangler as wr
import pandas as pd
from createplayerid import create_player_id_df


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create player id dataframe")
    parser.add_argument("--s3_bucket", type=str, help="s3 bucket name")
    parser.add_argument("--year", type=int, help="Year to create dataframe for")
    parser.add_argument("--debug", type=bool, help="Run in debug mode")
    args = parser.parse_args()
    return args


logging.basicConfig(
    format="%(levelname)s - %(asctime)s - %(filename)s - %(message)s",
    level=logging.INFO,
    filename="player-stats-{start_time}.log".format(
        start_time=datetime.now().strftime("%Y-%m-%d")
    ),
)


def collect_stats():
    args = read_args()
    season_year = args.year
    s3_bucket = args.s3_bucket
    debug = args.debug
    s3_path = f"s3://{s3_bucket}/data/playerstats/raw/{season_year}/playerstats.csv"
    logging.info(f"Writing data to {s3_path}")
    player_id_df = create_player_id_df(season_year=season_year)
    # take the first player returned
    player_name, player_id, _ = player_id_df.iloc[0]
    player_last_name_first_letter = player_name.split()[1][0]
    player_stats_url = f"https://www.pro-football-reference.com/players/{player_last_name_first_letter}/{player_id}.htm"
    # scrape the stats for a single player
    player_stats_df = pd.read_html(player_stats_url)[0]
    # save data to S3
    if debug: 
        player_stats_df.to_csv(f"debug_df_season_{season_year}.csv", index=False)
    else:
        wr.s3.to_csv(player_stats_df, s3_path, index=False)


if __name__ == "__main__":
    collect_stats()
