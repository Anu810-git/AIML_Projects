import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from streamlit_option_menu import option_menu


st.markdown("""
<h1 style="margin-bottom:40px;">
🚀 NASA Asteroid Tracker 🌟
</h1>
""", unsafe_allow_html=True)


engine = create_engine('mysql+pymysql://root:1234@localhost/project_db')
conn = engine.connect()

with st.sidebar:
    selected = option_menu(
        menu_title="Asteroid Approaches",
        options=["Filter Criteria", "Queries"],
        icons=["calendar", "grid"],  
        default_index=0,
    )

if selected == "Filter Criteria":
    col1, col2, col3 = st.columns(3)

    with col1:
        mag_min = st.slider("Min Magnitude", 13.8, 32.61, (13.8, 32.61))
        st.write(f"Selected Magnitude Range: {mag_min[0]} to {mag_min[1]}")

        dia_min = st.slider("Min Estimated Diameter (km)", 0.00, 4.62, (0.00, 4.62))
        st.write(f"Selected Min Diameter Range: {dia_min[0]} to {dia_min[1]}")

        dia_max = st.slider("Max Estimated Diameter (km)", 0.00, 10.33, (0.00, 10.33))
        st.write(f"Selected Max Diameter Range: {dia_max[0]} to {dia_max[1]}")

    with col2:
        vel_min = st.slider("Relative_velocity_kmph Range", 1418.21, 173071.83, (1418.21, 173071.83))
        st.write(f"Selected velocity Range: {vel_min[0]} to {vel_min[1]}")

        au_min = st.slider("Astronomical unit", 0.00, 0.50, (0.00, 0.50))
        st.write(f"Selected Astronomical Unit Range: {au_min[0]} to {au_min[1]}")

        hazardous_option = st.selectbox("Only Show Potentially Hazardous", options=[0, 1])
        st.write(f"Hazardous Filter: {hazardous_option}")

    with col3:
        start_date = st.date_input("Start Date", pd.to_datetime("2024-01-01"))
        end_date = st.date_input("End Date", pd.to_datetime("2025-04-13"))
        st.write(f"Date Range: {start_date} to {end_date}")
    
    st.markdown("<br>", unsafe_allow_html=True)

   
    if st.button("Filter"):
        query = """
        SELECT
            a.id,a.name,a.absolute_magnitude_h, a.estimated_diameter_min_km, a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid, ca.close_approach_date,
            ca.relative_velocity_kmph,ca.astronomical,ca.miss_distance_km FROM asteroids_table a JOIN close_approach_table ca ON a.id = ca.neo_reference_id
        """

        filtered_df = pd.read_sql(query, conn)

     
        filtered_df["absolute_magnitude_h"] = pd.to_numeric(filtered_df["absolute_magnitude_h"], errors="coerce")
        filtered_df["estimated_diameter_min_km"] = pd.to_numeric(filtered_df["estimated_diameter_min_km"], errors="coerce")
        filtered_df["estimated_diameter_max_km"] = pd.to_numeric(filtered_df["estimated_diameter_max_km"], errors="coerce")
        
        filtered_df["relative_velocity_kmph"] = (
            filtered_df["relative_velocity_kmph"].astype(str).str.replace(",", "").str.strip()
        )
        filtered_df["relative_velocity_kmph"] = pd.to_numeric(filtered_df["relative_velocity_kmph"], errors="coerce")
        filtered_df["astronomical"] = pd.to_numeric(filtered_df["astronomical"], errors="coerce")
        filtered_df["miss_distance_km"] = pd.to_numeric(filtered_df["miss_distance_km"], errors="coerce")
        filtered_df["is_potentially_hazardous_asteroid"] = pd.to_numeric(filtered_df["is_potentially_hazardous_asteroid"], errors="coerce")

        numeric_cols = ["absolute_magnitude_h", "estimated_diameter_min_km", 
            "estimated_diameter_max_km", "relative_velocity_kmph", 
            "astronomical", "miss_distance_km", "is_potentially_hazardous_asteroid"]
        filtered_df = filtered_df.dropna(subset=numeric_cols)

       
        filtered_df = filtered_df[
            (filtered_df["absolute_magnitude_h"] >= mag_min[0]) & (filtered_df["absolute_magnitude_h"] <= mag_min[1]) &
            (filtered_df["estimated_diameter_min_km"] >= dia_min[0]) & (filtered_df["estimated_diameter_min_km"] <= dia_min[1]) &
            (filtered_df["estimated_diameter_max_km"] >= dia_max[0]) & (filtered_df["estimated_diameter_max_km"] <= dia_max[1]) &
            (filtered_df["relative_velocity_kmph"] >= vel_min[0]) & (filtered_df["relative_velocity_kmph"] <= vel_min[1]) &
            (filtered_df["astronomical"] >= au_min[0]) & (filtered_df["astronomical"] <= au_min[1])
        ]

     
        filtered_df["close_approach_date"] = pd.to_datetime(filtered_df["close_approach_date"], errors="coerce")
        filtered_df = filtered_df[
            (filtered_df["close_approach_date"] >= pd.to_datetime(start_date)) & 
            (filtered_df["close_approach_date"] <= pd.to_datetime(end_date))
        ]

        
        filtered_df = filtered_df[filtered_df["is_potentially_hazardous_asteroid"] == hazardous_option]

        st.write("Total Records:", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)



if selected == "Queries":
    option = st.selectbox(
        "Select a query",
        ("1. List all the asteroids",
         "2. Count how many times each asteroid has approached Earth",
         "3. Average velocity of each asteroid over multiple approaches",
         "4. Find potentially hazardous asteroids that have approached Earth more than 3 times",
         "5. Find the month with the most asteroid approaches",
         "6. Get the asteroid with the fastest ever approach speed",
         "7. Sort asteroids by maximum estimated diameter (descending)",
         "8. Asteroid whose closest approach is getting nearer over time",
         "9. Name, date, and miss distance of each asteroid's closest approach",
         "10. Asteroids that approached Earth with velocity > 50,000 km/h",
         "11. Count how many approaches happened per month",
         "12. Asteroid with the highest brightness (lowest magnitude value)",
         "13. Get number of hazardous vs non-hazardous asteroids",
         "14. Asteroids that passed closer than the Moon (< 1 LD)",
         "15. Asteroids that came within 0.05 AU"),
    )

    if option == "1. List all the asteroids":
        df = pd.read_sql("SELECT name AS names_of_asteroids FROM asteroids_table", conn)
        st.dataframe(df)

    elif option == "2. Count how many times each asteroid has approached Earth":
        select_query = """
        SELECT ca.neo_reference_id, COUNT(*) AS approach_count
        FROM close_approach_table ca
        GROUP BY ca.neo_reference_id
        ORDER BY approach_count DESC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "3. Average velocity of each asteroid over multiple approaches":
        select_query = """
        SELECT AVG(relative_velocity_kmph) AS avg_velocity_kmph
        FROM close_approach_table
        GROUP BY neo_reference_id
        ORDER BY avg_velocity_kmph DESC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "4. Find potentially hazardous asteroids that have approached Earth more than 3 times":
        select_query = """
        SELECT a.name, COUNT(*) AS approach_count
        FROM asteroids_table a
        JOIN close_approach_table ca ON a.id = ca.neo_reference_id
        WHERE a.is_potentially_hazardous_asteroid = 1
        GROUP BY a.id, a.name
        HAVING COUNT(*) > 3
        ORDER BY approach_count DESC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "5. Find the month with the most asteroid approaches":
        select_query = """
        SELECT DATE_FORMAT(close_approach_date, '%%Y-%%m') AS approach_month, COUNT(*) AS approach_count
        FROM close_approach_table
        GROUP BY approach_month
        ORDER BY approach_count DESC
        LIMIT 1;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "6. Get the asteroid with the fastest ever approach speed":
        select_query = """
        SELECT a.name, ca.relative_velocity_kmph
        FROM close_approach_table ca
        JOIN (SELECT DISTINCT id, name FROM asteroids_table) a ON ca.neo_reference_id = a.id
        ORDER BY ca.relative_velocity_kmph DESC
        LIMIT 1;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "7. Sort asteroids by maximum estimated diameter (descending)":
        select_query = """
        SELECT name, estimated_diameter_max_km
        FROM asteroids_table
        ORDER BY estimated_diameter_max_km DESC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "8. Asteroid whose closest approach is getting nearer over time":
        select_query = """
        SELECT neo_reference_id, close_approach_date, miss_distance_km
        FROM close_approach_table
        ORDER BY neo_reference_id, close_approach_date;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "9. Name, date, and miss distance of each asteroid's closest approach":
        select_query = """
        SELECT a.name, ca.close_approach_date, ca.miss_distance_km
        FROM close_approach_table ca
        JOIN (SELECT DISTINCT id, name FROM asteroids_table) a ON ca.neo_reference_id = a.id
        WHERE ca.miss_distance_km = (
            SELECT MIN(ca2.miss_distance_km)
            FROM close_approach_table ca2
            WHERE ca2.neo_reference_id = ca.neo_reference_id
        )
        ORDER BY ca.miss_distance_km ASC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "10. Asteroids that approached Earth with velocity > 50,000 km/h":
        select_query = """
        SELECT DISTINCT a.name, ca.relative_velocity_kmph, ca.close_approach_date
        FROM close_approach_table ca
        JOIN (SELECT DISTINCT id, name FROM asteroids_table) a ON ca.neo_reference_id = a.id
        WHERE ca.relative_velocity_kmph > 50000
        ORDER BY ca.relative_velocity_kmph DESC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "11. Count how many approaches happened per month":
        select_query = """
        SELECT DATE_FORMAT(close_approach_date, '%%Y-%%m') AS approach_month, COUNT(*) AS approach_count
        FROM close_approach_table
        GROUP BY approach_month
        ORDER BY approach_month;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "12. Asteroid with the highest brightness (lowest magnitude value)":
        select_query = """
        SELECT DISTINCT name, absolute_magnitude_h
        FROM asteroids_table
        ORDER BY absolute_magnitude_h ASC
        LIMIT 1;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "13. Get number of hazardous vs non-hazardous asteroids":
        select_query = """
        SELECT is_potentially_hazardous_asteroid, COUNT(*) AS asteroid_count
        FROM (SELECT DISTINCT id, is_potentially_hazardous_asteroid FROM asteroids_table) AS a
        GROUP BY is_potentially_hazardous_asteroid;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "14. Asteroids that passed closer than the Moon (< 1 LD)":
        select_query = """
        SELECT a.name, ca.close_approach_date, ca.miss_distance_lunar, ca.miss_distance_km
        FROM close_approach_table ca
        JOIN (SELECT DISTINCT id, name FROM asteroids_table) a ON ca.neo_reference_id = a.id
        WHERE ca.miss_distance_lunar < 1
        ORDER BY ca.miss_distance_lunar ASC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)

    elif option == "15. Asteroids that came within 0.05 AU":
        select_query = """
        SELECT DISTINCT a.name, ca.close_approach_date, ca.astronomical
        FROM close_approach_table ca
        JOIN (SELECT DISTINCT id, name FROM asteroids_table) a ON ca.neo_reference_id = a.id
        WHERE ca.astronomical <= 0.05
        ORDER BY ca.astronomical ASC;
        """
        df1 = pd.read_sql(select_query, conn)
        st.dataframe(df1)