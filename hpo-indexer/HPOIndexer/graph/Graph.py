from abc import ABCMeta, abstractmethod
from HPOIndexer.model.models import Node
from typing import Sequence, Iterator, Optional


class Graph(metaclass=ABCMeta):

    @abstractmethod
    def get_closure(self,
                    node_id: str,
                    edge: Optional[str],
                    root: Optional[str],
                    label: Optional[str],
                    reflexive: Optional[bool]) -> Sequence[Node]:
        pass

    @abstractmethod
    def get_descendents(self,
                        node_id: str,
                        edge: Optional[str],
                        label: Optional[str]) -> Sequence[Node]:
        pass

    @abstractmethod
    def get_objects(self, subject: Optional[str],
                    predicate:Optional[str]) -> Iterator:
        pass

    @abstractmethod
    def get_subjects(self, object: Optional[str],
                     predicate: Optional[str]) -> Iterator:
        pass

    @abstractmethod
    def parse(self, source, format):
        pass
