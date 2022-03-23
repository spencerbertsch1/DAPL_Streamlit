"""
-------------------------------
| Data Analytics Project Lab  |
| Dartmouth College           |  
| Spring 2022                 |
-------------------------------

This file contains the code needed to build a simple streamlit dashboard to display insights about a Spotify 
user's listening behavior. 

The dashboard will contain information such as the genres that are listened to the most, the hourly and daily 
listening behavior, the top artists, and the top tracks. 

This file can be run from the command line by running: $ streamlit run streamlit_main.py
"""

import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

cid ="Your-client-ID" 
secret = "Your-client-secret"

from routines import SpotData, load_audio_features

st.set_page_config(layout="wide")

season_selection = st.sidebar.selectbox(
    "Would you like to narrow your results?",
    ("Spring Tunes", "Summer Bops", "Autumn Songs", 'Winter Jams', 'All Year Long')
)

season_mapper: dict = {
    # maps the string chosen to the months included in the search
    "Spring Tunes": [12, 1, 2], 
    "Summer Bops": [3, 4, 5], 
    "Autumn Songs": [6, 7, 8], 
    'Winter Jams': [9, 10, 11], 
    'All Year Long': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
}

# read the data into memory 
sd = SpotData()
streaming_data = sd.streaming_history
library = sd.library

# streaming data with audio features
audio_features = load_audio_features() 

# we need to convert the string datetime series to a pandas datetime column 
streaming_data['date_filter'] = pd.to_datetime(streaming_data['endTime'], format='%Y-%m-%d %H:%M')  
# and then we can filter the streaming data to only the season chosen by the user
streaming_data = streaming_data[streaming_data['date_filter'].dt.month.isin(season_mapper[season_selection])]

# we then repeat the process with the audio features that will be used in other charts 
audio_features['date_filter'] = pd.to_datetime(audio_features['endTime'], format='%Y-%m-%d %H:%M')  

# TODO vvv UNCOMMENT THIS vvv
# audio_features = audio_features[audio_features['date_filter'].dt.month.isin(season_mapper[season_selection])]
# TODO ^^^ UNCOMMENT THIS ^^^

# --- get top songs ---
top_songs_df = streaming_data.groupby(by=["artist_and_song"]).count().sort_values(by=['trackName'], ascending=False)
top_songs_df['artist_and_song'] = top_songs_df.index
top_songs_df = top_songs_df.reset_index(drop=True)
top_songs_df = top_songs_df[['artist_and_song', 'endTime']].head(10)
top_songs_df = top_songs_df.rename(columns={'endTime': 'Count'})

# --- get top artists ---
top_artist_df = streaming_data.groupby(by=["artistName"]).count().sort_values(by=['trackName'], ascending=False)
top_artist_df['artist'] = top_artist_df.index
top_artist_df = top_artist_df.reset_index(drop=True)
top_artist_df = top_artist_df[['artist', 'endTime']].head(10)
top_artist_df = top_artist_df.rename(columns={'endTime': 'Count'})

# --- how well do you like your own taste in music? --- 
good_taste_df = streaming_data[streaming_data['artist_and_song'].isin(library['artist_and_song'])]
good_taste_df = good_taste_df[['msPlayed', 'artist_and_song']]
grouped_taste_df = good_taste_df.groupby(['artist_and_song']).mean()
grouped_taste_df = grouped_taste_df.sort_values(by='msPlayed', ascending=True)
# here we want to exclude all the songs that were'nt played at all because they were never forcibly skipped 
grouped_taste_df = grouped_taste_df[grouped_taste_df['msPlayed'] > 1000.0]
grouped_taste_df['artist_and_song'] = grouped_taste_df.index
grouped_taste_df = grouped_taste_df.head(20)

# --- group for daily listening chart ---
l_df = streaming_data.copy()
l_df.index = pd.to_datetime(l_df['endTime'], format='%Y-%m-%d %H:%M')  
agg_15m = l_df.groupby(pd.Grouper(freq='15Min')).count()

agg_15m['d_time'] = agg_15m.index
agg_15m['time'] = agg_15m['d_time'].dt.time
agg_15m = agg_15m[['msPlayed', 'time']]

time_df: pd.DataFrame = agg_15m.groupby(['time']).sum()
time_df['time'] = time_df.index

# --- get top genres --- 
print(audio_features.shape)

top_genres_df = audio_features.groupby(by=["genres"]).count().sort_values(by=['trackName'], ascending=False)
top_genres_df['genre'] = top_genres_df.index
top_genres_df = top_genres_df.reset_index(drop=True)
top_genres_df = top_genres_df[['genre', 'endTime']].head(10)
top_genres_df = top_genres_df.rename(columns={'endTime': 'Count'})

# ----- PLOTLY -----

# fig_bar_songs = px.bar(top_songs_df, x='artist_and_song', y='Count', width=800, height=650, 
#              color='Count', text_auto=True, title="Favorite Songs over the Past Year")

# fig_bar_artists = px.bar(top_artist_df, x='artist', y='Count', width=800, height=650, 
#              color='Count', text_auto=True, title="Favorite Artists over the Past Year")

fig_bar_songs = px.bar(top_songs_df, x='Count', y='artist_and_song', height=550, # width=800, height=650, 
             color='Count', text_auto=True, title="Favorite Songs over the Past Year", orientation='h')
fig_bar_songs['layout']['yaxis']['autorange'] = "reversed"

fig_bar_artists = px.bar(top_artist_df, x='Count', y='artist', height=550,  # width=800, height=650, 
             color='Count', text_auto=True, title="Favorite Artists over the Past Year", orientation='h')
fig_bar_artists['layout']['yaxis']['autorange'] = "reversed"

fig_line = px.bar(time_df, x="time", y="msPlayed", width=1350, height=650, 
                  title='Daily Listening Pattern', color='msPlayed', color_continuous_scale=px.colors.sequential.Viridis)

fig_music_taste = px.bar(grouped_taste_df, x='artist_and_song', y='msPlayed', width=800, height=650, 
             color='msPlayed', text_auto=True, title="Songs you thought you liked,but you actually hate", 
             color_continuous_scale=px.colors.sequential.Tealgrn)

fig_pie = px.pie(top_genres_df, values='Count', names='genre', width=300, height=600, 
                 title='Top Genres for Listener', color_discrete_sequence=px.colors.qualitative.Plotly)

body1 = '''
### Part I: Genreal Music Taste!
A look at top artists, songs, and an overview of your previous year's listening habits: 

'''

body2 = '''
### Part II: How Well Do I Like My Own Taste in Music? 
Find all the songs that you thought you would like, but you actualy hate! 

'''

# --- STREAMLIT CODE ---

st.header('Spotify Dashboard', anchor=None)

st.markdown('Author: [Spencer Bertsch](https://github.com/spencerbertsch1). Thanks to my pal [Mike Koshakow](https://github.com/Cpt-Catnip) for letting me show his music preferences to the world!', unsafe_allow_html=False)

st.write(f'You\'ve selected: **{season_selection}**. Use the sidebar on the left to see other options :sunglasses:')

st.write(f'This simple dashboard was made as an exercise for the DAPL course at Dartmouth College. Feel free to use this dashboard \
as a template or starting point for your own project!')

st.markdown(body1, unsafe_allow_html=False)


col1, col2= st.columns(2)

with col1:
    st.header("Top Songs")
    st.plotly_chart(fig_bar_songs, use_container_width=True)

with col2:
    st.header("Top Artists")
    st.plotly_chart(fig_bar_artists, use_container_width=True)

st.markdown('We can now look at the listening pattern through out the day! Do you like to \
listen to music in the morning? In the evening? Perhaps a podcast over lunch? Let\'s find out.', unsafe_allow_html=False)

col1, col2 = st.columns(2)

with col1:
    st.header("Daily Listening Pattern")
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.header("Top Genres")
    st.plotly_chart(fig_pie, use_container_width=True)


st.markdown(body2, unsafe_allow_html=False)
st.plotly_chart(fig_music_taste, use_container_width=True)





# Create "How Well Do I Like My Own Taste in Music? The Dashboard!"

# Finds the songs that you thought you would like, but you actualy hate! 

# 1. Find the intersection of the songs you liked and your streaming songs 
# 2. Group by the artist_and_song field and take the mean of the msPlayed field 
# 3. Sort descending by the msPlayed field and display the "top" 25 songs with the least playtime 


