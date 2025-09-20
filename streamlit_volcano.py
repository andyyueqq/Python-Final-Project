"""Class: CS230--Section 1 Name: Xiangyu Yue
Description: Volcanoes data explorations including charts, forms, pictures, maps, and so on.
Final
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student. """

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

# st.set_page_config from "Streamlit Documentation", must be the first command
st.set_page_config(
    page_title="Volcanoes",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg/600px-Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg"
)

# Chapter 15.3 Displaying text, use markdown because there is a picture included
st.markdown(
    """
    <style>
    html, body, .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg/600px-Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    header, .stApp header {
        background: rgba(255, 255, 255, 0.0);
    }
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.05);
    }
    .stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-color: rgba(255, 255, 255, 0.2); 
    z-index: 0;
}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='color: steelblue; padding-top: 0'>
        Welcome to Volcano Data Explorer
    <h3 style='color: steelblue; padding-top: 0'>
        Scroll Down to See More ⬇️
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg/600px-Augustine_volcano_Jan_24_2006_-_Cyrus_Read.jpg" 
         style="width: 15%; ">
         
    """,
    unsafe_allow_html=True,
)
st.markdown("<hr style='border: 2px solid steelblue'>", unsafe_allow_html=True)

# Chapter 15.11 Caching to manipulate large data sets faster
DATA_URL = "volcanoes(in).csv"
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL, header=1)
    data = data.dropna(subset=["Volcano Name", "Latitude", "Longitude"])
    return data
#Drop rows with NaN in these columns <-
volcano_data = load_data()


# A function with three parameters, two have default values
# This function is called twice
def vol_tecto(data, region=None, tectonic=None):
    """Filter by region and/or tectonic setting."""
    if region:
        data = data[data["Volcanic Region"] == region]
    if tectonic:
        data = data[data["Tectonic Setting"] == tectonic]
    return data

def calculate_stats(data):
    """Calculate min, max, and mean of elevation."""
    return (data["Elevation (m)"].min(),
            data["Elevation (m)"].max(),
            data["Elevation (m)"].mean())

def convert_to_year(y):
    '''This part try to convert BCE and CE and unknown Year'''
    y = y.lower()
    # Convert unknown to None
    # Convert BCE years to negative, CE to positive
    if "unknown" in y:
        return None
    if "bce" in y:
        return -int(y.split(" ")[0])
    elif "ce" in y:
        return int(y.split(" ")[0])

#List Comprehension and assign new column
volcano_data["Eruption Year"] = [convert_to_year(x) for x in volcano_data["Last Known Eruption"]]

# Sidebar navigation
st.sidebar.markdown(
    """
    <div style="
        background: rgba(70, 130, 180, 0.7);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    ">
        Select Analysis Here
    </div>
    """,
    unsafe_allow_html=True
)


option = st.sidebar.selectbox(
    " ",
    ["Elevation Insights",
     "Volcano Trends",
     "Tectonic Setting",
     "5 Highest Volcanoes by Region",
     "Survey",
     "How to Classify Volcanoes"
    ],
)

# Page 1
if option == "Elevation Insights":
    st.subheader("Elevation Insights")
    st.write(f"🌍 of 🌋: **Map of Volcanoes**")

    st.markdown(
        """
            Color Legend:
        - 🟥: Elevation > 3000 m
        - 🟧: Elevation 1000–3000 m
        - 🟩: Elevation 0 - 1000 m
        - 🟪: Elevation < 0 m
        - ⬛: Unknown
        """
    )
    #Legends and Assign Color
    volcano_data["Elevation_Color"] = [
        [255, 0, 0] if x > 3000 else
        [255, 165, 0] if x > 1000 else
        [0, 128, 0] if x > 0 else
        [128, 0, 128] if x < 0 else
        [169, 169, 169]
        for x in volcano_data["Elevation (m)"]
    ]
    #Learned from https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart
    st.pydeck_chart(
        pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=volcano_data["Latitude"].mean(),
            longitude=volcano_data["Longitude"].mean(),
            zoom=1,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=volcano_data,
                get_position=["Longitude", "Latitude"],
                get_radius=50000,
                get_color="Elevation_Color",
                pickable=True, #Allow to see details with tooltip
            ),
        ],
        tooltip={"html": "<b>Volcano Name:</b> "
                         "{Volcano Name}<br>"
                         "<b>Elevation:</b> "
                         "{Elevation (m)} m",
                 "style": {"color": "white", "background-color": "black"}},

    ))

    # Calculated Fields
    st.write(f"📊  **Elevation Statistics**")
    i, a, v = calculate_stats(volcano_data)
    st.write(f"""
    - Minimum Elevation: {i} m
    - Maximum Elevation: {a} m
    - Average Elevation: {v:.2f} m
    """)
    # Histogram https://docs.streamlit.io/develop/api-reference/charts/st.pyplot
    fig, ax = plt.subplots()
    ax.hist(volcano_data["Elevation (m)"], bins=50, color="steelblue")
    ax.set_title("Distribution of Volcano Elevations", fontsize=14, color="steelblue")
    ax.set_xlabel("Elevation (m)")
    ax.set_ylabel("No. of volcanoes")
    # Streamlit method that displays (fig)
    st.pyplot(fig)

# Option 2
elif option == "Tectonic Setting":
    st.subheader("Distribution by Tectonic Setting")
    tectonic_setting = st.selectbox("Select Tectonic Setting", volcano_data["Tectonic Setting"].dropna().unique())
    #Drop unknown, duplicated categories
    filtered_data = vol_tecto(volcano_data, tectonic=tectonic_setting)
    #Call function vol_tecto
    if not filtered_data.empty:
        st.write(f"🌍 **Map of Volcanoes**")
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/satellite-streets-v11",
            #Applied a map style here
            initial_view_state=pdk.ViewState(
                latitude=filtered_data["Latitude"].mean(),
                longitude=filtered_data["Longitude"].mean(),
                zoom=2,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered_data,
                    get_position=["Longitude", "Latitude"],
                    get_radius=70000,
                    get_color=[255, 10, 100, 200],
                    pickable=True,
                ),
            ],
        tooltip={"html": "<b>Volcano Name:</b> {Volcano Name}<br><b>Elevation:</b> {Elevation (m)} m"},
        ))

        st.write(f"📊  **Landform Distribution for Selected Tectonic Setting**")
        # unique count by value_count()
        counts = filtered_data["Volcano Landform"].value_counts()
        fig, ax = plt.subplots()
        colors = ["#33cc33", "#ff9933", "#6699ff", "#ffcc00", "#ff3399", "#9933ff", "#33ccff"]
        bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)])
        # Get height of each bar, type, and assign color
        ax.set_title("Landform Distribution", color="Steelblue")
        ax.set_ylabel("Count")
        ax.set_xlabel("Volcano Landform")
        ax.legend([bar for bar in bars], counts.index, title="Volcano Landform", loc="upper right")
        # Remove x-axis ticks
        ax.set_xticks([])
        st.pyplot(fig)
        # bar chart
    else:
        st.write("No data available for the selected tectonic setting.")
        #handle no data


# Page 3
elif option == "5 Highest Volcanoes by Region":
    st.subheader("Top 5 Highest Elevation Volcanoes by Region")
    region = st.selectbox("Select Volcanic Region", volcano_data["Volcanic Region"].unique())
    #Select
    filtered_data = vol_tecto(volcano_data, region=region)
    #Call function
    highest_volcanoes = filtered_data.sort_values("Elevation (m)", ascending=False).head(5)
    #Top 5
    st.write("\U0001F4D2 **Details of Top 5 Volcanoes**")
    st.write(highest_volcanoes[["Volcano Name", "Elevation (m)", "Country"]])
    # Scatter plot
    st.write(f"📒 **Scatter Plot of Elevation**")
    fig, ax = plt.subplots()
    ax.scatter(highest_volcanoes["Volcano Name"], highest_volcanoes["Elevation (m)"], color="#ff6678")
    ax.set_title("Top 5 Volcanoes by Elevation", fontsize=14, color="Steelblue")
    ax.set_xlabel("Volcano Name")
    ax.set_ylabel("Elevation (m)")
    ax.tick_params(axis='x', rotation=45)
    # Rotate to avoid overlap
    st.pyplot(fig)


# Page 4
elif option == "Volcano Trends":
    st.subheader("Volcano Landforms and Eruption Trends")
    trend_option = st.selectbox("Select Trend Analysis", ["Landform Proportions", "Eruption Trends"])
    if trend_option == "Landform Proportions":
        st.markdown(
            """
            - <strong>Composite Volcanoes</strong>: Steep-sided, conical mountains formed by alternating eruptions of lava and ash, often with snow-covered peaks. <br>
            - <strong>Cluster Volcanoes</strong>: Groups of closely spaced, smaller volcanoes that erupt from multiple vents within a common area. <br>
            - <strong>Shield Volcanoes</strong>: Broad, gentle slopes primarily formed by the eruption of low-viscosity basaltic lava that can flow easily. <br>
            - <strong>Caldera Volcanoes</strong>: Large, collapsed craters formed when a massive eruption causes the volcano's magma chamber to empty and the land above it to sink.
            </p>
            """, unsafe_allow_html=True
        )

        counts = volcano_data["Volcano Landform"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(
            counts.values,
            autopct='%1.0f%%',#percentage with one decimal place
            startangle=90,
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff6699", "#33cc33", "#ff9933"],  # Added 3 more colors
            pctdistance=1.1
        )
        ax.set_title("Proportion of Volcano Landforms", fontsize=14)
        ax.legend(counts.index, title="Landform Types", loc="upper left")
        st.pyplot(fig)
        # Pie Chart

    elif trend_option == "Eruption Trends":
        st.write("📈 **Eruption Trends Over Time**")
        # Filter out rows with "Unknown
        eruptions_by_decade = volcano_data.dropna(subset=["Eruption Year"])
        # Create  decade row
        eruptions_by_decade["Decade"] = (eruptions_by_decade["Eruption Year"] // 10) * 10
        # Count per decade
        eruption_trends = eruptions_by_decade["Decade"].value_counts().sort_index()

        fig, ax = plt.subplots()
        ax.plot(eruption_trends.index, eruption_trends.values, marker="o", color="Steelblue")
        ax.set_title("Eruption Frequency Over Decades")
        ax.set_xlabel("Decade *BCE is shown in Negative")
        ax.set_ylabel("Number of Eruptions")
        # Display the plot
        st.pyplot(fig)
        st.write(
            "There's no real increase in frequency in volcanic eruptions. "
            "Reported increases in volcanic activity over time often reflect improved reporting mechanisms, technological advances (e.g., satellites, internet), "
            "and population growth near volcanoes, rather than actual increases in activity."
        )

# Option 5
elif option == "Survey":
    st.write("Volcano Information Form")
    st.write("You can create your own volcano here:")
    # Question 1: Slider
    volcano_height = st.slider(
        "Select the approximate height of the volcano (in meters):",
        min_value=-3000,
        max_value=8000,
        step=50,
        help="Select the approximate height of the volcano"
    )
    # Question 2: Number Input
    volcano_age = st.number_input(
        "How old is the volcano (in years)?",
        min_value=0,
        max_value=10000000,
        step=1000,
        help="Enter the estimated age of the volcano in years."
    )

    # Question 3: Radio Button
    volcano_activity = st.radio(
        "What is the current activity status of the volcano?",
        ("Active", "Dormant", "Extinct"),
        help="Select the current activity status of the volcano."
    )

    if st.button("Submit"):
        st.write("Thank you for your responses!")
        st.write(f"1. Volcano Height: {volcano_height} meters")
        st.write(f"2. Volcano Age: {volcano_age} years")
        st.write(f"3. Volcano Activity Status: {volcano_activity}")
#Last Video
elif option == "How to Classify Volcanoes":
    st.markdown("""
   This video describes the features geologists use to classify common types of volcanoes. 
    """)
    video_iframe = """
    <iframe width="560" height="315" 
        src="https://www.youtube.com/embed/iavbdqsSC1o?si=obEYNlXMV5efPCk6" 
        title="YouTube video player" frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
    </iframe>
    """
    st.components.v1.html(video_iframe, height=350)
