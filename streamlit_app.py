import streamlit as st
import pandas as pd
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
        st.write(selected_pod)
        val = df.loc[df["User Name (First then Last)"] == selected_pod, "Patient Id"].unique()
        st.dataframe(val)
    
    
        