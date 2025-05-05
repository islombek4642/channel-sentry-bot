import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import mysql.connector
from sqlalchemy import create_engine
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
import time

# Matrix-style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #00ff00;
        font-family: 'Share Tech Mono', monospace;
    }
    
    .stButton>button {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
        font-family: 'Share Tech Mono', monospace;
    }
    
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000000;
    }
    
    .css-1d391kg {
        background-color: #000000;
    }
    
    .stSelectbox {
        background-color: #000000;
        color: #00ff00;
    }
    
    .stSelectbox>div>div {
        background-color: #000000;
        color: #00ff00;
    }
    
    .stDataFrame {
        background-color: #000000;
        color: #00ff00;
    }
    
    .stMetric {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .stProgress>div>div {
        background-color: #00ff00;
    }
    
    .stProgress>div>div>div {
        background-color: #00ff00;
    }
    
    .stMarkdown {
        color: #00ff00;
    }
    
    .stAlert {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #000000;
        color: #00ff00;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #000000;
        color: #00ff00;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #000000;
        color: #00ff00;
        border-bottom: 2px solid #00ff00;
    }
</style>
""", unsafe_allow_html=True)

# Matrix rain effect
st.markdown("""
<div id="matrix-rain"></div>
<script>
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = [];

    for (let i = 0; i < columns; i++) {
        drops[i] = 1;
    }

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0F0';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 33);
</script>
""", unsafe_allow_html=True)

# Update the main title with Matrix style
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='color: #00ff00; font-family: "Share Tech Mono", monospace; text-shadow: 0 0 10px #00ff00;'>
        CHANNEL SENTRY
    </h1>
    <p style='color: #00ff00; font-family: "Share Tech Mono", monospace;'>
        Channel Statistics Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# ... rest of the existing code ... 