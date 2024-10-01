import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time
from datetime import datetime, timedelta
import streamlit_date_picker
from date import filter_by_date
from calc_revenue_per_minute import calc_revenue_per_minute
from patients_near_billing import user_patients_close_to_billing, pod_patients_close_to_billing, pharmacy_patients_close_to_billing

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
    time.sleep(0.1) # this delays long enough to prevent an error

    # filter by date
    df = filter_by_date(df, start_date, end_date)
    #st.write(df)

    st.write("Patients with the highest revenue per minute of care")
    rev_per_minute_data = calc_revenue_per_minute(df)
    st.write(rev_per_minute_data[["Patient Id", "Enrolled Care Program", "revenue per minute", "remaining minutes"]])

    # metric for who 
    st.write("Number of Patients billed greater than 50\% of their time by Pharmacy")
    pharmacy_patients_count = pharmacy_patients_close_to_billing(df)
    st.write(pharmacy_patients_count)

    st.write("Number of Patients billed greater than 50\% of their time by Pod")
    pod_patients_count = pod_patients_close_to_billing(df)
    st.write(pod_patients_count)

    st.write("Number of Patients billed greater than 50\% of their time by User Name")
    user_patients_count = user_patients_close_to_billing(df)
    st.write(user_patients_count)