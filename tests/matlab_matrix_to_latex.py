import argparse
import logging
from discordbot_sloth.helpers.RegexReplacer import RegexReplacer
from discordbot_sloth.helpers.RegexReplacer import list_printer
logger = logging.getLogger(__name__)
mapping = {
    r'\[': r'\\begin{bmatrix}' + '\n',
    r'\]': '\n' + r'\\end{bmatrix}',
    r',': ' & ',
    r';': r' \\\\ ' + '\n',
    r'\*': r'',
}


A = r'[-1*(b_1 + b_2)/M_1, b_2/M_1, -1*(k_1 + k_2)/M_1, k_2/M_1; b_2/M_2, -1*b_2/M_2, k_2/M_2, -1*k_2/M_2; 1, 0, 0, 0; 0, 1, 0, 0]'


B = r'[b_1/M_1, k_1/M_1; 0,0; 0,0; 0,0]'

parser = argparse.ArgumentParser()
parser.add_argument(dest = 'matlab')
args = parser.parse_args()
if __name__ == '__main__':
    
    
    h = RegexReplacer(settings=mapping)
#    print(h.decode(A), end = '\n\n')
#    print(h.decode(B), end = '\n\n')

    #print(h.decode(args.matlab))
    
    z = h.decode(A)
    temp = z.split(r' \\\\ ')
    print(list_printer(temp))    
    temp = [z.split(' & ') for z in temp]
    print(list_printer(temp))    
    
