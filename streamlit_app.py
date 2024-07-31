import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from selected_ages import select_ages, calculate_age

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

    df.dropna(subset="Patient Id", inplace=True)

    insurance_options = list(df["Primary Plan Name"].unique())

    with st.sidebar:
        with st.expander("Select Age Groups"):
            age_0_10 = st.checkbox("1-10", value=True)
            age_11_20 = st.checkbox("11-20", value=True)
            age_21_30 = st.checkbox("21-30", value=True)
            age_31_40 = st.checkbox("31-40", value=True)
            age_41_50 = st.checkbox("41-50", value=True)
            age_51_60 = st.checkbox("51-60", value=True)
            age_61_70 = st.checkbox("61-70", value=True)
            age_71_80 = st.checkbox("71-80", value=True)
            age_81_90 = st.checkbox("81-90", value=True)
            age_91_100 = st.checkbox("91-100", value=True)

        with st.expander("Select Insurance Plans"):
            for plan in insurance_options:
                st.checkbox(f"{plan}", value=True)

    # Age group logic
    df["Age"] = df["Birth Date"].apply(calculate_age)
    age_checkboxes = [age_0_10, age_11_20, age_21_30, age_31_40, age_41_50, age_51_60, age_61_70, age_71_80, age_81_90, age_91_100]
    selected_ages = select_ages(age_checkboxes)
    df = df[df["Age"].isin(selected_ages)]

    pod_options = df["User Name (First then Last)"].unique()
    multiselect_pods = st.multiselect("Select your Pods", pod_options, placeholder="None Selected",)

    if multiselect_pods:
        mean_duration_by_care_program = pd.Series([])
        count_duration_by_care_program = pd.Series([])

        for selected in multiselect_pods:
            curr_pod = df.loc[df["User Name (First then Last)"] == selected, :]
            if mean_duration_by_care_program.empty:
                mean_duration_by_care_program = curr_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].mean()
                mean_duration_by_care_program.rename(selected, inplace=True)
            else:
                new_pod = curr_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].mean()
                new_pod.rename(selected, inplace=True)
                mean_duration_by_care_program = pd.merge(mean_duration_by_care_program, new_pod, how="outer", on="Enrolled Care Programs")
        
            if count_duration_by_care_program.empty:
                count_duration_by_care_program = curr_pod.groupby(by=["Enrolled Care Programs"])["Patient Id"].size()
                count_duration_by_care_program.rename(selected, inplace=True)
            else:
                new_pod = curr_pod.groupby(by=["Enrolled Care Programs"])["Patient Id"].size()
                new_pod.rename(selected, inplace=True)
                count_duration_by_care_program = pd.merge(count_duration_by_care_program, new_pod, how="outer", on="Enrolled Care Programs")

                 
        # Mean Duration per Enrolled Care Program
        st.write("Mean Duration of Encounters per Enrolled Care Program ")
        st.write(mean_duration_by_care_program)

        #Get total number of Encounters per Enrolled Care Program 
        st.write("Total number of Encounters per Enrolled Care Program ")
        st.write(count_duration_by_care_program)
                
    #     # All of the patient ids
    #     st.write(f"Patients in {selected_pod}")
    #     vals = df.loc[df["User Name (First then Last)"] == selected_pod, "Patient Id"].unique()
    #     display_columns = 16
    #     padding_needed = (display_columns - len(vals) % display_columns) % display_columns

    #     # Pad the array with None (or np.nan)
    #     padded_data = np.pad(vals, (0, padding_needed), 'constant', constant_values=np.nan)

    #     st.dataframe(padded_data.reshape(-1, display_columns))
                 