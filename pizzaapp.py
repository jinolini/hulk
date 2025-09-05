import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("Jinolinis Pizzadeig kalkulator")

# --- Sidebar buttons ---
st.sidebar.header("Velg oppskrift")
use_standard = st.sidebar.button("24h Deig")
use_custom = st.sidebar.button("Custom")

standard_recipe = {
    "number_of_pizzas": 4,
    "weight_per_pizza": 390.0,
    "hydration": 64.0,
    "salt": 3.0,
    "yeast": 0.2,
    "total_flour": 933,
    "total_water": 597,
    "total_salt": 28,
    "total_yeast": 2
}

# --- State management for recipe selection ---
if "recipe_mode" not in st.session_state:
    st.session_state.recipe_mode = "custom"

if use_standard:
    st.session_state.recipe_mode = "standard"
if use_custom:
    st.session_state.recipe_mode = "custom"

# --- Main page reset button ---
if "reset_main" not in st.session_state:
    st.session_state.reset_main = False

if st.button("Reset alle verdier"):
    st.session_state.number_of_pizzas = 4
    st.session_state.weight_per_pizza = 250
    st.session_state.hydration = 65.0
    st.session_state.salt = 2.0
    st.session_state.yeast = 0.3
    st.session_state.reset_main = True

# --- Input section ---
if st.session_state.recipe_mode == "standard":
    number_of_pizzas = st.slider("Antall pizzaballer", 1, 20, st.session_state.get("number_of_pizzas", 4), key="number_of_pizzas")
    weight_per_pizza = st.slider("Vekt per pizzaball (g)", 160, 350, st.session_state.get("weight_per_pizza", 250), step=10, key="weight_per_pizza")
    hydration = st.slider("Hydrasjon (%)", 50.0, 100.0, st.session_state.get("hydration", 64.0), step=1.0, key="hydration")
    salt = standard_recipe["salt"]
    yeast = standard_recipe["yeast"]
    preset = True
else:
    number_of_pizzas = st.slider("Antall Pizza", 1, 20, st.session_state.get("number_of_pizzas", 4), key="number_of_pizzas")
    weight_per_pizza = st.slider("Vekt per Pizza (g)", 160, 350, st.session_state.get("weight_per_pizza", 250), step=10, key="weight_per_pizza")
    hydration = st.slider("Hydrasjon (%)", 50.0, 100.0, st.session_state.get("hydration", 65.0), key="hydration", step=1.0)
    salt = st.slider("Salt (%)", 1.0, 3.0, st.session_state.get("salt", 2.0), step=0.1, key="salt")
    yeast = st.slider("Gjær (%)", 0.1, 2.0, st.session_state.get("yeast", 0.3), step=0.01, key="yeast")
    preset = False

    # Message box below sliders in custom mode
    st.info(
        "Mye gjær (1–2%) → kort fermentering (1–4 h RT).\n\n"
        "Medium (~0.5%) → moderat fermentering (6–8 h RT).\n\n"
        "Lite gjær (0.1–0.2%) → lang fermentering (24–72 h, ofte CT)."
    )

# --- Calculations ---
if preset:
    total_dough = number_of_pizzas * weight_per_pizza
    total_flour = total_dough / (1 + (hydration/100) + (salt/100) + (yeast/100))
    total_water = total_flour * (hydration/100)
    total_salt = total_flour * (salt/100)
    total_yeast = total_flour * (yeast/100)
else:
    total_dough = number_of_pizzas * weight_per_pizza
    total_flour = total_dough / (1 + (hydration/100) + (salt/100) + (yeast/100))
    total_water = total_flour * (hydration/100)
    total_salt = total_flour * (salt/100)
    total_yeast = total_flour * (yeast/100)

# --- Layout ---
st.header("Ingridienser")
st.write(f"**Mel:** {total_flour:.1f} g ({100:.1f}%)")
st.write(f"**Vann:** {total_water:.1f} g ({(hydration):.1f}%)")
st.write(f"**Salt:** {total_salt:.1f} g ({(salt):.1f}%)")
st.write(f"**Gjær:** {total_yeast:.1f} g ({(yeast):.2f}%)")

# --- Gjæring section for standard recipe ---
if st.session_state.recipe_mode == "standard":
    st.header("Gjæring (24h Deig)")
    st.markdown(f"""
    **Heveplan:**
    - Heves i bulk RT: 2 timer  
    - Heves i bulk CT: 12 timer  
    - Romtempereres: 2 timer  
    - Deigen balles og heves videre i RT: 8 timer  
    """)
    st.subheader("Beregn tidspunkter for gjæring")
    start_time_str = st.text_input(
        "Når er deigen knadd? (skriv inn klokkeslett, f.eks. 14:30)", 
        value=datetime.now().strftime("%H:%M")
    )
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        today = datetime.today()
        start_datetime = datetime.combine(today, start_time)

        bulk_rt_end = start_datetime + timedelta(hours=2)
        bulk_ct_end = bulk_rt_end + timedelta(hours=12)
        room_temp_end = bulk_ct_end + timedelta(hours=2)
        ball_rt_end = room_temp_end + timedelta(hours=8)

        def format_time(dt):
            label = dt.strftime('%H:%M')
            if dt.day != start_datetime.day:
                label += " (neste dag!)"
            return label

        st.write(f"**Start (knas):** {format_time(start_datetime)}")
        st.write(f"**Slutt bulk RT (2h):** {format_time(bulk_rt_end)}")
        st.write(f"**Slutt bulk CT (12h):** {format_time(bulk_ct_end)}")
        st.write(f"**Slutt romtemperering (2h):** {format_time(room_temp_end)}")
        st.write(f"**Klar til steking:** {format_time(ball_rt_end)}")
    except ValueError:
        st.error("Skriv inn klokkeslett på formatet HH:MM, f.eks. 14:30")

# --- Hide chart and table ---
# (Chart and table code is commented out)
