from datetime import date,timedelta



def generate_dates():
    begin_date = date(year=2020,month=1,day=1)
    end_date = date(year=2020,month=5,day=1)
    dates = [end_date - timedelta(days=x) for x in reversed(range((end_date-begin_date).days + 1))]
    return dates


def generate_past_dates(length,time_window):
    end_date = date(year=2020,month=4,day=17-time_window)
    dates = [end_date - timedelta(days=x) for x in reversed(range(length))]
    return dates
