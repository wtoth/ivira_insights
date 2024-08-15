import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import streamlit_date_picker

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

        
        # Date Range 
        # note: by default we select the last month
        today = datetime.today()
        days_since_start_of_month = (today - today.replace(day=1))
        default_start, default_end = datetime.now() - days_since_start_of_month, datetime.now()
        date_range_string = streamlit_date_picker.date_range_picker(picker_type=streamlit_date_picker.PickerType.date,
                                            start=default_start, end=default_end,
                                            key='date_range_picker',
                                            refresh_button={'is_show': True, 'button_name': 'Current Month',
                                                            'refresh_value': days_since_start_of_month})
        if date_range_string:
            start, end = date_range_string

        df.dropna(subset="Patient Id", inplace=True)
        df["Encounters Completed (Call type: Encounter YES)"].fillna(0, inplace=True)
        insurance_options = list(df["Primary Plan Name"].unique())
        with st.expander("Select Age Groups"):
            age_range = st.slider("Age Range", 0, 100, (0, 100), step=1)

        with st.expander("Select Insurance Plans"):
            insurance_plans_checkboxes = []
            for plan in insurance_options:
                insurance_plans_checkboxes.append(st.checkbox(f"{plan}", value=True))