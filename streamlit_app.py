import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from selected_ages import calculate_age
from pricing_calculations import calculate_revenue

st.title("Ivira Insights Report")

with st.sidebar:
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
        df["Encounters Completed (Call type: Encounter YES)"].fillna(0, inplace=True)
        insurance_options = list(df["Primary Plan Name"].unique())
        with st.expander("Select Age Groups"):
            age_range = st.slider("Age Range", 0, 100, (0, 100), step=1)

        with st.expander("Select Insurance Plans"):
            insurance_plans_checkboxes = []
            for plan in insurance_options:
                insurance_plans_checkboxes.append(st.checkbox(f"{plan}", value=True))


if file_upload is not None:
    
    # Age group logic
    df["Age"] = df["Birth Date"].apply(calculate_age)
    df = df[df["Age"].isin(range(age_range[0], age_range[1] + 1))]

    # Display the result
    #st.write(grouped_df)
    # st.write(df)

    # Insurance Group Logic
    insurance_plans_selected = [plan for plan, val in zip(insurance_options, insurance_plans_checkboxes) if val]
    df = df[df["Primary Plan Name"].isin(insurance_plans_selected)]

    pod_options = df["User Name (First then Last)"].unique()
    multiselect_pods = st.multiselect("Select your Pods", pod_options, placeholder="None Selected",)

    if multiselect_pods:
        mean_duration_by_care_program = pd.Series([])
        count_duration_by_care_program = pd.Series([])
        current_revenue = pd.Series([])
        uncontacted_revenue = pd.Series([])
        time_billed_by_care_program = pd.Series([])
        time_unbilled_by_care_program = pd.Series([])
        uncontacted = pd.Series([])
        patient_list = {}
        patient_list_pods = {}

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

            patient_list[selected] = df.loc[df["User Name (First then Last)"] == selected, "Patient Id"].unique().tolist()

            # calculate revenue and missing revenue by pod
            grouped_df = curr_pod.groupby(['FirstName', 'LastName', 'User Name (First then Last)', 'Enrolled Care Programs']).agg({
                    'Duration (exact)': 'sum',
                    'Encounters Completed (Call type: Encounter YES)': 'sum'
                }).reset_index()
            
            grouped_df[["revenue", "revenue per minute"]] = grouped_df.apply(lambda x: 
                                                    calculate_revenue(x['Enrolled Care Programs'], 
                                                                                x['Duration (exact)'], 
                                                                                x['Encounters Completed (Call type: Encounter YES)']), 
                                                                                axis=1,
                                                                                result_type="expand")
            grouped_df["FullName"] = grouped_df['FirstName'] + " " + grouped_df['LastName']
            positive_revenue = grouped_df[grouped_df["revenue"] > 0]
            missing_revenue = grouped_df[grouped_df["revenue"] < 0]
            #st.write(positive_revenue)
            if current_revenue.empty:
                current_revenue = pd.DataFrame([[positive_revenue["revenue"].sum()], [positive_revenue["revenue per minute"].mean()], [positive_revenue["Duration (exact)"].sum()]], columns=[selected])
            else:
                current_revenue_tmp = pd.DataFrame([[positive_revenue["revenue"].sum()], [positive_revenue["revenue per minute"].mean()], [positive_revenue["Duration (exact)"].sum()]], columns=[selected])
                current_revenue = pd.concat([current_revenue, current_revenue_tmp], axis=1)

            if uncontacted_revenue.empty:
                uncontacted_revenue = pd.DataFrame([[-1*missing_revenue["revenue"].sum()], [-1*missing_revenue["revenue per minute"].mean()], [missing_revenue["Duration (exact)"].sum()]], columns=[selected])
            else:
                uncontacted_revenue_tmp = pd.DataFrame([[-1*missing_revenue["revenue"].sum()], [-1*missing_revenue["revenue per minute"].mean()], [missing_revenue["Duration (exact)"].sum()]], columns=[selected])
                uncontacted_revenue = pd.concat([uncontacted_revenue, uncontacted_revenue_tmp], axis=1)

            time_billed_by_care_program_pod = positive_revenue.loc[positive_revenue["User Name (First then Last)"] == selected, :]
            if time_billed_by_care_program.empty:
                time_billed_by_care_program = time_billed_by_care_program_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].sum()
                time_billed_by_care_program.rename(selected, inplace=True)
            else:
                new_pod = time_billed_by_care_program_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].sum()
                new_pod.rename(selected, inplace=True)
                time_billed_by_care_program = pd.merge(time_billed_by_care_program, new_pod, how="outer", on="Enrolled Care Programs")
        
            time_unbilled_by_care_program_pod = missing_revenue.loc[missing_revenue["User Name (First then Last)"] == selected, :]
            if time_unbilled_by_care_program.empty:
                time_unbilled_by_care_program = time_unbilled_by_care_program_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].sum()
                time_unbilled_by_care_program.rename(selected, inplace=True)
            else:
                new_pod = time_unbilled_by_care_program_pod.groupby(by=["Enrolled Care Programs"])["Duration (exact)"].sum()
                new_pod.rename(selected, inplace=True)
                time_unbilled_by_care_program = pd.merge(time_unbilled_by_care_program, new_pod, how="outer", on="Enrolled Care Programs")
        

            if uncontacted.empty:
                uncontacted = pd.DataFrame(missing_revenue["FullName"].unique(), columns=[selected])
            else:
                uncontacted_tmp = pd.DataFrame(missing_revenue["FullName"].unique(), columns=[selected])
                uncontacted = pd.concat([uncontacted, uncontacted_tmp], axis=1)



        

        # Mean Duration per Enrolled Care Program
        st.write("Mean Duration of Encounters per Enrolled Care Program ")
        st.write(mean_duration_by_care_program)

        #Get total number of Encounters per Enrolled Care Program 
        st.write("Total number of Encounters per Enrolled Care Program ")
        st.write(count_duration_by_care_program)

        # Revenue by Pod
        st.write("Current Revenue Billed by Pod")
        current_revenue.rename(index={0: "Total Revenue", 1: "Revenue per Minute", 2:"Total Minutes Billed Per Pod"}, inplace=True)
        st.write(current_revenue)

        # Missing Revenue by Pod
        st.write("Amount of Revenue missing by Pod")
        uncontacted_revenue.rename(index={0: "Total Revenue Lost", 1: "Revenue per Minute Lost", 2:"Total Minutes Billed Per Pod"}, inplace=True)
        st.write(uncontacted_revenue)

        st.write("Amount of Revenue Billed Broken down by pod and program")
        st.write(time_billed_by_care_program)

        st.write("Amount of Revenue Missing Broken down by pod and program")
        st.write(time_unbilled_by_care_program)

        # Uncontacted Patients in Each Pod
        st.write("Uncontacted Patients in each Pod")
        st.write(uncontacted)

        # List of Patient Ids in each pod
        st.write("Patients in Each Pod")
        count_string = []
        for key, val in patient_list.items():
            st.write(f"{key}: {len(val)}")

        # Pad each list in patient_list with None to ensure they are all the same length
        max_len = max(len(lst) for lst in patient_list.values())
        padded_patient_list = {k: v + [None] * (max_len - len(v)) for k, v in patient_list.items()}
        patient_list_df = pd.DataFrame(padded_patient_list)
        st.write(patient_list_df)                
                 

        