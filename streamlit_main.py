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
from datetime import date
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

from routines import SpotData, load_audio_features

DASHBOARD_SIMPLE: bool = False

st.set_page_config(layout="wide")

season_selection = st.sidebar.selectbox(
    "Would you like to narrow your results?",
    ('All Year Long', "Spring Tunes", "Summer Bops", "Autumn Songs", 'Winter Jams')
)

season_mapper: dict = {
    # maps the string chosen to the months included in the search
    "Spring Tunes": [3, 4, 5], 
    "Summer Bops": [6, 7, 8], 
    "Autumn Songs": [9, 10, 11], 
    'Winter Jams': [12, 1, 2], 
    'All Year Long': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
}

todays_date = date.today()
curr_year = int(todays_date.year)  # <-- we will use this later 

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
audio_features = audio_features[audio_features['date_filter'].dt.month.isin(season_mapper[season_selection])]

# we need to do this to fix a small bug with the line graph: 
line_audio_features: pd.DataFrame = audio_features.copy()
line_audio_features = line_audio_features[line_audio_features['date_filter'].dt.year != curr_year]

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


l_df = streaming_data.copy()
l_df.index = pd.to_datetime(l_df['endTime'], format='%Y-%m-%d %H:%M')  
agg_15m = l_df.groupby(pd.Grouper(freq='15Min')).count()

agg_15m['d_time'] = agg_15m.index
agg_15m['time'] = agg_15m['d_time'].dt.time
agg_15m = agg_15m[['msPlayed', 'time']]

# here we need to account for the time zone shift (roll back 5 hours)
time_df: pd.DataFrame = agg_15m.groupby(['time']).sum()
# convert time to datetimeime index 
time_df.index = pd.to_datetime(time_df.index, format='%H:%M:%S')  
# roll the time back by 5 hours
time_df = time_df.shift(periods=-5, freq="H")
# convert index back to time
time_df['d_time'] = time_df.index
# change the time sequence to 12 hour instead of military time 
time_df['time'] = time_df['d_time'].dt.strftime('%I:%M:%S %p')
# only keep the columns we need
time_df = time_df[['msPlayed', 'time']]
# rename columns to something more representative of reality 
time_df = time_df.rename(columns={'msPlayed': 'Songs Played'})


# --- get top genres --- 
top_genres_df = audio_features.copy()
top_genres_df = top_genres_df.groupby(by=["genres"]).count().sort_values(by=['trackName'], ascending=False)
top_genres_df['genre'] = top_genres_df.index
top_genres_df = top_genres_df.reset_index(drop=True)
top_genres_df = top_genres_df[['genre', 'endTime']].head(20)
top_genres_df = top_genres_df.rename(columns={'endTime': 'Count'})

def create_fig_pie(num_slices: int):
    # --- get top genres --- 
    top_genres_df = audio_features.copy()
    top_genres_df = top_genres_df.groupby(by=["genres"]).count().sort_values(by=['trackName'], ascending=False)
    top_genres_df['genre'] = top_genres_df.index
    top_genres_df = top_genres_df.reset_index(drop=True)
    top_genres_df = top_genres_df[['genre', 'endTime']].head(num_slices)
    top_genres_df = top_genres_df.rename(columns={'endTime': 'Count'})

    pie_chart_padding: int = 75  # <-- increase this to make the pie chart smaller
    labels = list(top_genres_df['genre'])
    values = list(top_genres_df['Count'])
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig_pie.update_layout(
        autosize=False,
        width=350,
        height=600,
        margin=dict(
            l=pie_chart_padding,
            r=pie_chart_padding,
            b=pie_chart_padding,
            t=pie_chart_padding/2,
            pad=4
        )
    )

    return fig_pie


def get_line_fig(time_agg: str):

    time_agg_mapper: dict = {
        'Daily': '1D', 
        'Weekly': '1W', 
        'Monthly': '1M'
    }

    # vvv we add this to fix a bug with the spring data
    if season_selection == "Spring Tunes":
        audio_feats_df = line_audio_features.copy()
    else:
        audio_feats_df = audio_features.copy()

    # --- group for attributes over time chart ---
    audio_feats_df.index = pd.to_datetime(audio_feats_df['endTime'], format='%Y-%m-%d %H:%M')  
    audio_feats_df = audio_feats_df.groupby(pd.Grouper(freq=time_agg_mapper[time_agg])).mean()
    audio_feats_df['day'] = audio_feats_df.index
    audio_feats_df['day_dt'] = audio_feats_df['day'].dt.date
    audio_feats_df_to_scale = audio_feats_df[['energy', 'loudness', 'danceability']]
    audio_feats_df_no_scale = audio_feats_df[['day_dt']]
    audio_feats_df_no_scale = audio_feats_df_no_scale.reset_index(drop=True)
    # we need to force all the loudness values to be positive here
    audio_feats_df_to_scale['loudness'] = audio_feats_df_to_scale['loudness'].abs()

    # perform a robust scaler transform of the dataset
    transformer = MinMaxScaler()
    audio_feats_df_to_scale = transformer.fit_transform(audio_feats_df_to_scale)
    audio_feats_df_to_scale = pd.DataFrame(audio_feats_df_to_scale)  # <-- convert back to pandas 
    audio_feats_df_to_scale = audio_feats_df_to_scale.fillna(0)

    # horizontally concatenate our no-scale feature back onto our scaled data
    audio_feats_df = pd.concat([audio_feats_df_no_scale, audio_feats_df_to_scale], axis=1)
    audio_feats_df = audio_feats_df.rename(columns={0: 'energy', 1: 'loudness', 2: 'danceability'})

    date = list(audio_feats_df['day_dt'])
    energy = list(audio_feats_df['energy'])
    loudness = list(audio_feats_df['loudness'])
    danceability = list(audio_feats_df['danceability'])
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=date, y=energy,
                        mode='lines',
                        name='Energy'))
    line_fig.add_trace(go.Scatter(x=date, y=loudness,
                        mode='lines',
                        name='Loudness'))
    line_fig.add_trace(go.Scatter(x=date, y=danceability,
                        mode='lines',
                        name='Danceability'))

    line_fig.update_layout(
        autosize=False,
        height=550
    )

    return line_fig


def get_fig_music_taste(threshold: str):

    threshold_mapper: dict = {
        'Why did I ever like this song? Give me the next one.': 1000.0, 
        'It\'s fine, but I don\'t want it now.': 5000.0, 
        'I can\'t decide... Skip after at least ten seconds.': 10000.0
    }

    # --- how well do you like your own taste in music? --- 
    good_taste_df = streaming_data[streaming_data['artist_and_song'].isin(library['artist_and_song'])]
    good_taste_df = good_taste_df[['msPlayed', 'artist_and_song']]
    grouped_taste_df = good_taste_df.groupby(['artist_and_song']).mean()
    grouped_taste_df = grouped_taste_df.sort_values(by='msPlayed', ascending=True)
    # here we want to exclude all the songs that were'nt played at all because they were never forcibly skipped 
    grouped_taste_df = grouped_taste_df[grouped_taste_df['msPlayed'] > threshold_mapper[threshold]]
    grouped_taste_df['artist_and_song'] = grouped_taste_df.index
    grouped_taste_df = grouped_taste_df.head(20)

    fig_music_taste = px.bar(grouped_taste_df, x='artist_and_song', y='msPlayed', width=800, height=650, 
             color='msPlayed', text_auto=True, title="Songs you thought you liked,but you actually hate", 
             color_continuous_scale=px.colors.sequential.Tealgrn)

    return fig_music_taste
    

# ----- PLOTLY -----

fig_bar_songs = px.bar(top_songs_df, x='Count', y='artist_and_song', height=550, # width=800, height=650, 
             color='Count', text_auto=True, title="Favorite Songs over the Past Year", orientation='h')
fig_bar_songs['layout']['yaxis']['autorange'] = "reversed"

fig_bar_artists = px.bar(top_artist_df, x='Count', y='artist', height=550,  # width=800, height=650, 
             color='Count', text_auto=True, title="Favorite Artists over the Past Year", orientation='h')
fig_bar_artists['layout']['yaxis']['autorange'] = "reversed"

fig_bar_listening = px.bar(time_df, x="time", y="Songs Played", width=1350, height=650, 
                  title='Daily Listening Pattern', color='Songs Played', color_continuous_scale=px.colors.sequential.Viridis)


# --- STREAMLIT CODE ---

st.markdown('# Spotify Dashboard', unsafe_allow_html=False)

st.markdown('Author: [Spencer Bertsch](https://github.com/spencerbertsch1). Thanks to my pal [Mike Koshakow](https://github.com/Cpt-Catnip) for letting me show his music preferences to the world!', unsafe_allow_html=False)

st.markdown('Feel free to check out [the github repo for this project.](https://github.com/spencerbertsch1/DAPL_Streamlit) \n \
            The README has much more information about how to set up your own running version of this dashboard and how you can adapt it to create your own music taste tracker.', unsafe_allow_html=False)

st.write(f'This dashboard was made as an exercise for the DAPL course at Dartmouth College. Feel free to use this dashboard \
as a template or starting point for your own project!')

st.write(f'You\'ve selected: **{season_selection}**. Use the sidebar on the left to see other options :sunglasses:')


st.markdown('''
## General Music Taste
We first take a look at top artists, songs, and an overview of the listener's previous year's listening habits: 
''', unsafe_allow_html=False)

col1, col2= st.columns(2)

with col1:
    st.header("Top Songs")
    st.plotly_chart(fig_bar_songs, use_container_width=True)

with col2:
    st.header("Top Artists")
    st.plotly_chart(fig_bar_artists, use_container_width=True)

if not DASHBOARD_SIMPLE:
    # here we only display the Energy, Loudness, & Danceability attributes if the dashboard is NOT set to simple
    st.markdown('''
    ## Energy, Loudness, & Danceability
    We can now look at how the listener\'s energy, loudness, and danceability change over time!
    ''', unsafe_allow_html=False)

    time_agg = st.selectbox(
        'How do you want to aggregate the song attributes?',
        ('Daily', 'Weekly', 'Monthly'))
    st.write(f'You selected **{time_agg}**, feel free to try other time aggregations for the listener\'s energy, loudness, and danceability.')


    line_fig = get_line_fig(time_agg=time_agg)
    st.plotly_chart(line_fig, use_container_width=True)


if DASHBOARD_SIMPLE:
    # for the simple version of the dashbaord, we only want to display the "daily listening pattern" chart 
    st.header("Daily Listening Pattern")
    st.markdown('We can now look at the listening pattern throughout the day! Do you like to \
listen to music in the morning? In the evening? Perhaps a podcast over lunch? Let\'s find out.', unsafe_allow_html=False)
    st.plotly_chart(fig_bar_listening, use_container_width=True)
else:
    # for the complex version of the dashbaord, we also include a pie chart showing the listener's genres
    col1, col2 = st.columns(2)

    with col1:
        st.header("Daily Listening Pattern")
        st.markdown('We can now look at the listening pattern throughout the day! Do you like to \
    listen to music in the morning? In the evening? Perhaps a podcast over lunch? Let\'s find out.', unsafe_allow_html=False)
        
        st.plotly_chart(fig_bar_listening, use_container_width=True)

    with col2:
        st.header("Top Genres")
        st.markdown('We can also examine the top genres listened to over this time period! Traditionally pie charts should be capped at around ten slices, \
        but just look at some of these genres! Anybody ever heard of bubble grunge?', unsafe_allow_html=False)
        num_slices: int = st.select_slider(
            'Select the number of slices in the pie chart',
            options=list(range(5, 50)))

        fig_pie = create_fig_pie(num_slices=num_slices)
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('''
# How Well Do I Like My Own Taste in Music? 
Find all the songs that you thought you would like, but you actually hate! This section of the dashboard finds the intersection of songs that have been liked by the listener (added to their "liked" songs), 
but whenever the song comes on the listener skips them immediately. These songs, therefore, are songs that the listener thought they would enjoy, but they never make a good enough impression to actually listen to. 

The songs are broken into three groups representing songs listened to for one, five, or ten seconds before harsh judgement was passed and the song was skipped. 

''', unsafe_allow_html=False)

threshold = st.radio(
     "How do you want to filter all of these not-so-liked songs?",
     ('Why did I ever like this song? Give me the next one.', 
     'It\'s fine, but I don\'t want it now.', 
     'I can\'t decide... Skip after at least ten seconds.'))

fig_music_taste = get_fig_music_taste(threshold=threshold)
st.plotly_chart(fig_music_taste, use_container_width=True)

st.markdown(""" 
## References

I was inspired to make this dashboard by my friend [Anne Bode](https://annebode.medium.com/) who made a similar dashboard in Tableau, [outlined here](https://towardsdatascience.com/visualizing-spotify-data-with-python-tableau-687f2f528cdd). 

Like Anne, I also found [this article](https://stmorse.github.io/journal/spotify-api.html) by Steven Morse very helpful when learning how to use Spotify's many APIs to get the information I wanted. 

Thanks for viewing this dashboard! If you enjoy it, please give [the repository](https://github.com/spencerbertsch1/DAPL_Streamlit) a star and feel free to build upon the code in this project to make your own fun, music-inspired dashboard of your own! 
""", unsafe_allow_html=False)