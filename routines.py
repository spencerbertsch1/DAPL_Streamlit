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
import matplotlib.pyplot as plt

# define path to data (pathlib works on any operating system)
PATH_TO_THIS_FILE: Path = Path(__file__).resolve()
ABSPATH_TO_DATA: Path = PATH_TO_THIS_FILE.parent / "MyData"
ABSPATH_TO_CREDENTIALS: Path = PATH_TO_THIS_FILE.parent.parent / "spotify_app_credentials.json"


class SpotData():

    def __init__(self):
        self.streaming_history = self.read_streaming_history()
        self.library = self.read_library()

    def read_streaming_history(self) -> pd.DataFrame:
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


    def read_library(self) -> pd.DataFrame:
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

        # read in only the 'tracks' data and drop everything else 
        df = pd.json_normalize(data, 'tracks')

        # rename some of the columns 
        df = df.rename(columns={'artist': 'artistName', 'track': 'trackName'})

        # add a unique key for each song which is the string concatenation of the 'artist' + 'song' 
        df['artist_and_song'] = df['artistName'] + ' - ' + df['trackName']

        # filter to only the columns we need 
        df = df[['artistName', 'trackName', 'artist_and_song']]

        return df


def barchart(df: pd.DataFrame):
    """
    Little function to create a nice bar chart in matplotlib
    This function is currently not being used because plotly charts look much nicer in Streamlit, but 
    we can still leave the matplotlib code in here. 

    :param: df - pandas dataframe containing the columns ['artist_and_song', 'Count']
    :return: fig and ax for the resulting matplotlib.pylot figure 
    """
    d = dict(zip(df.artist_and_song, df.Count))

    x = list(d.keys())
    y = list(d.values())

    fig, ax = plt.subplots(figsize =(12, 6), dpi=1000)
    ax.barh(x, y, color='blue')
    ax.set_xlabel("Play Count", fontsize = 12)
    ax.set_title("Most Streamed Songs Over the Past Year", fontsize = 14)

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5,
                str(round((i.get_width()), 2)),
                fontsize = 10, fontweight ='bold',
                color ='grey')

    # --- Add an optional annotation to the plot ---
    # fig.text(0.85, 0.15, 'DAPL 2022', fontsize = 15,
    #          color ='grey', ha ='right', va ='bottom',
    #          alpha = 0.7)

    # Show top values
    ax.invert_yaxis()

    ax.grid()

    return (fig, ax)


def load_audio_features():
    # TODO change this to reflect true path vvv
    fpath: Path = ABSPATH_TO_DATA / 'audio_features_old.csv'
    df: pd.DataFrame = pd.read_csv(fpath, sep=',')
    return df

# some test code 
if __name__ == "__main__":
    sd = SpotData()

    print('something')
