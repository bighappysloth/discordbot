from abc import ABC, abstractmethod
from discordbot_sloth.helpers.TimeFormat import *


class AbstractPanel(ABC):
    
    def __init__(self, 
                 created_date = None,
                 created_unix_date = None):
        
        if created_date is None:
            created_date = current_time()
        if created_unix_date is None:
            created_unix_date = epoch()
        
        self.created_date = created_date
        self.created_unix_date = created_unix_date
    
    @abstractmethod
    async def on_reaction_add(self, emoji, bot):
        pass

    @abstractmethod
    async def on_reaction_remove(self, emoji, bot):
        pass

    @abstractmethod
    async def on_edit(self, after, bot):
        pass

    @abstractmethod
    def __iter__(self):
        pass
    
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
        
        