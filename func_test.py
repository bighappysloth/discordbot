# Positional Arguments Test

def myFunc(*args):
    print(f'args: {args}, type: {type(args)}')


if __name__ == '__main__':
    myFunc(0,1,2,3,4,5)