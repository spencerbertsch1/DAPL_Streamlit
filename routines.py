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
import json

# define path to data (pathlib works on any operating system)
PATH_TO_THIS_FILE: Path = Path(__file__).resolve()
ABSPATH_TO_DATA: Path = PATH_TO_THIS_FILE.parent / "MyData"

def read_streaming_history() -> pd.DataFrame:
    """
    Function to read the StreamHistory json files as pandas dataframes and concatenate them
    
    :param: NA 
    :return: pandas dataframe containing the entire streaming history for the Spotify user 
    """

    dfs = []
    # iterate over each StreamingHistory file in the directory and read them into a pandas dataframe
    # TODO iterate through all the files that start with "streaming"
    for file_number in [0, 1, 2]:
        fname: str = f'StreamingHistory{file_number}.json'
        abspath_to_file: Path = ABSPATH_TO_DATA / fname
        df: pd.DataFrame = pd.read_json(str(abspath_to_file))
        # add the single dataframe to the list outside the loop so we can concatenate it later 
        dfs.append(df)

    # vertically concatenate all the dataframes and return the result 
    streaming_data: pd.DataFrame = pd.concat(dfs, axis=0)

    # add a unique key for each song which is the string concatenation of the 'artist' + 'song' 
    streaming_data['artist_and_song'] = streaming_data['artistName'] + ' - ' + streaming_data['trackName']

    return streaming_data


def read_library() -> pd.DataFrame:
    """
    Function to read the YourLibrary json files as pandas dataframes and concatenate them
    
    :param: NA 
    :return: pandas dataframe containing the entire library for the Spotify user 
    """

    # define the path to the file we want to read in 
    fname: str = f'YourLibrary.json'
    abspath_to_file: Path = ABSPATH_TO_DATA / fname

    # here we need to use json.load() because the file is nested json and we need to index the correct sub-dict 
    with open(str(abspath_to_file)) as data_file:    
        data = json.load(data_file)  

    # read in only the 'tracks' data 
    df = pd.json_normalize(data, 'tracks')

    # rename some of the columns 
    df = df.rename(columns={'artist': 'artistName', 'track': 'trackName'})

    # add a unique key for each song which is the string concatenation of the 'artist' + 'song' 
    df['artist_and_song'] = df['artistName'] + ' - ' + df['trackName']

    # filter to only the columns we need 
    df = df[['artistName', 'trackName', 'artist_and_song']]

    return df


# some test code 
if __name__ == "__main__":
    df1 = read_streaming_history()
    df2 = read_library()

    print('something')
