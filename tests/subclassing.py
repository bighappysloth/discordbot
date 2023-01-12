from abc import ABC, abstractmethod

from discordbot_sloth.helpers.TimeFormat import *
from discordbot_sloth.helpers.RegexReplacer import *

class C (ABC):

    @abstractmethod
    def test(self, arg1):
        pass
        
class subclass(C):
    
    def test(self, arg1):
        
        print("concrete: " + arg1)

class AbstractClass(ABC):
    
    def __init__(self, 
                 created_date = None,
                 created_unix_date = None):
        
        if created_date is None:
            created_date = current_time()
        if created_unix_date is None:
            created_unix_date = epoch()
            
        self.created_date = created_date
        self.created_unix_date = created_unix_date
    
    
    def __le__(self, other):
        return int(self.created_unix_date) <= int(other.created_unix_date)

    def __lt__(self, other):
        return int(self.created_unix_date) < int(other.created_unix_date)

    def __ge__(self, other):
        return int(self.created_unix_date) >= int(other.created_unix_date)

    def __gt__(self, other):
        return int(self.created_unix_date) > int(other.created_unix_date)

    def timestamp(self):
        out = {
            'created_date': self.created_date,
            'created_unix_date': self.created_unix_date
        }
        return out
        

class ConcreteClass(AbstractClass):
        
    def __init__(self, val, created_date=None, created_unix_date=None):
        super().__init__(created_date, created_unix_date)
        self.val = val    
    
    def __str__(self):
        return str(int(self.created_unix_date))
    
    def __iter__(self):
        out = {
            'val': self.val
        }
        temp = super().timestamp()
        for (k, v) in temp.items():
            out[k] = v
        for (k, v) in out.items():
            yield (k, v)

if __name__ == '__main__':
    x = ConcreteClass(1)
    y = ConcreteClass(2)
    A = [x, y]
    B = list(filter(lambda z: z.val == 1, A))
    
    print(B)
    for z in B:
        print(z.val)