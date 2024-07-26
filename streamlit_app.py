import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.title("Ivira Insights Report")

file_upload = st.file_uploader("upload file", type={"xlsx", "csv"})
if file_upload is not None:
    suffix = Path(file_upload.name).suffix
    if suffix == ".xlsx":
            df = pd.read_excel(file_upload)
    elif suffix == ".csv":
            df = pd.read_csv(file_upload)
    else:
        st.write("upload file type failed")

    # st.write(df)

    pod_options = df["User Name (First then Last)"].unique()
    selected_pod = st.selectbox("Select your Pod", pod_options, index=None, placeholder="Pick your Pod",)
    if selected_pod:
        pod = df.loc[df["User Name (First then Last)"] == selected_pod, :]

        # Mean Duration per Enrolled Care Program
        mean_duration_by_care_program = pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].mean()
        st.write("Mean Duration of Encounters per Enrolled Care Program ")
        st.write(mean_duration_by_care_program)

        #Get total number of Encounters per Enrolled Care Program 
        count_duration_by_care_program = pod.groupby(by=["Enrolled Care Programs"])["Patient Id"].size()
        st.write("Total number of Encounters per Enrolled Care Program ")
        st.write(count_duration_by_care_program)

        # All of the patient ids
        st.write(f"Patients in {selected_pod}")
        vals = df.loc[df["User Name (First then Last)"] == selected_pod, "Patient Id"].unique()
        display_columns = 16
        padding_needed = (display_columns - len(vals) % display_columns) % display_columns

        # Pad the array with None (or np.nan)
        padded_data = np.pad(vals, (0, padding_needed), 'constant', constant_values=np.nan)

        st.dataframe(padded_data.reshape(-1, display_columns))


    