import os
import pickle
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px

import streamlit as st
from utils import helper

########################
# Streamlit Sidebar
########################

st.set_page_config(layout="wide")
machines = {
    '603cd4524c34d5594f30cef1': 'Kuba',
    '603cd3ac4c34d5fac730ced3': 'Borkum',
    '603cd36f4c34d5a3d730ceca': 'Darss'
}

def format_func(option):
    return machines[option]

with st.sidebar:
    st.subheader('Configure the plot')

    month = st.selectbox(options=range(5,9), label='Please select a month', index=3)
    machineId = st.selectbox(
        options=list(machines.keys()),
        label='Please select a machine',
        key='machine',
        format_func=format_func,
        index=1
    )
    machineName = machines[machineId]

    with open('settings_' + machineId + '.pickle', 'rb') as handle:
        settings = pickle.load(handle)

    sensor_labels = settings['sensor_name_mapping']
    sensor_labels_ext = {}

    for key, label in sensor_labels.items():
        sensor_labels_ext['sensor_' + key] = label

###########################################################################
# Settings
###########################################################################
analyse_timerange = (dt.date(2023, month, 1), dt.date(2023, month+1, 1))

res_path = os.path.join(os.getcwd(), 'results_1511')

legend_activated=True

###########################################################################
# Load Data
###########################################################################

# get all files from results directory
loaded_dfs = []
list_filenames = []
for filename in os.listdir(res_path):
    list_filenames.append(filename)

filenames_filtered = []
for filename in list_filenames:
    valid = False

    # filter by analyse timerange
    file_timerange = (dt.datetime.strptime(filename.split('_')[1],"%Y-%m-%d").date(), dt.datetime.strptime(filename.split('_')[2],"%Y-%m-%d").date())
    if analyse_timerange[0] > file_timerange[0] or analyse_timerange[1] < file_timerange[1]:
        continue

    # filter by machine id
    if machineId not in filename:
        continue

    filenames_filtered.append(filename)


# todo if necessary
list_filenames_sorted = filenames_filtered.copy()

# parse dataframes from pickle files
for filename in list_filenames_sorted:
    with open(os.path.join(res_path,filename), 'rb') as handle:
        ldf = pickle.load(handle)
        loaded_dfs.append(ldf)

for ldf in loaded_dfs:
    print(ldf.shape)

# concatenate all loaded dataframes
df = pd.concat(loaded_dfs)

###########################################################################
# Split Data
###########################################################################
df.loc[df['cluster'] == 'decrease','cluster'] = 'increase'
df.loc[df['cluster'] != 'increase','cluster'] = 0
df.sort_index(inplace=True)
sensor_columns = [c for c in df.columns if isinstance(c, str) and 'sensor' in c]
station_columns = [column for column in df.columns if isinstance(column,str) and 'sensor' not in column and 'total' not in column and 'total_parts' not in column and 'cluster' not in column]
changes = helper.detect_changes(df, 'cluster')
anomaly_ranges = helper.anomaly_ranges(changes, 'increase')

anomalies = {}
for anomaly_range in anomaly_ranges:
    start = anomaly_range[0] - pd.Timedelta(hours=3)
    end = anomaly_range[1] + pd.Timedelta(hours=6)
    anomalies[anomaly_range] = df[start:end]

###########################################################################
# Visualization
###########################################################################
print('Visualizing...')
st.title("Anomalies in Failures: "+str(analyse_timerange[0])+" - "+str(analyse_timerange[1])+" "+machineName)
st.write("The anomalies were detected using machine learning algorithms. The Kmeans clustering algorithm and the Dynamic Time Warping metric were applied. Each row shows one anomaly. The first graph shows the total failures (rejects) in relation to the total production volume (in percent). The second graph shows the distribution of the failures among the sensors. The third graph shows the distribution of failures among stations.")

#st.bar_chart(df[sensor_columns])

col1, col2, col3 = st.columns(3)
for anomaly_range, dfa in anomalies.items():
    if dfa.loc[anomaly_range[1]]['total'] < 3.0:
        continue

    with col1:
        # Failures total and clusters
        fig = px.line(dfa['total'], title=str(anomaly_range[0].date())+" "+str(anomaly_range[0].time())+": detected anomaly (red)")
        fig = helper.highlight_anomaly(fig, anomaly_range)
        #fig = position_legend(fig, show_legend=False)
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)

    with col2:
        # Sensors Stacked Barchart
        fig = px.bar(dfa[sensor_columns], title="Failures by Sensors")
        fig = helper.change_labels(fig, sensor_labels_ext)
        #fig = position_legend(fig, show_legend=legend_activated)
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)

    with col3:
        # Failures by station
        fig = px.line(dfa[station_columns], title="Failures by Stations")
        #fig = position_legend(fig, show_legend=legend_activated)
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)




