import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("Jinolinis Pizzadeig kalkulator")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            min-width: 400px;
            max-width: 500px;
            width: 500px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar buttons ---
st.sidebar.header("Velg oppskrift")
use_custom = st.sidebar.button("Custom")
use_standard = st.sidebar.button("24h Deig")
use_poolish = st.sidebar.button("Poolish deig")

# --- Poolish yeast table ---
poolish_fermentation = {
    12: 0.250,
    13: 0.200,
    14: 0.160,
    15: 0.120,
    16: 0.099,
    17: 0.078,
    18: 0.062,
    19: 0.050,
    20: 0.039
}

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
if use_poolish:
    st.session_state.recipe_mode = "poolish"

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
    st.sidebar.header("24h Deig")
    number_of_pizzas = st.sidebar.slider("Antall pizzaballer", 1, 20, st.session_state.get("number_of_pizzas", 4), key="standard_number_of_pizzas")
    weight_per_pizza = st.sidebar.slider("Vekt per pizzaball (g)", 160, 350, st.session_state.get("weight_per_pizza", 250), step=10, key="standard_weight_per_pizza")
    hydration = st.sidebar.slider("Hydrasjon (%)", 50.0, 100.0, st.session_state.get("hydration", 64.0), step=1.0, key="standard_hydration")
    salt = st.sidebar.slider("Salt (%)", 1.0, 3.0, standard_recipe["salt"], step=0.1, key="standard_salt")
    yeast = st.sidebar.slider("Gjær (%)", 0.1, 2.0, standard_recipe["yeast"], step=0.01, key="standard_yeast")
    preset = True

elif st.session_state.recipe_mode == "poolish":
    st.sidebar.header("Poolish deig")
    number_of_pizzas = st.sidebar.slider("Antall pizzaballer", 1, 20, st.session_state.get("number_of_pizzas", 4), key="poolish_number_of_pizzas")
    weight_per_pizza = st.sidebar.slider("Vekt per pizzaball (g)", 160, 350, st.session_state.get("weight_per_pizza", 250), step=10, key="poolish_weight_per_pizza")
    hydration = st.sidebar.slider("Hydrasjon (%)", 50.0, 100.0, st.session_state.get("hydration", 64.0), step=1.0, key="poolish_hydration")
    salt = st.sidebar.slider("Salt (%)", 1.0, 3.0, st.session_state.get("salt", 2.0), step=0.1, key="poolish_salt")
    poolish_percent = st.sidebar.slider("Poolish (% av total deig)", 20, 40, 30, step=1, key="poolish_percent")
    fermentation_hours = st.sidebar.selectbox("Fermenteringstid (timer)", list(poolish_fermentation.keys()), index=2, key="poolish_fermentation_hours")
    yeast_percent = poolish_fermentation[fermentation_hours]  # This is now % yeast, not grams!
    preset = True

    # Beregn total mengder
    total_dough = number_of_pizzas * weight_per_pizza
    total_flour = total_dough / (1 + (hydration/100) + (salt/100) + (yeast_percent/100))
    total_water = total_flour * (hydration/100)
    total_salt = total_flour * (salt/100)
    total_yeast = total_flour * (yeast_percent/100)

    # Poolish mengder
    poolish_flour = total_flour * (poolish_percent / 100)
    poolish_water = poolish_flour  # 100% hydration in poolish
    poolish_yeast = poolish_flour * (yeast_percent / 100)  # Yeast for poolish in grams

    # Resten av ingrediensene (tilsettes etter poolish)
    rest_flour = total_flour - poolish_flour
    rest_water = total_water - poolish_water
    rest_salt = total_salt
    rest_yeast = total_yeast - poolish_yeast

else:
    st.sidebar.header("Custom")
    number_of_pizzas = st.sidebar.slider("Antall Pizza", 1, 20, st.session_state.get("number_of_pizzas", 4), key="custom_number_of_pizzas")
    weight_per_pizza = st.sidebar.slider("Vekt per Pizza (g)", 160, 350, st.session_state.get("weight_per_pizza", 250), step=10, key="custom_weight_per_pizza")
    hydration = st.sidebar.slider("Hydrasjon (%)", 50.0, 100.0, st.session_state.get("hydration", 65.0), key="custom_hydration", step=1.0)
    salt = st.sidebar.slider("Salt (%)", 1.0, 3.0, st.session_state.get("salt", 2.0), step=0.1, key="custom_salt")
    yeast = st.sidebar.slider("Gjær (%)", 0.1, 2.0, st.session_state.get("yeast", 0.3), step=0.01, key="custom_yeast")
    preset = False

# --- Message box and ingredient lists OUTSIDE sidebar ---
if st.session_state.recipe_mode == "custom":
    st.info(
        "Mye gjær (1–2%) → kort fermentering (1–4 h RT).\n\n"
        "Medium (~0.5%) → moderat fermentering (6–8 h RT).\n\n"
        "Lite gjær (0.1–0.2%) → lang fermentering (24–72 h, ofte CT)."
    )

if st.session_state.recipe_mode == "poolish":
    st.subheader("Poolish ingredienser")
    st.write(f"Mel: {poolish_flour:.1f} g (100%)")
    st.write(f"Vann: {poolish_water:.1f} g (100%)")
    st.write(f"Gjær: {poolish_yeast:.3f} g ({yeast_percent:.3f}%) for {fermentation_hours} timer fermentering")
    st.subheader("Resten av ingrediensene")
    st.write(f"Mel: {rest_flour:.1f} g")
    st.write(f"Vann: {rest_water:.1f} g")
    st.write(f"Salt: {rest_salt:.1f} g")
    st.write(f"Gjær: {rest_yeast:.3f} g")

# --- Calculations ---
if st.session_state.recipe_mode == "poolish":
    total_dough = number_of_pizzas * weight_per_pizza
    total_flour = total_dough / (1 + (hydration/100) + (salt/100) + (yeast_percent/100))
    total_water = total_flour * (hydration/100)
    total_salt = total_flour * (salt/100)
    total_yeast = total_flour * (yeast_percent/100)
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
st.write(f"**Gjær:** {total_yeast:.1f} g ({(yeast_percent):.2f}%)")

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

# --- Gjæring section for poolish recipe ---
if st.session_state.recipe_mode == "poolish":
    st.header("Gjæring (Poolish deig)")
    st.markdown(f"""
    **Poolish oppskrift:**  
    - Poolish: {poolish_percent}% av total deig  
    - Poolish = 100% mel + 100% vann  
    - Gjær til poolish: {yeast_percent:.3f}% av poolish-mel ({poolish_yeast:.3f} g) for {fermentation_hours} timer fermentering
    """)
    st.markdown(f"""
    **Heveplan:**
    - Poolish fermenteres: {fermentation_hours} timer  
    - Poolish blandes med resten av ingrediensene og heves i bulk RT: 2 timer  
    - Deigen balles og heves videre i RT: 2 timer  
    """)
    st.subheader("Beregn tidspunkter for gjæring")
    start_time_str = st.text_input(
        "Når starter du poolish? (skriv inn klokkeslett, f.eks. 14:30)", 
        value=datetime.now().strftime("%H:%M"),
        key="poolish_start_time"
    )
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        today = datetime.today()
        start_datetime = datetime.combine(today, start_time)

        poolish_end = start_datetime + timedelta(hours=fermentation_hours)
        bulk_rt_end = poolish_end + timedelta(hours=2)
        ball_rt_end = bulk_rt_end + timedelta(hours=2)

        def format_time(dt):
            label = dt.strftime('%H:%M')
            if dt.day != start_datetime.day:
                label += " (neste dag!)"
            return label

        st.write(f"**Start poolish:** {format_time(start_datetime)}")
        st.write(f"**Slutt poolish fermentering ({fermentation_hours}h):** {format_time(poolish_end)}")
        st.write(f"**Slutt bulk RT (2h):** {format_time(bulk_rt_end)}")
        st.write(f"**Klar til steking (etter balling og 2h RT):** {format_time(ball_rt_end)}")
    except ValueError:
        st.error("Skriv inn klokkeslett på formatet HH:MM, f.eks. 14:30")
