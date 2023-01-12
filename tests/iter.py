class foo:

    def __init__(self):
        self.cache = {
            'a': 1234,
            'b': 34,
            'memory': {
                'epic': 888,
                'abc': 'dddd'
            }
        }
    
    def __iter__(self):
        for (k, v) in self.cache.items():
            yield (k,v)
            
            
class C:
    
    def __init__(self, val):
        self.val = val
        self.storage = foo()
        
        
    def __lt__(self, other):
        return self.val < other.val

    def __gt__(self,other):
        return self.val > other.val
    
    def __le__(self, other):
        return self.val <= other.val
    
    def __ge__(self, other):
        return self.val >= other.val
    
    def __str__(self):
        return str(self.val)
    
    def __iter__(self):
        out = {
            'val': self.val,
            'foo': foo,
        }
        for (k, v) in out.items(): 
            yield (k, v)



if __name__ == '__main__':
    x = C(2)
    y = C(4)
    print(f'{x}>={y}?: {x>=y}')
    print(dict(x))