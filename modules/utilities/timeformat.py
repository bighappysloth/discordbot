import datetime

def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d at %H.%M.%S")


def epoch_delta_milliseconds():
    x = datetime.datetime.now()
    seconds = (x - datetime.datetime(1970, 1, 1)).total_seconds()*1000
    # seconds = seconds + x.microsecond
    return str(int(seconds))