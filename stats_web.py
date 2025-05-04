import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Kanal statistikasi", layout="wide")
st.title("\U0001F4CA Kanal statistikasi")

# Ma'lumotlar bazasidan o'qish
conn = sqlite3.connect('stats.db')
df = pd.read_sql_query("SELECT * FROM members", conn)

if df.empty:
    st.info("Hozircha statistik ma'lumotlar yo'q.")
else:
    df['join_date'] = pd.to_datetime(df['join_date'])
    df['date'] = df['join_date'].dt.date

    st.subheader("Kunlik qo'shilgan a'zolar")
    daily = df.groupby('date').size()
    st.bar_chart(daily)

    st.subheader("Manbalar bo'yicha a'zolar")
    source_counts = df['source'].value_counts()
    st.bar_chart(source_counts)

    st.subheader("Soatlik qo'shilganlar (bugun)")
    today = pd.Timestamp.now().date()
    today_df = df[df['date'] == today]
    if not today_df.empty:
        today_df['hour'] = today_df['join_date'].dt.hour
        st.bar_chart(today_df['hour'].value_counts().sort_index())
    else:
        st.info("Bugun a'zo qo'shilmagan.")

conn.close() 