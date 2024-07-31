import datetime

def calculate_age(born):
    born = datetime.datetime.strptime(born, "%m/%d/%Y")
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def select_ages(ages):
    output = []
    counter = 1
    for age in ages:
        if age:
            for num in range(counter, counter + 10):
                output.append(num)
        counter += 10
    return output