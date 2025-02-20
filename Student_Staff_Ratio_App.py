import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Student to Staff Ratios", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Comparisons with Other Schools")

# Cache the data loading function to improve performance
@st.cache_data
def load_data():
    df = pd.read_csv("filtered_school_data.csv")
    return df

# Load the data
df = load_data()
# Recreate the column_labels_dict to match Streamlit display labels
column_labels_dict = {col: col.replace("_", " ").title() for col in df.columns}

# Create a unique identifier for schools (concatenating name, suburb, and state)
df["school_identifier"] = df["school_name"] + " (" + df["suburb"] + ", " + df["state"] + ")"

# Sidebar for selecting schools
st.sidebar.title("School Selection")
st.sidebar.markdown("**Select one or more schools** from the list below to compare their FTE Student-Staff Ratio over time.")

# Ensure unique selection by displaying full school details
schools = df["school_identifier"].unique()
selected_schools = st.sidebar.multiselect("Select Schools:", schools, default=["Ilim College (Dallas, VIC)"])

# Extract the corresponding school names from the selected identifiers
selected_school_names = df[df["school_identifier"].isin(selected_schools)]["school_name"].unique()

# Sidebar for selecting comparator
st.sidebar.title("Comparator Selection")
st.sidebar.markdown("**Choose a comparator** to overlay on the graph. This helps compare selected schools against a broader benchmark.")

comparator_options = ["National Median", "State Median", "Sector Median"]
selected_comparator = st.sidebar.radio("Choose Comparator:", comparator_options)

# Filter dataset for selected schools
filtered_df = df[df["school_identifier"].isin(selected_schools)]

# Plot FTE_Student_Staff_Ratio over time
fig = px.line(
    filtered_df,
    x="calendar_year",
    y="fte_student_staff_ratio",
    color="school_identifier",
    title="FTE Student-Staff Ratio Over Time",
    labels={"fte_student_staff_ratio": "Student to Staff Ratio", "calendar_year": "Year", "school_identifier": ""},
    markers=True
)

# Add the selected comparator line
if selected_comparator == "National Median":
    comparator_df = df.groupby("calendar_year")["national_median"].mean().reset_index()
    fig.add_scatter(x=comparator_df["calendar_year"], y=comparator_df["national_median"], 
                    mode="lines", name="National Median")

elif selected_comparator == "State Median":
    state_medians = df.groupby(["calendar_year", "state"])["state_median"].mean().reset_index()
    for state in filtered_df["state"].unique():
        state_df = state_medians[state_medians["state"] == state]
        fig.add_scatter(x=state_df["calendar_year"], y=state_df["state_median"], 
                        mode="lines", name=f"{state} State Median")

elif selected_comparator == "Sector Median":
    sector_medians = df.groupby(["calendar_year", "school_sector"])["sector_median"].mean().reset_index()
    for sector in filtered_df["school_sector"].unique():
        sector_df = sector_medians[sector_medians["school_sector"] == sector]
        fig.add_scatter(x=sector_df["calendar_year"], y=sector_df["sector_median"], 
                        mode="lines", name=f"{sector} Sector Median")

# Display the plot
st.plotly_chart(fig)


# Automatically map column names to Title Case using column_labels_dict
column_config_dict = {col: st.column_config.TextColumn(label) for col, label in column_labels_dict.items()}

# Override specific columns that need numeric formatting
column_config_dict.update({
    "calendar_year": st.column_config.NumberColumn("Year", format="%d"),
    "icsea": st.column_config.NumberColumn("ICSEA", format="%d"),
    "fte_student_staff_ratio": st.column_config.NumberColumn("FTE Student-Staff Ratio", format="%.2f"),
    "national_median": st.column_config.NumberColumn("National Median Ratio", format="%.2f"),
    "state_median": st.column_config.NumberColumn("State Median Ratio", format="%.2f"),
    "sector_median": st.column_config.NumberColumn("School Sector Median", format="%.2f")
})

# Display the dataframe with updated labels
# Debugging outputs
st.write('''Data sourced from [ACARA Data Access Program](https://acara.edu.au/contact-us/acara-data-access) Schools Profile 2008-2024.
This app used 2014-2024 data only. ''')
st.write(f"Selected Schools: {selected_schools}")
st.write(f"Filtered Data: {filtered_df.shape[0]} rows")
st.dataframe(filtered_df, width=5000, height=300, hide_index=True, column_config=column_config_dict)

