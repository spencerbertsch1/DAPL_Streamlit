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

import pandas as pd
import streamlit as st

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

# Create "How Well Do I Like My Own Taste in Music? The Dashboard!"

# Finds the songs that you thought you would like, but you actualy hate! 

# 1. Find the intersection of the songs you liked and your streaming songs 
# 2. Group by the artist_and_song field and take the mean of the msPlayed field 
# 3. Sort descending by the msPlayed field and display the "top" 25 songs with the least playtime 


