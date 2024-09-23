def duration_to_seconds(input):
    if input == 0:
        return 0
    else:
        h, m, s = input.split()
        return int(h[:-1]) * 3600 + int(m[:-1])*60 + int(s[:-1])
    

# this will calculate revenue per minute left 
# args: duration (in seconds)
# output: ["revenue per minute"], ["remaining minutes"] - How much revenue you can gain per minute of work and how many minutes you need to work to achieve next price target
def revenue_per_minute(program, duration):
    if program == "RPM":
        if duration >= 4800: # this is the maxed out case
            return [0, 0]
        billing_bracket = duration // 1200
        time_to_billable = 1200 - (duration % 1200)
        if billing_bracket >= 1: # Billable periods after the first period. Billing code: 99458
            dollars_per_minutes = 40.19 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60]
        else: # this is the first billable period. Code: 99457
            dollars_per_minutes = 40.19 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60]

    elif program == "PCM":
        if duration >= 5400: # this is the maxed out case
            return [0, 0]
        billing_bracket = duration // 1800
        time_to_billable = 1800 - (duration % 1800)
        if billing_bracket >= 1: # Billable periods after the first period. Billing code: 99458
            dollars_per_minutes = 53.47 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60]
        else: # this is the first billable period. Code: 99457
            dollars_per_minutes = 78.60 / (time_to_billable/60)
            return [dollars_per_minutes, time_to_billable/60]

    elif program == "CCM":
        if (duration/60) >= 61:
            billing_bracket = duration // 1800
            time_to_billable = 1800 - (duration % 1800)
            if billing_bracket >= 1:
                dollars_per_minutes = 72.12 / (time_to_billable/60)
                return [dollars_per_minutes, time_to_billable/60]
            else:
                dollars_per_minutes = 133.93 / (time_to_billable/60)
                return [dollars_per_minutes, time_to_billable/60]
        else:
            billing_bracket = duration // 1200
            time_to_billable = 1200 - (duration % 1200)
            if billing_bracket >= 1:
                dollars_per_minutes = 47.88 / (time_to_billable/60)
                return [dollars_per_minutes, time_to_billable/60]
            else:
                dollars_per_minutes = 62.55 / (time_to_billable/60)
                return [dollars_per_minutes, time_to_billable/60]
    else:
        return [0,0]


# this just runs the above functions
def calc_revenue_per_minute(analytics_assessment):
    analytics_assessment["duration in seconds"] = analytics_assessment["Duration (exact)"].apply(duration_to_seconds)
    patients_by_duration = analytics_assessment.groupby(by=["Patient Id", "Enrolled Care Program"])["duration in seconds"].sum().reset_index()

    patients_by_duration[["revenue per minute", "remaining minutes"]] = patients_by_duration.apply(lambda x: revenue_per_minute(x["Enrolled Care Program"], x["duration in seconds"]), axis=1, result_type="expand")
    patients_by_duration.sort_values(by="revenue per minute", ascending=False, inplace=True)
    return patients_by_duration