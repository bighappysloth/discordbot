from pathlib import Path
from functools import reduce

__TEX_LOG_START__ = r'==== LOG FILE START ===='
__TEXT_LOG_END__ = r'==== LOG FILE END ===='

list_printer = lambda x: reduce(lambda a,b: a + '\n' + b, x)
x = Path('./log_test.txt')

with x.open('r') as log_file: 
    temp = log_file.readlines()
    print(list_printer(temp))
    print(temp)
    shallow = [a.strip() for a in temp]

    start = shallow.index(__TEX_LOG_START__)
    end = shallow.index(__TEXT_LOG_END__)
    crop = temp[start+1:end]
    
    list_printer(crop)
    