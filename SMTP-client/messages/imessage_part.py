from abc import ABC, abstractmethod


class IMessagePart(ABC):
    @abstractmethod
    def build(self) -> str:
        raise NotImplementedError
