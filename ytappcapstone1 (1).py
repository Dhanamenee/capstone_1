

import streamlit as st
from youtube_api import get_channel_details, get_video_ids, get_video_details,create_tables, insert_channel, insert_video


#from sql_handler import create_tables, insert_channel, insert_video
import pandas as pd
import mysql.connector

st.set_page_config(page_title="YouTube Data Harvest", layout="wide")
st.title("📺 YouTube Data Harvesting and Warehousing")

# Initialize tables if not exist
create_tables()

channel_id = st.text_input("UC-jVLgSrtXj0gUlbS5QFPHg")

if st.button("Fetch & Store Channel Data"):
    with st.spinner("Fetching from YouTube..."):
        channel = get_channel_details(channel_id)
        if not channel:
            st.error("Invalid Channel ID or not found.")
        else:
            insert_channel(channel)
            video_ids = get_video_ids(channel["playlist_id"])
            for vid in video_ids:
                video = get_video_details(vid)
                insert_video(video, channel["channel_id"])
            st.success(f"Stored data for '{channel['channel_name']}' and {len(video_ids)} videos.")

st.markdown("## 🔍 Run SQL Queries")

query_options = {
    "All videos and their channels":
        "SELECT video_name, channel_name FROM videos JOIN channels USING(channel_id)",
    "Channel with most videos":
        "SELECT channel_name, COUNT(*) AS video_count FROM videos JOIN channels USING(channel_id) GROUP BY channel_name ORDER BY video_count DESC LIMIT 1",
    "Top 10 most viewed videos":
        "SELECT video_name, view_count, channel_name FROM videos JOIN channels USING(channel_id) ORDER BY view_count DESC LIMIT 10"
}

selected_query = st.selectbox("Choose a query", list(query_options.keys()))

if st.button("Run Query"):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2594",
        database="youtube_project"
    )
    df = pd.read_sql(query_options[selected_query], db)
    st.dataframe(df)
