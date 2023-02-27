import time
from datetime import datetime, timezone
from discordbot_sloth.config import LOCALZONE

__TIME_FORMAT__ = r'%Y-%m-%d at %H.%M.%S'

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def current_time() -> str:
    return datetime.now().strftime(__TIME_FORMAT__)

def fmt_date(x:datetime) -> str:
    """Converts UTC time to current time. Has the possibility of breaking things if the inputs and outputs are not handled correctly.

    E.g: two different dates are compared but they have their own timezones.
    Args:
        x (datetime): _description_

    Returns:
        str: _description_
    """
    temp = datetime_from_utc_to_local(x).strftime(__TIME_FORMAT__)
    return temp

def convert_time(z) -> datetime:
    return datetime.strptime(current_time(), __TIME_FORMAT__)

def epoch(x=None) -> str: 
    if x is None:
        x = datetime.now()
    seconds = (x - datetime(1970, 1, 1)).total_seconds() * 1000
    # seconds = seconds + x.microsecond
    return str(int(seconds))

if __name__ == '__main__':
    
    print(datetime.strptime(current_time(),__TIME_FORMAT__))