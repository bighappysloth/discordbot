#loop
from discordbot_sloth.helpers.RegexReplacer import *

x = list(range(13))
x = [str(z) for z in x]
print(list_printer(x))
numpages = int(len(x)/3) + 1

for i in range(1, numpages + 1):
    
    end = min(3*i,len(x))
    s = list_printer(x[3*(i-1):end])
    print(f'page: {s}') 
    

A = {
    'a': 12,
    'b': 3,
    'c': -5
}
print(dict_printer(A))

test = lambda x: x>=0

B = {k: v for k,v in A.items() if test(v)}
print(B)
