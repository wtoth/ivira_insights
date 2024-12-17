import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import time
from datetime import datetime, timedelta
import streamlit_date_picker
from date import filter_by_date
from selected_ages import calculate_age
from calc_revenue_per_minute import calc_revenue_per_minute
from patients_near_billing import user_patients_close_to_billing, pod_patients_close_to_billing, pharmacy_patients_close_to_billing

st.set_page_config(layout='wide')
st.title("Ivira Insights Report")
# current upload file is Analytics Assessment Report 2024-07-01 2024-07-31.xlsx

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

        df["date"] = datetime(year=2024, month=7, day=1)

        # Date Range 
        # note: by default we select the last month
        today = datetime.today()
        days_since_start_of_month = (today - today.replace(day=1))
        default_start, default_end = datetime.now() - days_since_start_of_month, datetime.now()

        #NOTE!!! HUGE default set is being set initially to year=2024, month=7, day=1 based on our data
        default_start = datetime(year=2024, month=7, day=1)

        date_range_string = streamlit_date_picker.date_range_picker(picker_type=streamlit_date_picker.PickerType.date,
                                            start=default_start, end=default_end,
                                            key='date_range_picker',
                                            refresh_button={'is_show': True, 'button_name': 'Current Month',
                                                            'refresh_value': days_since_start_of_month})
        if date_range_string:
            start_date, end_date = date_range_string

        df.dropna(subset="Patient Id", inplace=True)
        #df["Encounters Completed (Call type: Encounter YES)"].fillna(0, inplace=True)
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

    # Insurance Group Logic
    insurance_plans_selected = [plan for plan, val in zip(insurance_options, insurance_plans_checkboxes) if val]
    df = df[df["Primary Plan Name"].isin(insurance_plans_selected)]

    time.sleep(0.5) # this delays long enough to prevent an error

    # filter by date
    df = filter_by_date(df, start_date, end_date)
    #st.write(df)

    st.header("Patients with highest return per minute of care")
    with st.container(border=True):
        rev_per_minute_data = calc_revenue_per_minute(df)
        st.data_editor(rev_per_minute_data[["Patient Id", "Enrolled Care Program", "revenue per minute", "remaining minutes"]], hide_index=True, use_container_width=True)

    st.header("Number of Patients billed greater than 50\%")
    with st.container(border=True):
        col_1, col_2 = st.columns(2)
        with st.container():
            with col_1:
                col_1.subheader("Number of Patients billed greater than 50\% of their time by Pod")
                nested_col_1, nested_col_2 = st.columns(2) 
                with nested_col_1:
                    pod_patients_count = pod_patients_close_to_billing(df, 0.5)
                    st.dataframe(pod_patients_count, hide_index=True)
                with nested_col_2:
                    st.bar_chart(pod_patients_count, x="POD", y="patient_count")
        
        with st.container():
            with col_2:
                col_2.subheader("Number of Patients billed greater than 50\% of their time by User Name")
                nested_col_3, nested_col_4 = st.columns(2) 
                with nested_col_3:
                    user_patients_count = user_patients_close_to_billing(df, 0.5).rename(columns={"User Name (First then Last)":"Employee"})
                    st.dataframe(user_patients_count, hide_index=True)
                with nested_col_4:
                    st.bar_chart(user_patients_count.iloc[:10], x="Employee", y="patient_count")


    # breakdown billed hours by call type
    billed_hours_by_user_type = df.groupby(by=["User Type"])["duration in seconds"].sum().reset_index()
    billed_hours_by_user_type["duration in hours"] = round(billed_hours_by_user_type["duration in seconds"] / 3600, 2)
    # st.dataframe(billed_hours_by_user_type)
    
    

    st.title("Billed Hours by User Type")
    with st.container(border=True):
        user_type_col_1, user_type_col_2 = st.columns(2) 
        with user_type_col_1: 
            fig = px.pie(
                billed_hours_by_user_type, 
                names="User Type", 
                values="duration in hours",
                title="Distribution of Billed Hours by User Type"
            )
            st.plotly_chart(fig)
        with user_type_col_2:
            st.subheader("")
            st.bar_chart(billed_hours_by_user_type, x="User Type", y="duration in hours", )

    st.title("Billed Hours Broken down by Call Type")
    with st.container(border=True):
        billed_hours_by_care_type = df.groupby(by=["Call Type Selected"])["duration in seconds"].sum().reset_index()
        billed_hours_by_care_type["duration in minutes"] = round(billed_hours_by_care_type["duration in seconds"] / 60, 2)
        billed_hours_by_care_type.sort_values(by="duration in minutes", ascending=False, inplace=True)
        hours_breakdown_col_1, hours_breakdown_col_2 = st.columns(2) 
        with hours_breakdown_col_1: 
            st.dataframe(billed_hours_by_care_type[["Call Type Selected", "duration in minutes"]], hide_index=True)
        with hours_breakdown_col_2: 
            st.subheader("Top 5 Call Types")
            st.bar_chart(billed_hours_by_care_type.iloc[:5], x="Call Type Selected", y="duration in minutes", y_label ="Hours for each call")
