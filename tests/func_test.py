# Positional Arguments Test
import json
import logging
import anotherModule
# from module_configs.matplotlib_args import HelperString
# class yieldclass:

    

#     def __init__(self):
#         pass
        
    
#     def __iter__(self):
#         self.x = list(range(4))
#         self.y = [f'K{z}' for z in self.x]
#         self.A = zip(self.y,self.x)
#         for z in self.A: yield z

# def myFunc(*args):
#     print(f'args: {args}, type: {type(args)}')

# def manyargs(a,b,c,d=None):
#     return(f'a: {a}, b: {b}, c: {c}, d: {d}')

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    # E = yieldclass()
    # temp = json.dumps(dict(E),sort_keys=True, indent=4)
    # print(temp)
    # k = ['a', 'b', 'c']
    # v = list(range(3))
    # x = [dict(zip(k,[vi + i for vi in v])) for i in range(4)]
    
    # print(f'x: {x}')
    # y = [manyargs(**z, d=10) for z in x]
    # print(f'y: {y}')

    logger.debug('from man file')
    anotherModule.qq()
