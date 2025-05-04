import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import pymysql

pymysql.install_as_MySQLdb()

st.set_page_config(page_title="Kanal statistikasi", layout="wide")
st.title("\U0001F4CA Kanal statistikasi")

# .env dan MYSQL_URL olish
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

MYSQL_URL = os.getenv('MYSQL_URL')
engine = create_engine(MYSQL_URL, echo=False)
Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    join_date = Column(String(32))
    source = Column(Text)

Session = sessionmaker(bind=engine)
session = Session()

# Ma'lumotlarni olish
def get_members_df():
    members = session.query(Member).all()
    if not members:
        return pd.DataFrame()
    data = [{
        'id': m.id,
        'user_id': m.user_id,
        'join_date': m.join_date,
        'source': m.source
    } for m in members]
    df = pd.DataFrame(data)
    if not df.empty:
        df['join_date'] = pd.to_datetime(df['join_date'])
        df['date'] = df['join_date'].dt.date
    return df

df = get_members_df()

if df.empty:
    st.info("Hozircha statistik ma'lumotlar yo'q.")
else:
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

session.close() 