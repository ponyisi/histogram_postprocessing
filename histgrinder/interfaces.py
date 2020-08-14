from abc import ABC, abstractmethod
from typing import Mapping, Collection, Any, Iterable, Union
from .HistObject import HistObject

# Interface for modules that read histograms from a source
class InputModule(ABC):
    @abstractmethod
    def configure(self, options: Mapping) -> None:
        """Called to configure the module. Definition is up to specific implementation."""
        return

    @abstractmethod
    def setSelectors(self, selectors: Collection[str]) -> None:
        return

    @abstractmethod
    def __iter__(self) -> Iterable[HistObject]:
        return None

# Interface for modules that write histograms to a sink
class OutputModule(ABC):
    @abstractmethod
    def configure(self, options: Mapping) -> None:
        """ Called to configure the module."""
        return

    @abstractmethod
    def publish(self, obj: Union[HistObject, Iterable[HistObject]]) -> None:
        """ Publish the histogram. """
        return

    @abstractmethod
    def finalize(self) -> None:
        return