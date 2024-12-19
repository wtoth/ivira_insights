from datetime import datetime
import pandas as pd


def filter_by_date(df, start_date, end_date):
    #df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Apply boolean indexing to filter by date
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return filtered_df
