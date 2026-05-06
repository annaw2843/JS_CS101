import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import altair as alt
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
from utils.download_tool import download_dataset, dataset_path
import sys
import streamlit as st


def main():
    ##################################################
    # Download dataset:
    #       https://catalog.data.gov/dataset/traffic-crashes-crashes
    ##################################################

    download_dataset()

    start = time.time()
    df = pd.read_csv(dataset_path)
    end = time.time()

    print(
        f"Stored dataset locally! It took {end-start:.2f} seconds to load into dataframe."
    )
    print(df.head())
    print(df.shape)

    ##################################################
    # General Data cleaning that helps all of the team
    ##################################################
    # drop duplicate rows
    df = df.drop_duplicates()

    # drop some useless columns
    df = df.drop(columns=["CRASH_RECORD_ID", "CRASH_DATE_EST_I", "DOORING_I"])

    # Clean up CRASH_DATE by converting to datatype
    if df["CRASH_DATE"].dtype != "datetime":
        df["CRASH_DATE"] = pd.to_datetime(df["CRASH_DATE"])
    earliest_date = df["CRASH_DATE"].min()
    latest_date = df["CRASH_DATE"].max()

    # Change the CRASH_DAY_NAME which is numeric to a more informative string 
    number_to_day_map = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday"
    }
    df["CRASH_DAY_NAME"] = df["CRASH_DAY_OF_WEEK"].map(number_to_day_map)

    # These entries are too long to be used as labels for the x- or y-axis
    df["TRAFFIC_CONTROL_DEVICE_SHORT"] = df["TRAFFIC_CONTROL_DEVICE"].replace(
        {
            "TRAFFIC SIGNAL": "SIGNAL",
            "STOP SIGN/FLASHER": "STOP/FLASHER",
            "NO CONTROLS": "NO CTRL",
            "PEDESTRIAN CROSSING SIGN": "PED XING",
            "OTHER RAILROAD CROSSING": "OTHER RR XING",
            "RAILROAD CROSSING GATE": "RR GATE",
            "RR CROSSING SIGN": "RR XING",
            "OTHER REG. SIGN": "REG SIGN",
            "LANE USE MARKING": "LANE MARKS",
            "FLASHING CONTROL SIGNAL": "FLASHER",
            "BICYCLE CROSSING SIGN": "BIKE XING",
            "OTHER WARNING SIGN": "OTHER WARNING"
        }
    )

    df["DEVICE_CONDITION_SHORT"] = df["DEVICE_CONDITION"].replace(
        {
            "FUNCTIONING PROPERLY": "FUNC PROPER",
            "FUNCTIONING IMPROPERLY": "FUNC IMPR",
            "WORN REFLECTIVE MATERIAL": "WORN REFL",
            "NOT FUNCTIONING": "BROKEN",
            "NO CONTROLS": "NO CTRL"
        }
    )

    df["WEATHER"] = df['WEATHER_CONDITION'].replace( {
     "UNKNOWN":"UNK",
     "CLOUDY/OVERCAST": "CLOUDY",
     "FREEZING RAIN/DRIZZLE": "FRZ/RAIN",
     "SLEET/HAIL": "HAIL",
     "BLOWING SNOW": "BLOW SNW",
     "SEVERE CROSS WIND GATE": "CROSS WIND",
     "FOG/SMOKE/HAVE": "HAZY",
     "BLOWING SAND": "BLW SAND"
    })

    # Drop columns that now have substitutes. Do this so the dataset is smaller.
    df = df.drop(columns = ['TRAFFIC_CONTROL_DEVICE', 'DEVICE_CONDITION', 'WEATHER_CONDITION'])

    ##################################################
    # Seaborn Plot #1
    #    To determine whether traffic crashes occur more often when controls are present or absent.
    #    --- Need to clean up data so that if TRAFFIC_CONTROL_DEVICE_SHORT == UNKNOWN, then it does not
    #        effect our data.
    ##################################################

    # Remove all rows with TRAFFIC_CONTROL_DATA_SHORT == UNKNOWN
    df_wo_unkn = df[df["TRAFFIC_CONTROL_DEVICE_SHORT"] != "UNKNOWN"].copy()

    df_wo_unkn["CONTROL_EXISTS"] = "Has Control Device"
    df_wo_unkn.loc[
        df_wo_unkn["TRAFFIC_CONTROL_DEVICE_SHORT"] == "NO CTRL", "CONTROL_EXISTS"
    ] = "No Control Device"


    fig = plt.figure(figsize = (10,6))

    ax = sns.countplot(
        data=df_wo_unkn, x="CONTROL_EXISTS", hue="CONTROL_EXISTS"
    )
    plt.suptitle("How Many Crashes With and Without Traffic Control")
    plt.title(f"Dates: {earliest_date} - {latest_date}")
    plt.xlabel("Existence of Traffic Control Device")
    plt.ylabel("Count")

    for container in ax.containers:
        labels = [f"{int(v):,}" for v in container.datavalues]
        ax.bar_label(container, labels=labels, padding=3)

    max_count = df_wo_unkn["CONTROL_EXISTS"].value_counts().max()
    ax.set_ylim(0, max_count * 1.15)

    if 'ipykernel' in sys.modules:
        plt.show()
    else:
        st.set_page_config(layout="wide")
        st.pyplot(fig)
    
    ##################################################
    # Seaborn Plot #2
    #    To determine whether traffic crashes occur more often when controls are present or absent.
    #    --- Same as Seaborn Plot #1, except uses % (percentages)
    ##################################################
    counts = df_wo_unkn["CONTROL_EXISTS"].value_counts(normalize=True) * 100
    order = ["Has Control Device", "No Control Device"]
    counts = counts.reindex(order)

    colors_wanted = sns.color_palette(
        "magma", len(counts)
    )  # use only as many colors as needed

    fig = plt.figure(figsize = (10,6))
    ax = sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=colors_wanted,
        legend=False,
    )
    plt.suptitle(
        "How Many Crashes With and Without Traffic Control (Percentages)",
        y=0.95,
    )
    plt.title(f"Dates: {earliest_date} - {latest_date}")
    plt.xlabel("Existence of Traffic Control Device")
    plt.ylabel("Percentage")

    # Add percent labels on top
    for i, v in enumerate(counts.values):
        ax.text(i, v + 0.8, f"{v:.1f}% of total", ha="center", fontsize=11)

    ax.set_ylim(0, max(counts.values) + 40)  # Make y-axis go up to 100
    plt.tight_layout()
    plt.show()

    if 'ipykernel' in sys.modules:
        plt.show()
    else:
        st.set_page_config(layout="wide")
        st.pyplot(fig)

    ##########################################################################
    # SEABORN BARPLOT...most common traffic control devices
    ##########################################################################
    df_wo_unkn = df[df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'NO CTRL'].copy()
    df_wo_unkn_nodev = df_wo_unkn[df_wo_unkn["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'NO CTRL'].copy()
    counts = df_wo_unkn_nodev["TRAFFIC_CONTROL_DEVICE_SHORT"].value_counts()  

    fig, ax = plt.subplots(figsize=(10, 6)) 

    g=sns.barplot(x=counts.values,
                  y=counts.index,
                  ax=ax)    # Don't create a new window; 
                            # draw your bar chart on Matplotlib axes
    ax.set_xscale('log')

    ax.set_title(
        "Number of Each Type of Traffic Device Present\n"
        f"Dates: {earliest_date} - {latest_date}",
        fontsize=14)

    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel("Count(log scale)", fontsize=10)
    plt.ylabel("Traffic Control Devices", fontsize=10)
    plt.tight_layout(rect=[0.01, 0, 0.99, 0.99]) 

    if 'ipykernel' in sys.modules:
        plt.show()
    else:
        st.set_page_config(layout="wide")
        st.pyplot(fig, width='stretch')

    ##############################################################################
    # SEABORN HEATMAP - Traffic Control Devices and Their Conditions During Crashes in Percentages.
    ##############################################################################

    # Get rid of traffic control devices where they are unknown.
    #  because an unknown/non-existent device has no real condition.
    # Get rid of unknown device conditions.
    df_wo1 = df[ (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'UNKNOWN')
             &   (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'NO CTRL')
             &   (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'OTHER')
             &   (df["DEVICE_CONDITION_SHORT"] != 'NO CTRL') 
             &   (df["DEVICE_CONDITION_SHORT"] != 'OTHER') 
             &   (df["DEVICE_CONDITION_SHORT"] != 'UNKNOWN') ].copy()

    # Create count table
    heatmap_data = pd.crosstab(
        df_wo1["DEVICE_CONDITION_SHORT"],
        df_wo1["TRAFFIC_CONTROL_DEVICE_SHORT"]
    )

    top = heatmap_data.sum().nlargest(10).index
    heatmap_data_small = heatmap_data[top]

    # Calculate percentages. That is "given a traffic control device, 
    #    give me the percentage occurrence of each condition."
    heatmap_pct = heatmap_data.div(heatmap_data.sum(axis=0), axis=1) * 100
    annot_text  = heatmap_pct.round(1).astype(str) + "%"

    fig, ax = plt.subplots(figsize=(20, 10))
    ax = sns.heatmap(
        heatmap_pct,
        cmap="viridis",
        annot=annot_text,
        annot_kws={"size":12, "weight":"bold"},
        fmt="",
        linewidths=1,
        linecolor="white",
        cbar_kws={"label": "Percent Number of Crashes", "shrink": 0.8},
        square=False,
        ax = ax
    )

    plt.title(
        "Traffic Control Devices and Their Conditions During Crashes (%)\n"
        f"Dates: {earliest_date} - {latest_date}",
        fontsize=24)

    plt.xlabel("Traffic Control Devices", fontsize=13, labelpad=20, fontweight='bold')
    plt.ylabel("Device Conditions", fontsize=13, labelpad=20, fontweight='bold')
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=11)
    cbar.set_label("Percent Number of Crashes", fontsize=13)

    plt.tight_layout(rect=[0.005, 0, 0.995, 0.995])

    if 'ipykernel' in sys.modules:
        plt.show()
    else:
        st.set_page_config(layout="wide")
        st.pyplot(fig)

    ##########################################################################
    # PLOTLY EXPRESS COUNTPLOT...Accident occurred in Clear Weather vs. Inclement?
    ##########################################################################

    df_weather = df[df["WEATHER"] != 'UNK'].copy()
    df_weather["WEATHER_CLEAR"] = df_weather["WEATHER"].apply(
        lambda x: "CLEAR" if x == "CLEAR" else "INCLEMENT"
    )

    fig = px.histogram( df_weather,
                        x='WEATHER_CLEAR',
                        text_auto=True )

    fig.update_layout(
        title= {
            "text": f"<b>Number of Accidents in Clear vs. Non Clear Weather</b><br>"
                    f"<sup><b>Dates: {earliest_date} - {latest_date}</b></sup>",
            'x': 0.5,
            'xanchor': 'center'
    } )

    fig.update_xaxes(title = "<b>Weather</b>", automargin=True)

    if 'ipykernel' in sys.modules:
        fig.show()
    else:
        st.set_page_config(layout="wide")
        st.plotly_chart(fig, width='stretch')

    ##########################################################################
    # PLOTLY EXPRESS COUNTPLOT...Accident occurred in Clear Weather vs. Inclement? in percentages
    ##########################################################################
    df_pct = df_weather['WEATHER_CLEAR'].value_counts(normalize=True).reset_index()
    df_pct.columns = ['WEATHER_CLEAR', 'percentage']
    df_pct['percentage'] *= 100

    fig = px.histogram( df_pct,
                        x='WEATHER_CLEAR',
                        y='percentage',
                        histfunc='sum',
                        text_auto=".1f" )

    fig.update_layout(
        title= {
            "text": f"<b>Number of Accidents in Clear vs. Non Clear Weather (%)</b><br>"
                    f"<sup><b>Dates: {earliest_date} - {latest_date}</b></sup>",
            'x': 0.5,
            'xanchor': 'center'
    } )

    fig.update_xaxes(title = "<b>Weather</b>", automargin=True, autorange='reversed')
    fig.update_traces(texttemplate="%{y:.1f}%", textposition='inside')

    if 'ipykernel' in sys.modules:
        fig.show()
    else:
        st.set_page_config(layout="wide")
        st.plotly_chart(fig, width='stretch')

    
    ######################################################
    # PLOTLY EXPRESS HEATMAP
    # Trying to detect correlation between traffic device
    #  and weather. Does the weather play a factor in seeing the device?
    ######################################################

    # Get rid of traffic control devices where they are unknown.
    #  because an unknown/non-existent device cannot relate to any weather.
    # Get rid of unknown weather conditions.
    df_wo1 = df[ (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'UNKNOWN')
             &   (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'NO CTRL')
             &   (df["TRAFFIC_CONTROL_DEVICE_SHORT"] != 'OTHER')
             &   (df["WEATHER"] != 'UNK') 
             &   (df["WEATHER"] != 'OTHER') ].copy()

    heatmap_data = pd.crosstab(
        df_wo1["WEATHER"],
        df_wo1["TRAFFIC_CONTROL_DEVICE_SHORT"]
    ) 

    # Calculate percentages. That is "given a traffic control device, 
    #    give me the percentage occurrence of each condition."
    heatmap_pct = heatmap_data.div(heatmap_data.sum(axis=0), axis=1) * 100
    fig = px.imshow(
        heatmap_pct,
        color_continuous_scale="magma",
        text_auto=".1f",
        aspect="auto"
    )

    fig.update_layout(
        width=1000,
        height=600,
        autosize=False,
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(
            title="% Count",
            title_side="right"
        ),
        title={
            "text": f"<b>Traffic Control Devices and Weather During Crash (%)</b><br>"
                    f"<sup><b>Dates: {earliest_date} - {latest_date}</b></sup>",
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    fig.update_xaxes( tickangle=-45, tickfont=dict(size=12, family="Arial Black") )
    fig.update_yaxes( tickfont=dict(size=12, family="Arial Black"))
    fig.update_xaxes(title = "<b>Traffic Control Devices</b>", automargin=True)
    fig.update_yaxes(title = "<b>Weather</b>", automargin=True)
    fig.update_traces(texttemplate="%{z:.1f}%")

    if 'ipykernel' in sys.modules:
        fig.show()
    else:
        st.set_page_config(layout="wide")
        st.plotly_chart(fig, width='stretch')


    ##########################################################################
    # ALTAIR Plots...investigating the PRIMARY CONTRIBUTORY CAUSE column
    # - ALTAIR limits its dataset size to 5000 rows, so sampling was necessary to obtain the 5000 rows.
    # - Because of the sampling, the results are nondeterministic and can vary from run to run.
    ##########################################################################

    df["CAUSE"] = df['PRIM_CONTRIBUTORY_CAUSE'].replace( {
         'DRIVING SKILLS/KNOWLEDGE/EXPERIENCE': 'DRIVING SKILLS',
         'UNDER THE INFLUENCE OF ALCOHOL/DRUGS (USE WHEN ARREST IS EFFECTED)': "ALCH/DRUGS ARREST",
         'HAD BEEN DRINKING (USE WHEN ARREST IS NOT MADE)': 'ALCH/DRUGS NO-ARR',
         'FAILING TO REDUCE SPEED TO AVOID CRASH': "SPEED BY CRASH",
         "FOLLOWING TOO CLOSELY": "TAILGATING",
         'OPERATING VEHICLE IN ERRATIC, RECKLESS, CARELESS, NEGLIGENT OR AGGRESSIVE MANNER': "RECKLESS",
         'DISTRACTION - OTHER ELECTRONIC DEVICE (NAVIGATION DEVICE, DVD PLAYER, ETC.)': "ELECTRONICS",
         'FAILING TO YIELD RIGHT-OF-WAY': "NO RT-OF-WAY",
         'IMPROPER OVERTAKING/PASSING': "IMPR PASSING",
         'EVASIVE ACTION DUE TO ANIMAL, OBJECT, NONMOTORIST': 'EVASIVE ACTION',
         'ROAD ENGINEERING/SURFACE/MARKING DEFECTS': 'ROAD DEFECT',
         'VISION OBSCURED (SIGNS, TREE LIMBS, BUILDINGS, ETC.)': 'VISION OBSCURED'
    })
    df_sample = df.sample(5000)

    df_causes = df_sample[ (df_sample["CAUSE"] != 'UNABLE TO DETERMINE')
                        &  (df_sample["CAUSE"] != 'NOT APPLICABLE') ].copy()

    df_causes['ETRONICS'] = (
        (df_sample["CAUSE"] == 'ELECTRONICS') |
        (df_sample["CAUSE"] == 'TEXTING') |
        (df_sample["CAUSE"] == 'CELL PHONE USE OTHER THAN TEXTING' )
    ).map({True: "YES", False: "NO"})

    df_causes['SPEEDING'] = (
        (df_sample["CAUSE"] == 'FAILING TO REDUCE SPEED TO AVOID CRASH') |
        (df_sample["CAUSE"] == 'SPEED BY CRASH') |
        (df_sample["CAUSE"] == 'EXCEEDING SAFE SPEED FOR CONDITIONS' )
    ).map({True: "YES", False: "NO"})

    df_causes['WEATHER'] = (
        (df_sample["CAUSE"] == 'WEATHER')
    ).map({True: "YES", False: "NO"})

    chart_etronics = alt.Chart(df_causes).mark_bar().encode(
        x=alt.X('ETRONICS:N', 
                title='ELECTRONICS-RELATED CRASHES (Yes/No)',
                sort=["YES", "NO"]),
        y=alt.Y('count():Q', title='Count'),
        color=alt.Color('ETRONICS:N', legend=None)
    ).properties(width=250)

    chart_speeding = alt.Chart(df_causes).mark_bar().encode(
        x=alt.X('SPEEDING:N', 
                title='SPEEDING-RELATED CRASHES (Yes/No)',
                sort=["YES", "NO"]),
        y=alt.Y('count():Q', title='Count'),
        color=alt.Color('SPEEDING:N', legend=None)
    ).properties(width=250)

    chart_weather = alt.Chart(df_causes).mark_bar().encode(
        x=alt.X('WEATHER:N', 
                title='WEATHER-RELATED CRASHES (Yes/No)',
                sort=["YES", "NO"]),
        y=alt.Y('count():Q', title='Count'),
        color=alt.Color('WEATHER:N', legend=None)
    ).properties(width=250)

    top    = df_causes["CAUSE"].value_counts().nlargest(5).index
    df_top = df_causes[df_causes['CAUSE'].isin(top)]

    chart_causes = alt.Chart(df_top).mark_bar().encode(
        x='CAUSE:N',
        y=alt.Y('count():Q', title='Count'),
        color=alt.Color('CAUSE:N', legend=None)
    ).properties(
        width=500,
        title=alt.TitleParams(
            text='Primary Causes of Crashes',
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            fontSize=20,
            subtitleFontSize=14,
            anchor="middle")
    )
    empty_spacer = alt.Chart(pd.DataFrame({'x':[]})).mark_point().properties(width=80)
    top_row = empty_spacer | chart_causes 
    bottom_row = chart_etronics | chart_speeding | chart_weather
    final_chart = top_row & bottom_row

    if 'ipykernel' in sys.modules:
        final_chart.show()
    else:
        st.altair_chart(final_chart, width='stretch'


    ######################################################
    #  PLOTLY SUNBURST
    #   Relates traffic signal devices to lighting conditions.
    #  - Please note that this graph is interactive...click on a color and it will
    #   show you all values associated with a category.
    ######################################################
    df_wo1 = df[
        ~df["TRAFFIC_CONTROL_DEVICE_SHORT"].isin(["UNKNOWN", "OTHER", "OTHER WARNING"]) &
        ~df["LIGHTING_CONDITION"].isin(["UNKNOWN"])
    ].copy()

    top = df_wo1['TRAFFIC_CONTROL_DEVICE_SHORT'].value_counts().nlargest(5).index
    df_small = df_wo1['TRAFFIC_CONTROL_DEVICE_SHORT'].isin(top)
    counts = (
        df_wo1.value_counts(["TRAFFIC_CONTROL_DEVICE_SHORT", "LIGHTING_CONDITION"]).reset_index(name="count")
    )

    fig = px.sunburst(
        counts,
        path=["TRAFFIC_CONTROL_DEVICE_SHORT", "LIGHTING_CONDITION"],
        values="count",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    # Method 1: (not bold, not radial) fig.update_traces(textinfo="label+value+percent parent")
    fig.update_traces(           # Method #2 (bold and radial)
        texttemplate="<b>%{label}</b><br><b>%{value}</b><br><b>%{percentParent:.1%}</b>", 
        insidetextorientation='radial' 
    )
    fig.update_layout(    height=600,
                         title={
                         "text": f"<b>Traffic Control Devices and Lighting During Crash (%)</b><br>"
                         f"<sup><b>Dates: {earliest_date} - {latest_date}</b></sup>",
                         'x': 0.5,
                         'xanchor': 'center' },
                      margin=dict(t=80, b=10, l=5, r=5) # get title closer to plot, rmv left & right white space
    )
    if 'ipykernel' in sys.modules:
        fig.show()
    else:
        st.set_page_config(layout="wide")
        st.plotly_chart(fig, width='stretch')

    ###############################################################################
    # ALTAIR COUNT BAR GRAPHS FOR HOUR FREQUENCY ANALYSIS 
    # - Hours of the highest number of crashes 
    # - Have to sample, since Altair does not like datasets with more than 5000 rows
    # - Since it is a sampling, each time this code is run, the plots can be different
    ###############################################################################
    df_sample = df.sample(5000)

    chartTime = alt.Chart(df_sample).mark_bar().encode(
        x=alt.X('CRASH_HOUR:O',  
                title='Hour of Crash'),
    y=alt.Y('count()',title='Count'),
    ).properties(
        title=alt.TitleParams(
            text='Crash Counts by Hour',
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            fontSize=20,
            subtitleFontSize=14,
            anchor="middle"
        ),
        width=800
    )

    if 'ipykernel' in sys.modules:
        chartTime.show()
    else:
        st.altair_chart(chartTime, width='stretch')

    ###############################################################################
    # ALTAIR COUNT BAR GRAPHS FOR DAY FREQUENCY ANALYSIS 
    # - Day of the week with highest number of crashes 
    # - Have to sample, since Altair does not like datasets with more than 5000 rows
    # - Since it is a sampling, each time this code is run, the plots can be different
    ###############################################################################

    chartDay = alt.Chart(df_sample).encode(
        x=alt.X(
            'CRASH_DAY_NAME:O',
            title='Day of Crash',
            sort=['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            axis=alt.Axis(labelAngle=0, labelFontSize=12, titleFontSize=16),
            scale=alt.Scale(paddingInner=0.25)
        ),
        y=alt.Y(
            'count()',
            title='Crash Count',
            axis=alt.Axis(labelFontSize=12, titleFontSize=16)
        ),
        tooltip=[ 
            alt.Tooltip('CRASH_DAY_NAME:N', title="Day"),
            alt.Tooltip('count():Q', title="Crash Count") 
        ]
    )

    bars = chartDay.mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6
    ).encode(
        color=alt.Color(
            "count():Q",
            scale=alt.Scale(scheme="greens"),
            legend=None
        )
    )

    labels = chartDay.mark_text(
        dy=-8,
        fontSize=12,
        fontWeight="bold"
    ).encode(
        text=alt.Text("count():Q", format=',')
    )

    chartDayFancy = (bars + labels).properties(
        width=800,
        height=400,
        title=alt.TitleParams(
            text="Crash Counts by Day",
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            fontSize=22,
            subtitleFontSize=14,
            anchor="middle"
        )
    ).interactive()

    if 'ipykernel' in sys.modules:
        chartDayFancy.show()
    else:
        st.altair_chart(chartDayFancy, width='stretch')

    ###############################################################################
    # ALTAIR COUNT BAR GRAPHS FOR month FREQUENCY ANALYSIS 
    # - Months with highest number of crashes 
    # - Have to sample, since Altair does not like datasets with more than 5000 rows
    # - Since it is a sampling, each time this code is run, the plots can be different
    ###############################################################################

    month_order = list(range(1,13))
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    df_sample["MONTH_NAME"] = df_sample["CRASH_MONTH"].map(month_names)
    month_counts = (
        df_sample.groupby(["CRASH_MONTH", "MONTH_NAME"]).size().reset_index(name="count")
    )

    total = month_counts["count"].sum()
    month_counts["percent"] = month_counts["count"] / total
    month_counts["percent_label"] = (month_counts["percent"] * 100).round(1).astype(str) + "%"
    bars = alt.Chart(month_counts).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X("MONTH_NAME:N", sort=[month_names[m] for m in month_order], 
                title="Month of Crash",
               axis=alt.Axis(labelAngle=0)),
        y=alt.Y("count:Q", title="Crash Count"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues"), legend=alt.Legend(title="Crash Count")),
        tooltip=[
            alt.Tooltip("MONTH_NAME:N", title="Month"),
            alt.Tooltip("count:Q", title="Crash Count"),
            alt.Tooltip("percent:Q", format=".1%", title="Percent")
        ]
    )

    count_labels = alt.Chart(month_counts).mark_text(
        dy=-8,
        fontSize=11,
        fontWeight="bold",
        color="black"
    ).encode(
        x=alt.X("MONTH_NAME:N", sort=[month_names[m] for m in month_order]),
        y="count:Q",
        text="count:Q"
    )

    percent_labels = alt.Chart(month_counts).mark_text(
        dy=18,
        fontSize=11,
        fontWeight="bold",
        color="white"
    ).encode(
        x=alt.X("MONTH_NAME:N", sort=[month_names[m] for m in month_order]),
        y="count:Q",
        text="percent_label:N"
    )

    chartMonthFancy = (bars + count_labels + percent_labels).properties(
        width=800,
        height=400,
        title=alt.TitleParams(
            text="Crash Counts by Month",
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            fontSize=22,
            subtitleFontSize=13,
            anchor="middle"
        )
    )

    if 'ipykernel' in sys.modules:
        chartMonthFancy.show()
    else:
        st.altair_chart(chartMonthFancy, width='stretch')

    ###############################################################################
    # ALTAIR COUNT BAR GRAPHS FOR year FREQUENCY ANALYSIS 
    # - Years with highest number of crashes 
    # - Have to sample, since Altair does not like datasets with more than 5000 rows
    # - Since it is a sampling, each time this code is run, the plots can be different
    ###############################################################################

    df_sample["YEAR"] = df["CRASH_DATE"].dt.year
    chartYear = alt.Chart(df_sample).mark_line(
        point=False,
        strokeWidth=3
    ).encode(
        x=alt.X('YEAR:O',
                title="Year of Crash",
                axis=alt.Axis(labelAngle=0, format='d')), # format option needed to remove commas from year
        y=alt.Y('count():Q', title='Crash Count'),
        tooltip=[
            alt.Tooltip("YEAR:O", title="Year"),
            alt.Tooltip("count():Q", title="Crash Count")
        ]
    ).interactive()

    points = alt.Chart(df_sample).mark_circle(
        size=130
    ).encode(
        x="YEAR:O",
        y="count():Q",
        color=alt.Color(
            "count():Q", 
            scale=alt.Scale(scheme="browns"), 
            legend=alt.Legend(
                title="Crash Count",
                orient="right",
                titleFontSize=14,
                labelFontSize=12
            )
        ),
        tooltip=[
            alt.Tooltip("YEAR:O", title="Year"),
            alt.Tooltip("count():Q", title="Crash Count")
        ]    
    )

    labels = alt.Chart(df_sample).mark_text(
        dy=-12,
        fontSize=11,
        fontWeight="bold"
    ).encode(
        x="YEAR:O",
        y="count:Q",
        text="count:Q"
    )

    chartYearFancy = (chartYear + points + labels).properties(
        width=800,
        height=400,
        title=alt.TitleParams(
            text="Crash Counts Per Year",
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            fontSize=22,
            subtitleFontSize=13,
            anchor="middle"
        )    
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        strokeWidth=0
    )

    if 'ipykernel' in sys.modules:
        chartYearFancy.show()
    else:
        st.altair_chart(chartYearFancy, width='stretch')

    ###############################################################################
    # ALTAIR 
    #  - Temporal analysis between days of the week and times of crashes
    # - Have to sample, since Altair does not like datasets with more than 5000 rows
    # - Since it is a sampling, each time this code is run, the plots can be different
    ###############################################################################

    chartTemporal = alt.Chart(df_sample).mark_rect().encode(
        x=alt.X('CRASH_HOUR:O', title='Hour of Day'),
        y=alt.Y('CRASH_DAY_NAME:O', 
                title='Day of Week',
                sort=["Sunday", "Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday"]
               ),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='magma')),
        tooltip=[
            alt.Tooltip('CRASH_HOUR:O', title='Hour'),
            alt.Tooltip('CRASH_DAY_NAME:O', title='Day'),
            alt.Tooltip('count():Q', title='Crashes')
        ]
    ).properties(
        width=800,
        height=400,
        title=alt.TitleParams(
            text='Crashes by Hour and Day of Week',
            subtitle=f"Dates: {earliest_date} - {latest_date}",
            anchor="middle"
        )
    ).interactive()

    if 'ipykernel' in sys.modules:
        chartTemporal.show()
    else:
        st.set_page_config(layout="wide")
        st.altair_chart(chartTemporal, width='stretch')

if __name__ == "__main__":
    main()
