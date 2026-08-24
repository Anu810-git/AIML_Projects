import os
import streamlit as st
import numpy as np
import pandas as pd
import joblib
 
# ----------------------------
# Load saved artifacts
# ----------------------------
@st.cache_resource
def load_artifacts():
    # the best regression model may have been saved as .pkl (sklearn/XGBoost)
    # or as .h5 (if the ANN model performed best)
    if os.path.exists('best_price_model.pkl'):
        price_model = joblib.load('best_price_model.pkl')
        is_ann = False
    else:
        from tensorflow.keras.models import load_model
        price_model = load_model('best_price_model.h5')
        is_ann = True
 
    price_scaler = joblib.load('price_scaler.pkl')
    cluster_model = joblib.load('best_cluster_model.pkl')
    cluster_scaler = joblib.load('cluster_scaler.pkl')
    pca = joblib.load('pca_transform.pkl')
    cluster_names = joblib.load('cluster_names.pkl')
    encoding_maps = joblib.load('encoding_maps.pkl')
    return price_model, price_scaler, cluster_model, cluster_scaler, pca, cluster_names, encoding_maps, is_ann
 
price_model, price_scaler, cluster_model, cluster_scaler, pca, cluster_names, encoding_maps, is_ann = load_artifacts()
 
cut_order = encoding_maps['cut_order']
color_order = encoding_maps['color_order']
clarity_order = encoding_maps['clarity_order']
 
st.set_page_config(page_title="Diamond Dynamics", page_icon="💎", layout="centered")
 
st.title("💎 Diamond Dynamics")
st.subheader("Price Prediction & Market Segmentation")
 
st.markdown("Enter the diamond's attributes below to predict its price (INR) and identify its market segment.")
 
# ----------------------------
# Input form
# ----------------------------
col1, col2 = st.columns(2)
 
with col1:
    carat = st.number_input("Carat", min_value=0.01, max_value=6.0, value=0.5, step=0.01)
    x = st.number_input("Length - x (mm)", min_value=0.1, max_value=15.0, value=5.0, step=0.01)
    y = st.number_input("Width - y (mm)", min_value=0.1, max_value=15.0, value=5.0, step=0.01)
    z = st.number_input("Depth - z (mm)", min_value=0.1, max_value=15.0, value=3.0, step=0.01)
 
with col2:
    depth = st.number_input("Depth %", min_value=40.0, max_value=80.0, value=61.5, step=0.1)
    table = st.number_input("Table %", min_value=40.0, max_value=80.0, value=57.0, step=0.1)
    cut = st.selectbox("Cut", cut_order, index=4)
    color = st.selectbox("Color", color_order, index=5)
    clarity = st.selectbox("Clarity", clarity_order, index=4)
 
# ----------------------------
# Feature preparation
# ----------------------------
def prepare_features():
    cut_enc = cut_order.index(cut)
    color_enc = color_order.index(color)
    clarity_enc = clarity_order.index(clarity)
    volume = x * y * z
    dimension_ratio = (x + y) / (2 * z) if z != 0 else 0
 
    price_features = pd.DataFrame([{
        'carat': carat, 'cut_enc': cut_enc, 'color_enc': color_enc, 'clarity_enc': clarity_enc,
        'depth': depth, 'table': table, 'x': x, 'y': y, 'z': z,
        'volume': volume, 'dimension_ratio': dimension_ratio
    }])
 
    cluster_features = pd.DataFrame([{
        'carat': carat, 'cut_enc': cut_enc, 'color_enc': color_enc, 'clarity_enc': clarity_enc,
        'depth': depth, 'table': table, 'x': x, 'y': y, 'z': z
    }])
 
    return price_features, cluster_features
 
price_features, cluster_features = prepare_features()
 
st.divider()
 
pcol1, pcol2 = st.columns(2)
 
# ----------------------------
# Price Prediction
# ----------------------------
with pcol1:
    if st.button("🎯 Predict Price", use_container_width=True):
        scaled = price_scaler.transform(price_features)
        pred = price_model.predict(scaled)
        predicted_price = float(pred.flatten()[0]) if is_ann else float(pred[0])
        st.success(f"Predicted Price: ₹ {predicted_price:,.2f}")
 
# ----------------------------
# Cluster Prediction
# ----------------------------
with pcol2:
    if st.button("🧭 Predict Market Segment", use_container_width=True):
        scaled_c = cluster_scaler.transform(cluster_features)
        cluster_id = cluster_model.predict(scaled_c)[0]
        cluster_label = cluster_names.get(cluster_id, f"Cluster {cluster_id}")
        st.info(f"Cluster: {cluster_id} — **{cluster_label}**")
 
        pca_point = pca.transform(scaled_c)
        st.caption(f"PCA projection: ({pca_point[0][0]:.2f}, {pca_point[0][1]:.2f})")
 
st.divider()
st.caption("Model trained on the Diamonds dataset (53,940 records) using Random Forest / XGBoost / ANN regression and K-Means clustering.")