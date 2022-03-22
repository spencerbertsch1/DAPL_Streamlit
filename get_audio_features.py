"""
-------------------------------
| Data Analytics Project Lab  |
| Dartmouth College           |  
| Spring 2022                 |
-------------------------------

This file is designed to use the Spotify API to gather audio features about tracks. The data 
is then saved to disk so that the Spotify API doesn't need to be pinged whenever a user refreshes 
the Streamlit dashboard. 

This script should be run once as a single preprocessing step before the dashboard can be run. 

This file can be run from the command line by running: $ python3 get_audio_features.py
"""

import pandas as pd
from pathlib import Path
import time
import json
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from routines import SpotData, ABSPATH_TO_CREDENTIALS, ABSPATH_TO_DATA

# set to true for development and debugging
TEST_MODE = True

# read the data into memory 
sd = SpotData()
streaming_data = sd.streaming_history
library = sd.library

# --- Get Music Genres using Spotify API --- 

# Opening JSON file
f = open(str(ABSPATH_TO_CREDENTIALS))
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

n_rows: int = streaming_data.shape[0]

# Iterate through each song and use Spotify's development APIs to gather energy, loudness, danceability, and genres
row_list = []
tic = time.time()
for i, row in enumerate(streaming_data.iterrows()):
    artist = row[1]['artistName']
    track = row[1]['trackName']

    df = row[1].to_frame().T

    track_id_blob = sp.search(q='artist:' + artist + ' track:' + track, type='track')
    # we need to extract the id from the nested dictionary, list, and final dictionary 

    try:
        track_id = track_id_blob['tracks']['items'][0]['id']

        # actual GET request with proper header
        r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
        r = r.json()

        # get the track attributes we want
        energy = r['energy']
        loudness = r['loudness']
        danceability = r['danceability']

        # now we can get the genres based on the track_id found above 
        # first we get the artist info
        a = requests.get(BASE_URL + 'tracks/' + track_id, headers=headers)
        a = a.json()
        a_uri = a['artists'][0]['uri'].split(':')[2]

        g = requests.get(BASE_URL + 'artists/' + a_uri, headers=headers)
        g = g.json()
        genres: list = g['genres']

        df['energy'] = energy
        df['loudness'] = loudness
        df['danceability'] = danceability

        for genre in genres:
            df_local = df.copy()
            df_local['genres'] = genre
            row_list.append(df_local)
    except:
        print(f'Passing... API did not return sufficient information for: {track} by {artist}')

    # keep track of the progress
    if i%10 == 0:
        print(f'Time Elapsed: {time.strftime("%H:%M:%S", time.gmtime(time.time() - tic))}, Percent Complete: {round((i/n_rows), 3)*100}%')

    if TEST_MODE:
        if i >= 250:
            break

stream_history: pd.DataFrame = pd.concat(row_list, axis=0)

f_name: str = 'audio_features.csv'
write_path: Path = ABSPATH_TO_DATA / f_name
stream_history.to_csv(write_path, sep=',')

print('Proccessing complete.')