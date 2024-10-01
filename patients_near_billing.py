import pandas as pd

def duration_to_seconds(input):
    if input == 0:
        return 0
    else:
        h, m, s = input.split()
        return int(h[:-1]) * 3600 + int(m[:-1])*60 + int(s[:-1])
    

# this will calculate revenue per minute left 
# args: duration (in seconds)
# output: ["revenue per minute"], ["remaining minutes"] - How much revenue you can gain per minute of work and how many minutes you need to work to achieve next price target
def percent_billed(program, duration):
    if program == "RPM":
        if duration >= 4800: # this is the maxed out case
            return [0, 0, 0, 0]
        billing_bracket = duration // 1200
        time_to_billable = 1200 - (duration % 1200)
        percent_billed = (duration % 1200) / 1200 
        if billing_bracket >= 1: # Billable periods after the first period. Billing code: 99458
            dollars_per_minutes = 40.19 / (time_to_billable/60)
        else: # this is the first billable period. Code: 99457
            dollars_per_minutes = 40.19 / (time_to_billable/60)
        return [dollars_per_minutes, time_to_billable/60, time_to_billable, percent_billed]

    elif program == "PCM":
        if duration >= 5400: # this is the maxed out case
            return [0, 0]
        billing_bracket = duration // 1800
        time_to_billable = 1800 - (duration % 1800)
        percent_billed = (duration % 1800) / 1800 
        if billing_bracket >= 1: # Billable periods after the first period. Billing code: 99458
            dollars_per_minutes = 53.47 / (time_to_billable/60)
        else: # this is the first billable period. Code: 99457
            dollars_per_minutes = 78.60 / (time_to_billable/60)
        return [dollars_per_minutes, time_to_billable/60, time_to_billable, percent_billed]

    elif program == "CCM":
        if (duration/60) >= 61:
            billing_bracket = duration // 1800
            time_to_billable = 1800 - (duration % 1800)
            percent_billed = (duration % 1800) / 1800 
            if billing_bracket >= 1:
                dollars_per_minutes = 72.12 / (time_to_billable/60)
            else:
                dollars_per_minutes = 133.93 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60, time_to_billable, percent_billed]
        else:
            billing_bracket = duration // 1200
            time_to_billable = 1200 - (duration % 1200)
            percent_billed = (duration % 1200) / 1200 
            if billing_bracket >= 1:
                dollars_per_minutes = 47.88 / (time_to_billable/60)
            else:
                dollars_per_minutes = 62.55 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60, time_to_billable, percent_billed]
    else:
        return [0,0, 0, 0]

# this just runs the above functions
def user_patients_close_to_billing(analytics_assessment):
    analytics_assessment["duration in seconds"] = analytics_assessment["Duration (exact)"].apply(duration_to_seconds)
    patients_by_duration = analytics_assessment.groupby(by=["Patient Id", "Enrolled Care Program"])["duration in seconds"].sum().reset_index()

    patients_by_duration[["revenue per minute", "remaining minutes", "time to billable", "percent billed"]] = patients_by_duration.apply(lambda x: percent_billed(x["Enrolled Care Program"], x["duration in seconds"]), axis=1, result_type="expand")
    merged_df = pd.merge(patients_by_duration, 
                     analytics_assessment[['Patient Id', 'Pharmacy Name', 'POD', 'User Name (First then Last)']].drop_duplicates(), 
                     on="Patient Id", 
                     how="left") # merge in the Pharmacy Name, POD, and User Name

    filtered_df = merged_df[merged_df['percent billed'] > 0.5]

    user_patients_billed_over_50_perc = filtered_df.groupby(['User Name (First then Last)'])['Patient Id'].nunique().reset_index()
    user_patients_billed_over_50_perc.rename(columns={'Patient Id': 'patient_count'}, inplace=True)
    user_patients_billed_over_50_perc.sort_values(by=["patient_count"], inplace=True, ascending=False)

    return user_patients_billed_over_50_perc


def pod_patients_close_to_billing(analytics_assessment):
    analytics_assessment["duration in seconds"] = analytics_assessment["Duration (exact)"].apply(duration_to_seconds)
    patients_by_duration = analytics_assessment.groupby(by=["Patient Id", "Enrolled Care Program"])["duration in seconds"].sum().reset_index()

    patients_by_duration[["revenue per minute", "remaining minutes", "time to billable", "percent billed"]] = patients_by_duration.apply(lambda x: percent_billed(x["Enrolled Care Program"], x["duration in seconds"]), axis=1, result_type="expand")
    merged_df = pd.merge(patients_by_duration, 
                     analytics_assessment[['Patient Id', 'Pharmacy Name', 'POD', 'User Name (First then Last)']].drop_duplicates(), 
                     on="Patient Id", 
                     how="left") # merge in the Pharmacy Name, POD, and User Name

    filtered_df = merged_df[merged_df['percent billed'] > 0.5]

    pod_patients_billed_over_50_perc = filtered_df.groupby(['POD'])['Patient Id'].nunique().reset_index()
    pod_patients_billed_over_50_perc.rename(columns={'Patient Id': 'patient_count'}, inplace=True)
    pod_patients_billed_over_50_perc.sort_values(by=["patient_count"], inplace=True, ascending=False)

    return pod_patients_billed_over_50_perc

def pharmacy_patients_close_to_billing(analytics_assessment):
    analytics_assessment["duration in seconds"] = analytics_assessment["Duration (exact)"].apply(duration_to_seconds)
    patients_by_duration = analytics_assessment.groupby(by=["Patient Id", "Enrolled Care Program"])["duration in seconds"].sum().reset_index()

    patients_by_duration[["revenue per minute", "remaining minutes", "time to billable", "percent billed"]] = patients_by_duration.apply(lambda x: percent_billed(x["Enrolled Care Program"], x["duration in seconds"]), axis=1, result_type="expand")
    merged_df = pd.merge(patients_by_duration, 
                     analytics_assessment[['Patient Id', 'Pharmacy Name', 'POD', 'User Name (First then Last)']].drop_duplicates(), 
                     on="Patient Id", 
                     how="left") # merge in the Pharmacy Name, POD, and User Name

    filtered_df = merged_df[merged_df['percent billed'] > 0.5]

    pharmacy_patients_billed_over_50_perc = filtered_df.groupby(['Pharmacy Name'])['Patient Id'].nunique().reset_index()
    pharmacy_patients_billed_over_50_perc.rename(columns={'Patient Id': 'patient_count'}, inplace=True)
    pharmacy_patients_billed_over_50_perc.sort_values(by=["patient_count"], inplace=True, ascending=False)

    return pharmacy_patients_billed_over_50_perc