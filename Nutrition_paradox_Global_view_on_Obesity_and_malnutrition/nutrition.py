"""
Nutrition Paradox - Streamlit Dashboard
Connects to MySQL (obesity_table, malnutrition_table), runs all 25 analysis
queries, and shows interactive tables + EDA visualizations.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Nutrition Paradox Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# 1. Database connection
# ---------------------------------------------------------------------------
st.sidebar.header("Database Connection")

username = st.sidebar.text_input("Username", value="root")
password = st.sidebar.text_input("Password", value="1234")
host = st.sidebar.text_input("Host", value="localhost")
port = st.sidebar.text_input("Port", value="3306")
database = st.sidebar.text_input("Database", value="nutrition_project")

@st.cache_resource
def get_engine(username, password, host, port, database):
    return create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    )

engine = get_engine(username, password, host, port, database)

@st.cache_data(ttl=600)
def run_query(query):
    return pd.read_sql(text(query), con=engine)

# ---------------------------------------------------------------------------
# 2. All 25 queries
# ---------------------------------------------------------------------------
QUERIES = {
    "1. Top 5 regions - highest avg obesity 2022": """
        SELECT Region, AVG(Mean_Estimate) AS avg_obesity
        FROM obesity_table WHERE Year = 2022
        GROUP BY Region ORDER BY avg_obesity DESC LIMIT 5;""",

    "2. Top 5 countries - highest obesity": """
        SELECT Country, AVG(Mean_Estimate) AS avg_obesity
        FROM obesity_table GROUP BY Country
        ORDER BY avg_obesity DESC LIMIT 5;""",

    "3. Obesity trend in India": """
        SELECT Year, AVG(Mean_Estimate) AS avg_obesity
        FROM obesity_table WHERE Country = 'India'
        GROUP BY Year ORDER BY Year;""",

    "4. Average obesity by gender": """
        SELECT Gender, AVG(Mean_Estimate) AS avg_obesity
        FROM obesity_table GROUP BY Gender;""",

    "5. Country count by obesity level & age group": """
        SELECT Obesity_level, Age_Group, COUNT(DISTINCT Country) AS country_count
        FROM obesity_table GROUP BY Obesity_level, Age_Group
        ORDER BY Obesity_level, Age_Group;""",

    "6a. Top 5 least reliable countries (highest CI_Width)": """
        SELECT Country, AVG(CI_Width) AS avg_ci_width
        FROM obesity_table GROUP BY Country
        ORDER BY avg_ci_width DESC LIMIT 5;""",

    "6b. Top 5 most consistent countries (lowest CI_Width)": """
        SELECT Country, AVG(CI_Width) AS avg_ci_width
        FROM obesity_table GROUP BY Country
        ORDER BY avg_ci_width ASC LIMIT 5;""",

    "7. Average obesity by age group": """
        SELECT Age_Group, AVG(Mean_Estimate) AS avg_obesity
        FROM obesity_table GROUP BY Age_Group;""",

    "8. Top 10 countries - consistent low obesity": """
        SELECT Country, AVG(Mean_Estimate) AS avg_obesity, AVG(CI_Width) AS avg_ci_width
        FROM obesity_table GROUP BY Country
        ORDER BY avg_obesity ASC, avg_ci_width ASC LIMIT 10;""",

    "9. Countries - female obesity exceeds male": """
        SELECT f.Country, f.Year, f.Mean_Estimate AS female_estimate,
               m.Mean_Estimate AS male_estimate,
               (f.Mean_Estimate - m.Mean_Estimate) AS difference
        FROM obesity_table f
        JOIN obesity_table m ON f.Country = m.Country AND f.Year = m.Year
        WHERE f.Gender = 'Female' AND m.Gender = 'Male'
        ORDER BY difference DESC LIMIT 10;""",

    "10. Global average obesity per year": """
        SELECT Year, AVG(Mean_Estimate) AS global_avg_obesity
        FROM obesity_table GROUP BY Year ORDER BY Year;""",

    "11. Average malnutrition by age group": """
        SELECT Age_Group, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table GROUP BY Age_Group;""",

    "12. Top 5 countries - highest malnutrition": """
        SELECT Country, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table GROUP BY Country
        ORDER BY avg_malnutrition DESC LIMIT 5;""",

    "13. Malnutrition trend - Africa": """
        SELECT Year, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table WHERE Region = 'Africa'
        GROUP BY Year ORDER BY Year;""",

    "14. Gender-based average malnutrition": """
        SELECT Gender, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table GROUP BY Gender;""",

    "15. Avg CI_Width by level & age group": """
        SELECT Malnutrition_Level, Age_Group, AVG(CI_Width) AS avg_ci_width
        FROM malnutrition_table GROUP BY Malnutrition_Level, Age_Group
        ORDER BY Malnutrition_Level, Age_Group;""",

    "16. Yearly malnutrition - India, Nigeria, Brazil": """
        SELECT Country, Year, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table
        WHERE Country IN ('India', 'Nigeria', 'Brazil')
        GROUP BY Country, Year ORDER BY Country, Year;""",

    "17. Regions with lowest malnutrition": """
        SELECT Region, AVG(Mean_Estimate) AS avg_malnutrition
        FROM malnutrition_table GROUP BY Region
        ORDER BY avg_malnutrition ASC LIMIT 5;""",

    "18. Countries with increasing malnutrition": """
        SELECT Country,
               MIN(Mean_Estimate) AS earliest_estimate,
               MAX(Mean_Estimate) AS recent_estimate,
               (MAX(Mean_Estimate) - MIN(Mean_Estimate)) AS increase
        FROM malnutrition_table GROUP BY Country
        HAVING (MAX(Mean_Estimate) - MIN(Mean_Estimate)) > 0
        ORDER BY increase DESC;""",

    "19. Min/Max malnutrition year-wise": """
        SELECT Year, MIN(Mean_Estimate) AS min_malnutrition,
               MAX(Mean_Estimate) AS max_malnutrition
        FROM malnutrition_table GROUP BY Year ORDER BY Year;""",

    "20. High CI_Width flags (>5)": """
        SELECT Country, Year, Gender, Age_Group, Mean_Estimate, CI_Width
        FROM malnutrition_table WHERE CI_Width > 5
        ORDER BY CI_Width DESC;""",

    "21. Obesity vs malnutrition - 5 countries": """
        SELECT o.Country, AVG(o.Mean_Estimate) AS avg_obesity,
               AVG(m.Mean_Estimate) AS avg_malnutrition
        FROM obesity_table o
        JOIN malnutrition_table m ON o.Country = m.Country AND o.Year = m.Year
        WHERE o.Country IN ('India', 'Nigeria', 'Brazil', 'United States', 'Germany')
        GROUP BY o.Country;""",

    "22. Gender-based disparity - both datasets": """
        SELECT o.Gender, AVG(o.Mean_Estimate) AS avg_obesity,
               AVG(m.Mean_Estimate) AS avg_malnutrition
        FROM obesity_table o
        JOIN malnutrition_table m
          ON o.Gender = m.Gender AND o.Year = m.Year AND o.Country = m.Country
        GROUP BY o.Gender;""",

    "23. Region-wise avg - Africa & Americas": """
        SELECT o.Region, AVG(o.Mean_Estimate) AS avg_obesity,
               AVG(m.Mean_Estimate) AS avg_malnutrition
        FROM obesity_table o
        JOIN malnutrition_table m ON o.Region = m.Region AND o.Year = m.Year
        WHERE o.Region IN ('Africa', 'Americas')
        GROUP BY o.Region;""",

    # NOTE: requires MySQL 8.0+ for WITH (CTE) support.
    "24. Obesity up & malnutrition down": """
        WITH obesity_yearly AS (
            SELECT Country, Year, AVG(Mean_Estimate) AS avg_estimate
            FROM obesity_table GROUP BY Country, Year),
        malnutrition_yearly AS (
            SELECT Country, Year, AVG(Mean_Estimate) AS avg_estimate
            FROM malnutrition_table GROUP BY Country, Year),
        obesity_range AS (
            SELECT Country, MIN(Year) AS min_year, MAX(Year) AS max_year
            FROM obesity_yearly GROUP BY Country),
        malnutrition_range AS (
            SELECT Country, MIN(Year) AS min_year, MAX(Year) AS max_year
            FROM malnutrition_yearly GROUP BY Country)
        SELECT orng.Country,
               (o2.avg_estimate - o1.avg_estimate) AS obesity_change,
               (m2.avg_estimate - m1.avg_estimate) AS malnutrition_change
        FROM obesity_range orng
        JOIN obesity_yearly o1 ON o1.Country = orng.Country AND o1.Year = orng.min_year
        JOIN obesity_yearly o2 ON o2.Country = orng.Country AND o2.Year = orng.max_year
        JOIN malnutrition_range mrng ON mrng.Country = orng.Country
        JOIN malnutrition_yearly m1 ON m1.Country = mrng.Country AND m1.Year = mrng.min_year
        JOIN malnutrition_yearly m2 ON m2.Country = mrng.Country AND m2.Year = mrng.max_year
        WHERE (o2.avg_estimate - o1.avg_estimate) > 0
          AND (m2.avg_estimate - m1.avg_estimate) < 0
        ORDER BY obesity_change DESC;""",

    "25. Age-wise trend analysis": """
        SELECT o.Age_Group, o.Year, o.avg_obesity, m.avg_malnutrition
        FROM (SELECT Age_Group, Year, AVG(Mean_Estimate) AS avg_obesity
              FROM obesity_table GROUP BY Age_Group, Year) o
        JOIN (SELECT Age_Group, Year, AVG(Mean_Estimate) AS avg_malnutrition
              FROM malnutrition_table GROUP BY Age_Group, Year) m
          ON o.Age_Group = m.Age_Group AND o.Year = m.Year
        ORDER BY o.Age_Group, o.Year;""",
}

# ---------------------------------------------------------------------------
# 3. Layout - tabs
# ---------------------------------------------------------------------------
st.title("🍽️ Nutrition Paradox Dashboard")
st.caption("Obesity vs Malnutrition — WHO GHO data (Obesity & Malnutrition tables)")

tab_queries, tab_eda = st.tabs(["📋 SQL Query Results (All 25)", "📊 EDA Visualizations"])

# --- Tab 1: All 25 queries as interactive tables ---
with tab_queries:
    st.subheader("Run and explore all 25 analysis queries")
    selected = st.selectbox("Choose a query to view", list(QUERIES.keys()))

    try:
        df_result = run_query(QUERIES[selected])
        st.dataframe(df_result, use_container_width=True)
        st.download_button(
            "Download this result as CSV",
            df_result.to_csv(index=False),
            file_name=f"{selected.split('.')[0]}_result.csv",
        )
    except Exception as e:
        st.error(f"Query failed: {e}")

    with st.expander("Show all 25 queries at once (may take a moment)"):
        if st.button("Run all queries"):
            for name, q in QUERIES.items():
                st.markdown(f"**{name}**")
                try:
                    st.dataframe(run_query(q), use_container_width=True)
                except Exception as e:
                    st.error(f"{name} failed: {e}")

# --- Tab 2: EDA visualizations ---
with tab_eda:
    st.subheader("Exploratory visualizations")

    try:
        obesity_all = run_query("SELECT * FROM obesity_table;")
        malnutrition_all = run_query("SELECT * FROM malnutrition_table;")
    except Exception as e:
        st.error(f"Could not load base tables: {e}")
        obesity_all, malnutrition_all = pd.DataFrame(), pd.DataFrame()

    if not obesity_all.empty and not malnutrition_all.empty:

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**1. Global obesity & malnutrition trend over years**")
            ob_trend = obesity_all.groupby("Year")["Mean_Estimate"].mean().reset_index()
            mal_trend = malnutrition_all.groupby("Year")["Mean_Estimate"].mean().reset_index()
            ob_trend["Type"] = "Obesity"
            mal_trend["Type"] = "Malnutrition"
            trend_combined = pd.concat([ob_trend, mal_trend], ignore_index=True)
            fig1 = px.line(trend_combined, x="Year", y="Mean_Estimate", color="Type", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("**2. Top 10 countries by obesity**")
            top10 = (
                obesity_all.groupby("Country")["Mean_Estimate"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            fig2 = px.bar(top10, x="Mean_Estimate", y="Country", orientation="h")
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**3. Obesity by region (map)**")
            region_avg = obesity_all.groupby("Country")["Mean_Estimate"].mean().reset_index()
            fig3 = px.choropleth(
                region_avg, locations="Country", locationmode="country names",
                color="Mean_Estimate", color_continuous_scale="Reds",
                title="Average Obesity by Country"
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("**4. Obesity & malnutrition by gender (stacked bar)**")
            ob_gender = obesity_all.groupby("Gender")["Mean_Estimate"].mean().reset_index()
            ob_gender["Type"] = "Obesity"
            mal_gender = malnutrition_all.groupby("Gender")["Mean_Estimate"].mean().reset_index()
            mal_gender["Type"] = "Malnutrition"
            gender_combined = pd.concat([ob_gender, mal_gender], ignore_index=True)
            fig4 = px.bar(gender_combined, x="Gender", y="Mean_Estimate", color="Type", barmode="stack")
            st.plotly_chart(fig4, use_container_width=True)

        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**5. Country count by obesity level**")
            level_counts = obesity_all.groupby("Obesity_level")["Country"].nunique().reset_index()
            level_counts.columns = ["Obesity_level", "Country_Count"]
            fig5 = px.pie(level_counts, names="Obesity_level", values="Country_Count")
            st.plotly_chart(fig5, use_container_width=True)

        with col6:
            st.markdown("**6. CI_Width heatmap by region & year**")
            pivot = obesity_all.pivot_table(values="CI_Width", index="Region", columns="Year", aggfunc="mean")
            fig6 = px.imshow(pivot, aspect="auto", color_continuous_scale="YlOrRd")
            st.plotly_chart(fig6, use_container_width=True)

        st.markdown("**7. Obesity vs malnutrition trend — pick a country**")
        country_choice = st.selectbox("Country", sorted(obesity_all["Country"].dropna().unique()))
        ob_c = obesity_all[obesity_all["Country"] == country_choice].groupby("Year")["Mean_Estimate"].mean().reset_index()
        mal_c = malnutrition_all[malnutrition_all["Country"] == country_choice].groupby("Year")["Mean_Estimate"].mean().reset_index()
        ob_c["Type"] = "Obesity"
        mal_c["Type"] = "Malnutrition"
        dual = pd.concat([ob_c, mal_c], ignore_index=True)
        fig7 = px.line(dual, x="Year", y="Mean_Estimate", color="Type", markers=True)
        st.plotly_chart(fig7, use_container_width=True)

        col8, col9 = st.columns(2)

        with col8:
            st.markdown("**8. Obesity vs malnutrition per country (scatter)**")
            ob_avg = obesity_all.groupby("Country")["Mean_Estimate"].mean().reset_index(name="avg_obesity")
            mal_avg = malnutrition_all.groupby("Country")["Mean_Estimate"].mean().reset_index(name="avg_malnutrition")
            merged = ob_avg.merge(mal_avg, on="Country")
            fig8 = px.scatter(merged, x="avg_obesity", y="avg_malnutrition", hover_name="Country")
            st.plotly_chart(fig8, use_container_width=True)

        with col9:
            st.markdown("**9. Obesity burden by region (treemap)**")
            fig9 = px.treemap(obesity_all, path=["Region", "Country"], values="Mean_Estimate")
            st.plotly_chart(fig9, use_container_width=True)

        st.markdown("**10. Age group & gender breakdown (box plot)**")
        fig10 = px.box(obesity_all, x="Age_Group", y="Mean_Estimate", color="Gender")
        st.plotly_chart(fig10, use_container_width=True)

    else:
        st.info("Connect to the database using the sidebar to load EDA visuals.")
