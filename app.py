# -*- coding: utf-8 -*-
"""EV Range Predictor – Fixed "0" dropdown bug"""

import streamlit as st
import pandas as pd
import joblib

# ========================= LOAD MODEL & DATA =========================
model = joblib.load("electric_range_model.pkl")
df = pd.read_csv("cleaned_data.csv")

# ========================= PAGE CONFIG & CYBERPUNK STYLE =========================
st.set_page_config(page_title="EV Range Predictor", layout="wide")

cyberpunk_css = """
<style>
body {
    background-color: #0a0f1f;
    color: #c3f8ff;
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #0a0f1f 0%, #06101f 100%);
}
h1 {
    color: #00eaff;
    text-shadow: 0 0 20px #00eaff;
    text-align: center;
}
label {
    color: #9be4ff !important;
}
.css-1cpxqw2, .css-znku1x, .css-145kmo2 {
    color: #c3f8ff !important;
}
.stButton>button {
    background: linear-gradient(90deg, #003cff, #00eaff);
    color: white;
    border-radius: 10px;
    padding: 12px 25px;
    border: none;
    box-shadow: 0 0 15px #0066ff;
    transition: 0.3s;
}
.stButton>button:hover {
    box-shadow: 0 0 25px #00eaff;
    transform: scale(1.05);
}
.result-box {
    background: rgba(0, 255, 255, 0.06);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #00eaff33;
    text-align: center;
    box-shadow: 0 0 25px #00eaff55;
}
</style>
"""
st.markdown(cyberpunk_css, unsafe_allow_html=True)

# ========================= TITLE =========================
st.markdown("<h1>ELECTRIC VEHICLE RANGE PREDICTOR</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ========================= SIDEBAR INPUTS (FIXED) =========================
st.sidebar.header("Input Vehicle Features")

# ---- MAKE (bug-free version) ----
makes_list = sorted(df['Make'].dropna().astype(str).str.strip().unique().tolist())

make_options = ["-- Select Make --"] + makes_list
if 'selected_make' not in st.session_state:
    st.session_state.selected_make = make_options[0]

selected_make = st.sidebar.selectbox(
    "Make",
    options=make_options,
    index=make_options.index(st.session_state.selected_make),
    key="make_sb"
)
st.session_state.selected_make = selected_make

if selected_make == "-- Select Make --":
    st.sidebar.warning("Please select a Make")
    Make = None
    unique_models = []
else:
    Make = selected_make
    # Filter models for the selected make
    unique_models = sorted(
        df[df['Make'].astype(str) == Make]['Model']
        .dropna().astype(str).str.strip().unique().tolist()
    )

# ---- MODEL ----
model_options = ["-- Select Model --"] + unique_models
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = model_options[0]

selected_model = st.sidebar.selectbox(
    "Model",
    options=model_options,
    index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
    key="model_sb"
)
st.session_state.selected_model = selected_model

if selected_model == "-- Select Model --":
    Model = None
else:
    Model = selected_model

# ---- OTHER INPUTS (unchanged) ----
unique_ev_types = sorted(df['EV_Type'].dropna().astype(str).unique().tolist())
EV_Type = st.sidebar.selectbox("EV Type", ["-- Select EV Type --"] + unique_ev_types)

if EV_Type == "-- Select EV Type --":
    EV_Type = None

unique_cafv = sorted(df['CAFV_Eligibility'].dropna().astype(str).unique().tolist())
CAFV_Eligibility = st.sidebar.selectbox("CAFV Eligibility", ["-- Select Eligibility --"] + unique_cafv)

if CAFV_Eligibility == "-- Select Eligibility --":
    CAFV_Eligibility = None

Vehicle_Age = st.sidebar.number_input("Vehicle Age (years)", min_value=0, max_value=30, value=3)

current_year = 2025
implied_model_year = current_year - Vehicle_Age
st.sidebar.text(f"Implied Model Year: {implied_model_year}")

unique_utilities = sorted(df['Electric_Utility'].dropna().astype(str).unique().tolist())
Electric_Utility = st.sidebar.selectbox("Electric Utility Provider", ["-- Select Utility --"] + unique_utilities)

if Electric_Utility == "-- Select Utility --":
    Electric_Utility = None

predict_btn = st.sidebar.button("Predict Electric Range")

# ========================= PREDICTION =========================
if predict_btn:
    # Basic validation
    if None in [Make, Model, EV_Type, CAFV_Eligibility, Electric_Utility]:
        st.error("Please fill in all fields before predicting.")
    else:
        input_df = pd.DataFrame({
            "Make": [Make],
            "Model": [Model],
            "EV_Type": [EV_Type],
            "CAFV_Eligibility": [CAFV_Eligibility],
            "Vehicle_Age": [Vehicle_Age],
            "Electric_Utility": [Electric_Utility]
        })

        try:
            pred = model.predict(input_df)[0]
            st.markdown(
                f"""
                <div class="result-box">
                    <h2 style="color:#00eaff;">Estimated Electric Range</h2>
                    <h1 style="font-size:60px; color:#00f7ff; text-shadow:0 0 30px #00f7ff;">
                        {pred:.2f} miles
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Prediction Error: {e}")
