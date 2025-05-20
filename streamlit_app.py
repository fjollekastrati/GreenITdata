import altair as alt
import pandas as pd
import streamlit as st

# Configure the Streamlit page
st.set_page_config(page_title="Website Emissions Dashboard", page_icon="🌿")

# Title and description
st.title("🌿 Website Emissions Dashboard")
st.write(
    """
    This app visualizes website emissions data using Google's Lighthouse Emissions metrics.
    Explore how different websites perform in terms of their carbon footprint and environmental impact.
    Use the widgets below to filter and analyze the data!
    """
)

# Load the data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("data/website_emissions_summary.csv")
    return df

df = load_data()

# Widgets for filtering
categories = st.multiselect(
    "Select Website Categories",
    options=df["category"].unique(),
    default=list(df["category"].unique())[:3],  # default to first 3 categories
)

years = st.slider(
    "Select Year Range",
    int(df["year"].min()),
    int(df["year"].max()),
    (int(df["year"].min()), int(df["year"].max())),
)

# Filter data based on widget inputs
df_filtered = df[
    (df["category"].isin(categories)) &
    (df["year"].between(years[0], years[1]))
]

# Pivot data to have years as index and categories as columns with mean emissions
df_reshaped = df_filtered.pivot_table(
    index="year",
    columns="category",
    values="emissions",
    aggfunc="mean",
    fill_value=0
).sort_index()

# Display the filtered data as a table
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Year")},
)

# Prepare data for Altair chart
df_chart = pd.melt(
    df_reshaped.reset_index(),
    id_vars="year",
    var_name="category",
    value_name="emissions"
)

# Create the emissions line chart
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("emissions:Q", title="Average Emissions (gCO2)"),
        color=alt.Color("category:N", title="Website Category"),
        tooltip=["year", "category", "emissions"],
    )
    .properties(height=320)
)

# Show the chart in the app
st.altair_chart(chart, use_container_width=True)
