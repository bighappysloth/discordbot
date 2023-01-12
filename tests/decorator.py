def wrap(x=0):
    def bro(f):
        
        def temp():
            print('Before execution')
            f()
            print(f'After execution. x = {x}')
        
        return temp
    return bro

@wrap(x = 1)
def epic():
    print('Epicly')
    
epic()