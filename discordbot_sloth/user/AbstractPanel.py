from abc import ABC, abstractmethod


class AbstractPanel(ABC):
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
