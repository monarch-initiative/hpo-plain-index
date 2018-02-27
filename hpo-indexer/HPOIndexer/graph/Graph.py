from abc import ABCMeta, abstractmethod
from HPOIndexer.model.models import Node
from typing import Sequence, Iterator, Optional, Any, Tuple


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
    def get_descendants(self,
                        node_id: str,
                        edge: Optional[str],
                        label: Optional[str]) -> Sequence[Node]:
        pass

    @abstractmethod
    def get_objects(self, subject: Any, predicate: Any) -> Iterator[str]:
        """
        :return: Returns an iterator of curie formatted identifiers
        """
        pass

    @abstractmethod
    def get_subjects(self, object: Any, predicate: Any) -> Iterator[str]:
        """
        :return: Returns an iterator of curie formatted identifiers
        """
        pass

    @abstractmethod
    def get_predicate_objects(self, subject: Any) -> Iterator[Tuple[str,str]]:
        """
        :return: Returns an iterator of 2 item tuples of either
        (curie: str, curie: str) or (curie: str, literal: str)
        """
        pass

    @abstractmethod
    def parse(self, source, format):
        pass
