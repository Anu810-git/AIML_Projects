import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load saved model and feature list
model = joblib.load('best_taxi_fare_model.pkl')
features = joblib.load('features.pkl')

st.title("🚗 TripFare: Predict Your Taxi Fare")
st.write("Enter your trip details below to get an estimated fare.")

# --- User Inputs ---
pickup_lat = st.number_input("Pickup Latitude", value=40.7128)
pickup_lon = st.number_input("Pickup Longitude", value=-74.0060)
dropoff_lat = st.number_input("Dropoff Latitude", value=40.7580)
dropoff_lon = st.number_input("Dropoff Longitude", value=-73.9855)
passenger_count = st.slider("Passenger Count", 1, 6, 1)
pickup_hour = st.slider("Pickup Hour (0-23)", 0, 23, 12)
is_weekend = st.selectbox("Is it a weekend?", ["No", "Yes"])
is_night = st.selectbox("Is it a night ride (10PM-5AM)?", ["No", "Yes"])

# --- Calculate derived features ---
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c

trip_distance = haversine(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)

input_dict = {
    'trip_distance': trip_distance,
    'passenger_count': passenger_count,
    'pickup_hour': pickup_hour,
    'is_weekend': 1 if is_weekend == "Yes" else 0,
    'is_night': 1 if is_night == "Yes" else 0,
}

# Build input row matching the training features (fill missing ones with 0)
input_df = pd.DataFrame([input_dict])
for col in features:
    if col not in input_df.columns:
        input_df[col] = 0
input_df = input_df[features]   # match column order

# --- Predict ---
if st.button("Predict Fare"):
    prediction = model.predict(input_df)[0]
    st.success(f"💰 Estimated Total Fare: ${prediction:.2f}")