# Streamlit Demo App 

<p align="center">
  <img src="https://user-images.githubusercontent.com/20422614/160195268-311e1fca-9397-429c-b99f-aeb1d064c04f.png" alt="drawing" width="55%"/>
</p>

This repository contains a Spotify + Streamlit dashboard built as an example of cloud data visualization for the Data Analytics Project Lab at Dartmouth College. 

Feel free to check out the [live dashboard here!](https://share.streamlit.io/spencerbertsch1/dapl_streamlit/main/streamlit_main.py)

Author: [Spencer Bertsch](https://github.com/spencerbertsch1)  
Dartmouth College  
Spring 2022  

Big thanks to my pal [Mike Koshakow](https://github.com/Cpt-Catnip) for letting me share his music preferences with the world! 

# How to create a dashboard using your own spotify data (Simple)
1. Clone this repository locally.
2. Request your data from Spotify using [this link](https://www.spotify.com/us/account/privacy/). Be patient, this can take a few days. 
3. Once you receive your data from Spotify, place the important JSON files into the `MyData` directory. Spotify will give you lots of data including billing information, but you only need the following files: 
- SearchQueries.json
- YourLibrary.json
- StreamingHistory.json  
Note you might have more than one StreamingHistory.json file. That's okay, just copy all the streaming history files into the `MyData` directory.  
4. Set the `DASHBOARD_SIMPLE` variable to `True` at the top of the `streamlit_main.py` script (line 29).  
5. Once that's done you will have all the data you need! Last step is to run the dashboard using the following command: 
- `$ streamlit run streamlit_main.py`
After that the dashboard should open in your default web browser. 


# How to create a dashboard using your own spotify data (Advanced)

If you want to see this spotify dashboard reflect your own music taste, you will need to follow these steps: 

1. Clone this repository locally.
2. Request your data from Spotify using [this link](https://www.spotify.com/us/account/privacy/). Be patient, this can take a few days. 
3. Once you receive your data from Spotify, place the important JSON files into the `MyData` directory. Spotify will give you lots of data including billing information, but you only need the following files: 
- SearchQueries.json
- YourLibrary.json
- StreamingHistory.json  
Note you might have more than one StreamingHistory.json file. That's okay, just copy all the streaming history files into the `MyData` directory.  
4. Next you will need to create a spotify developer account using [this link](https://developer.spotify.com/dashboard/applications), and create a new project. After you create the project, you will need to copy the Client-ID and the Client-Secret into a new .json file called `spotify_app_credentials.json`. 
5. Your `spotify_app_credentials.json` file should contain a single line in the following format: `{"Client-ID": "XXXX", "Client-Secret": "XXXX"}`.
Place your new json file into the directory one level above the working directory of this project alongside `DAPL_Streamlit`. 
6. Just a few more steps! Now run the `get_audio_features.py` script by running the following command: 
- `$ python3 get_audio_features.py`  
This script can take a while to run depending on how many songs you've listened to in the past year. For a listener with 24k songs streamed it took about an hour. The limiting factor here is not the machine running the script, but the response time for the APIs returning all the data we need to collect.  
7. Once that's done you will have all the data you need! Last step is to run the dashboard using the following command: 
- `$ streamlit run streamlit_main.py`
After that the dashboard should open in your default web browser. 


# How to run this code

If you want to run this dashboard locally, simply follow these steps: 

1. Clone this repository locally.
2. Create a new Conda environment by running the following command:
   1. `$ conda create -n streamlit-demo python=3.8`
3. Activate the new environment by running the following command: 
   1. `$ conda activate streamlit-demo`
4. Install the necessary dependencies by navigating to the working directory and pip installing the required libraries by running the following commands: 
   1. `$ cd ~/DAPL_Streamlit`
   2. `$ pip install -r requirements.txt`
5. Run the streamlit_main.py file to create a local server and see the dashboard running on your computer. 
   1. `$ streamlit run streamlit_main.py`
7. That's it! After that the dashboard should open in your default web browser. 

## Resources

As mentioned at the bottom of the dashboard itself, I was inspired to make this dashboard by my friend [Anne Bode](https://annebode.medium.com/) who did a similar project using Tableau, [outlined here](https://towardsdatascience.com/visualizing-spotify-data-with-python-tableau-687f2f528cdd). 

Like Anne, I also found [this article](https://stmorse.github.io/journal/spotify-api.html) by Steven Morse very helpful when learning how to use Spotify's many APIs to get the information I wanted. 

Thanks for viewing this dashboard! If you enjoy it, please give [the repository](https://github.com/spencerbertsch1/DAPL_Streamlit) a star ⭐ and feel free to build upon the code in this project to make a fun, music-inspired dashboard of your own! 

### Image Sources

- [Spotify Logo Source](https://www.freepnglogos.com/pics/spotify-logo-png)
- [Streamlit Logo Source](https://www.crunchbase.com/organization/streamlit)
