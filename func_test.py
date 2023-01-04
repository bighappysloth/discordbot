# Positional Arguments Test
import json
class yieldclass:

    

    def __init__(self):
        pass
        
    
    def __iter__(self):
        self.x = list(range(4))
        self.y = [f'K{z}' for z in self.x]
        self.A = zip(self.y,self.x)
        for z in self.A: yield z

def myFunc(*args):
    print(f'args: {args}, type: {type(args)}')


if __name__ == '__main__':
    E = yieldclass()
    temp = json.dumps(dict(E),sort_keys=True, indent=4)
    print(temp)
