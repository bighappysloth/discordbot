import datetime
import discord
__TIME_FORMAT__ = r'"%Y-%m-%d at %H.%M.%S'


def current_time() -> str:
    return datetime.datetime.now().strftime(__TIME_FORMAT__)

def fmt_date(x:datetime.datetime) -> str:
    return x.strftime(__TIME_FORMAT__)

def convert_time(z) -> datetime.datetime:
    return datetime.datetime.strptime(current_time(), __TIME_FORMAT__)

def epoch_delta_milliseconds(x=datetime.datetime.now()) -> str: 
    seconds = (x - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    # seconds = seconds + x.microsecond
    return str(int(seconds))

if __name__ == '__main__':
    
    print(datetime.datetime.strptime(current_time(),__TIME_FORMAT__))