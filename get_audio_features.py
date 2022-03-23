"""
-------------------------------
| Data Analytics Project Lab  |
| Dartmouth College           |  
| Spring 2022                 |
-------------------------------

This file is designed to use the Spotify API to gather audio features about streamed tracks. The data 
is then saved to disk so that the Spotify API doesn't need to be pinged whenever a user refreshes 
the Streamlit dashboard. 

This script should be run once as a single preprocessing step before the dashboard can be run. 

This script can be run from the command line by running: $ python3 get_audio_features.py
"""

import pandas as pd
from pathlib import Path
import time
import glob
import json
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from routines import SpotData, ABSPATH_TO_CREDENTIALS, ABSPATH_TO_DATA

def main(TEST_MODE: bool = False, chunk_size: int = 50, rows_to_skip: int = 0):
    """
    Function to gather additional attributes about songs and artists using the Spotify API.
    
    :param: TEST_MODE - bool, set to true for development and debugging
    """

    # read the data into memory 
    sd = SpotData()
    streaming_data = sd.streaming_history

    # --- Get Music Genres using Spotify API --- 

    # Opening JSON file
    f = open(str(ABSPATH_TO_CREDENTIALS))  # <-- we don't version this in git
    # returns JSON object containing Spotify credentials as a python dictionary
    creds = json.load(f)
    # Closing file
    f.close()

    CLIENT_ID = creds['Client-ID']
    CLIENT_SECRET = creds['Client-Secret']

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'

    sp = spotipy.Spotify()

    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # grab the total number of songs, we will need this later to track our progress
    n_rows: int = streaming_data.shape[0]

    # Iterate through each song and use Spotify's development APIs to gather energy, loudness, danceability, and genres
    row_list = []
    tic = time.time()

    # define how often we will be updated on the progress
    verbose_frequency = 100
    if TEST_MODE: 
        verbose_frequency = verbose_frequency/10  # <-- we want more frequent updates when running in TEST_MODE

    # this process is pretty slow, so we can use a tiered caching system to speed things up! 
    # each sub-cache maps a track-id to its respective attribute, in the case of genres it's a list
    track_cache = {'genre_cache': {}, 'energy_cache': {}, 'loudness_cache': {}, 'danceability_cache': {}}
    artist_cache = {}  # <-- {artist_uri: [list of genres]}

    for i, row in enumerate(streaming_data.iloc[rows_to_skip:].iterrows()):
        artist = row[1]['artistName']
        track = row[1]['trackName']

        # transpose here so that our column series turns into a row dataframe
        df = row[1].to_frame().T

        track_id_blob = sp.search(q='artist:' + artist + ' track:' + track, type='track')
        # we need to extract the id from the nested dictionary, list, and final dictionary 

        try:
            track_id = track_id_blob['tracks']['items'][0]['id']

            # here we check if we've seen this song before. If we have, then we just use the cached data and move on
            if track_id in track_cache['energy_cache'].keys():
                energy: str = track_cache['energy_cache'][track_id]
                loudness: str = track_cache['loudness_cache'][track_id]
                danceability: str = track_cache['danceability_cache'][track_id]
                genres: list = track_cache['genre_cache'][track_id]

            # if this is a new song (we haven't seen it before), then we gather all the attributes from the Spotify API
            else:
                # actual GET request with proper header
                r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
                r = r.json()

                # get the track attributes we want
                energy = r['energy']
                loudness = r['loudness']
                danceability = r['danceability']

                track_cache['energy_cache'][track_id] = energy
                track_cache['loudness_cache'][track_id] = loudness
                track_cache['danceability_cache'][track_id] = danceability

                # now we can get the genres based on the track_id found above 
                # first we get the artist info
                a = requests.get(BASE_URL + 'tracks/' + track_id, headers=headers)
                a = a.json()
                a_uri = a['artists'][0]['uri'].split(':')[2]

                # Here we check whether or not we have seen this artist before. It's likely that we've already processed a 
                # different song from the same artist, so we use another cache to skip the Spotify API call if that's the case
                if a_uri in artist_cache.keys():
                    genres: list = artist_cache[a_uri]
                    track_cache['genre_cache'][track_id] = genres
                else:
                    g = requests.get(BASE_URL + 'artists/' + a_uri, headers=headers)
                    g = g.json()
                    genres: list = g['genres']
                    # add the new genres to the cache
                    artist_cache[a_uri] = genres
                    # and finally add the new genres to the track cache as well
                    track_cache['genre_cache'][track_id] = genres

            # build the dataframe by adding the newly found atributes
            df['energy'] = energy
            df['loudness'] = loudness
            df['danceability'] = danceability

            # expand the dataframe to create a row for each unique genre in the genre list
            # this is generally not best practice because it's very space inefficient, but the dataframe is small here so it's okay
            for genre in genres:
                df_local = df.copy()
                df_local['genres'] = genre
                row_list.append(df_local)
        
        # if spotify didn't return anything then we log that and continue
        except:
            print(f'Passing... API did not return sufficient information for: {track} by {artist}')

        # keep track of the progress
        if i%verbose_frequency == 0:
            print(f'Time Elapsed: {time.strftime("%H:%M:%S", time.gmtime(time.time() - tic))}, Percent Complete: {round(((i+rows_to_skip)/n_rows), 3)*100}%')

        # we need to store our progress so that we can start from the middle if the process fails
        if i%chunk_size == 0:
            # concatenate all the single row dataframes in the row list
            chunk_stream_history: pd.DataFrame = pd.concat(row_list, axis=0)
            f_name: str = f'audio_features_original_{i}.csv'
            write_path: Path = ABSPATH_TO_DATA / 'audio_features' / f_name
            
            # write the current chunk to disk as a csv file 
            chunk_stream_history.to_csv(write_path, sep=',')
            
            # empty the row list
            row_list = []

        if TEST_MODE:
            if i >= 75:
                break

    # if we have unprocessed records left over, we need to process those here
    if len(row_list) != 0:
            chunk_stream_history: pd.DataFrame = pd.concat(row_list, axis=0)
            f_name: str = 'audio_features_original_leftover.csv'
            write_path: Path = ABSPATH_TO_DATA / 'audio_features' / f_name
            # write the current chunk to disk as a csv file 
            chunk_stream_history.to_csv(write_path, sep=',')

    # read all the chunked pandas dataframes into memory and generate the complete dataframe
    complete_df_list = []
    df_path: Path = ABSPATH_TO_DATA / 'audio_features' / '*.csv'
    chunked_df_path: str = str(df_path)
    for fname in glob.glob(chunked_df_path):
        chunk_df: pd.DataFrame = pd.read_csv(fname, sep=',')
        complete_df_list.append(chunk_df)

    # generate the complete stream history 
    complete_stream_history = pd.concat(complete_df_list, axis=0)
    # filter and order the data here
    complete_stream_history = complete_stream_history[['endTime', 'artistName', 'trackName', 'msPlayed', 'artist_and_song', 'energy', 'loudness', 'danceability', 'genres']]
    complete_stream_history = complete_stream_history.sort_values(by=['endTime', 'artist_and_song'], ascending=True)

    # write the final file that contains all the data we need. after this we're all done
    final_f_name: str = f'audio_features_final.csv'
    write_path: Path = ABSPATH_TO_DATA / 'audio_features' / final_f_name
    complete_stream_history.to_csv(write_path, sep=',')

    print('Proccessing complete.')


if __name__ == "__main__":

    TEST_MODE = True    # <-- change this to False for the real run
    chunk_size = 50    # <-- change this to 1000 for the real run
    rows_to_skip = 17_000
    main(TEST_MODE=TEST_MODE, chunk_size=chunk_size, rows_to_skip=rows_to_skip)
