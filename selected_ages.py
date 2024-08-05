import datetime

def calculate_age(born):
    born = datetime.datetime.strptime(born, "%m/%d/%Y")
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
