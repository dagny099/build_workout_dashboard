import pymysql
import streamlit as st

def get_db_connection():
    connection = pymysql.connect(
        host=st.secrets["db_host"],
        user=st.secrets["db_user"],
        password=st.secrets["db_pass"],
        db=st.secrets["db_name"],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def load_data():
    connection = get_db_connection()
    query = "SELECT * FROM exercise_table;"
    return pd.read_sql(query, connection)

df = load_data()
st.write(df)


import plotly.express as px

if st.checkbox("Show Charts"):
    fig = px.line(df, x='date', y='steps', title="Daily Exercise Steps")
    st.plotly_chart(fig)


