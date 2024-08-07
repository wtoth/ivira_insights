

def calculate_revenue(plan, hours, encounters):
    # catch all for it there were no hours
    profit = 0
    if hours == 0:
        return profit
    
    if plan == "RPM":
        hour_block = max(hours // 20 + 1, 4)
        profit = 48.84 + 40.19 * (hour_block - 1)
    elif plan == "PCM":
        hour_block = max(hours // 30 + 1, 3)
        profit = 78.60 + 53.47 * (hour_block - 1)
    elif plan == "CCM":
        if hours >= 61:
            hour_block = (hours - 60) // 30 + 1
            profit = 158.31 + 133.93 + 72.12 * (hour_block - 1)
        else:
            hour_block = max(hours // 20 + 1, 3)
            profit = 62.55 + 47.88 * (hour_block - 1)
    else:
        return 0
    
    if encounters == 0:
        profit *= -1

    return profit