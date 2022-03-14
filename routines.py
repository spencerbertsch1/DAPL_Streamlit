"""
-------------------------------
| Data Analytics Project Lab  |
| Dartmouth College           |  
| Spring 2022                 |
-------------------------------

This file contains a few helper functions needed to load the .json files from spotify to memory using 
pandas, clean and join a few dataframes, grab the genres usingt the Spotify API. We then write the 
resulting dataframe back down to disk as a .csv file. 

This light processing is needed so that we can use the resulting .csv file as the data source for our 
Streamlit Spotify dashboard. 
"""

import pandas as pd
from pathlib import Path

# define path to data (pathlib works on any operating system)
PATH_TO_THIS_FILE: Path = Path(__file__).resolve()
ABSPATH_TO_DATA: Path = PATH_TO_THIS_FILE.parent / "MyData"

def read_streaming_history() -> pd.DataFrame:
    """
    Function to read the three json files as pandas dataframes and concatenate them
    :return: pandas dataframe containing the entire streaming history for the Spotify user 
    """

    dfs = []
    # iterate over each StreamingHistory file in the directory and read them into a pandas dataframe
    for file_number in [0, 1, 2]:
        fname: str = f'StreamingHistory{file_number}.json'
        abspath_to_file: Path = ABSPATH_TO_DATA / fname
        df: pd.DataFrame = pd.read_json(str(abspath_to_file))
        # add the single dataframe to the list outside the loop so we can concatenate it later 
        dfs.append(df)

    # vertically concatenate all the dataframes and return the result 
    streaming_data: pd.DataFrame = pd.concat(dfs, axis=0)

    return streaming_data


if __name__ == "__main__":
    df = read_streaming_history()

    print('something')
