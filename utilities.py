import pandas as pd
import psycopg2
from config import settings
import streamlit as st
from datetime import date, timedelta

def get_leagues():
    '''This function gets a list of all the leagues with "interesting" predictions'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    get_query = f"SELECT date, league FROM match_ml_predictions"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['date', 'league'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")

    yesterday = date.today() + timedelta(days=-1)
    today = date.today()
    today_df = df[(df['date'].dt.date == yesterday) | (df['date'].dt.date == today)]
    leagues = tuple(set(list(today_df['league'])))
    return leagues

def get_league_matches(league):
    '''This function gets a list of all the matches from all the leagues'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT date, hometeam, awayteam FROM match_ml_predictions WHERE league = '{league}'"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['date','hometeam','awayteam'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")

    yesterday = date.today() + timedelta(days=-1)
    today = date.today()
    today_df = df[(df['date'].dt.date == yesterday) | (df['date'].dt.date == today)]
    
    matches = []
    for i in range(today_df.shape[0]):
        matches.append(f"{list(today_df['date'])[i]}_{list(today_df['hometeam'])[i]}_{list(today_df['awayteam'])[i]}")
    matches = tuple(matches)
    matches
    return matches


def get_predictions(league, date, home_team, away_team):
    '''This function gets the predictions from the selected match'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT * FROM match_ml_predictions WHERE league = '{league}' AND date = '{date}' AND hometeam = '{home_team}' AND awayteam = '{away_team}'"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=column_names)
    return df


def view_pred(league, selected_option):
    '''Takes the league and match and extracts the predictions. It also combines
    the teams prediction with the referee's prediction'''

    list_of_condition = selected_option.split('_')
    prediction = get_predictions(league, list_of_condition[0], list_of_condition[1], list_of_condition[2])

    with st.expander(f"Match Outcome Prediction"):
        st.write('--'*20)
        st.write(f"Outcome: {list(prediction['predicted_outcome'])[0]}")

    with st.expander(f"Match Score Prediction"):
        st.write('--'*20)
        st.write(f"Feature not yet available...")
        #st.write(f"Score: {list(prediction['predicted_scores'])[0]}")

def set_stage(stage):
        st.session_state.stage = stage

def form(leagues_matches, league):
    with st.form(str(league)):
        #Creates a link for each form so that each form can be easily navigated to from the sidebar.
        league_link = str(league).replace(' ','_')
        st.markdown(f"<a name='_{league_link}'></a>", unsafe_allow_html=True)
        
        st.write(f"{league}")

        #Creates a list of options with repesct to the available predictions
        selected_option = st.selectbox('Please select a Match.', leagues_matches)

        #Submit the selected option
        submitted = st.form_submit_button("Submit", on_click=set_stage, args=(1,))

    if submitted:
        view_pred(league, selected_option)