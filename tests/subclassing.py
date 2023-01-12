from abc import ABC, abstractmethod

class C (ABC):

    @abstractmethod
    def test(self, arg1):
        pass
        
class subclass(C):
    
    def test(self, arg1):
        
        print("concrete: " + arg1)

if __name__ == '__main__':
    z = subclass()