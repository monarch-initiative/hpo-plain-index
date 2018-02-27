from abc import ABCMeta, abstractmethod
from HPOIndexer.model.models import Node
from typing import Sequence, Iterator, Optional, Any, Tuple


class Graph(metaclass=ABCMeta):

    @abstractmethod
    def get_closure(self,
                    node_id: Any,
                    edge: Optional[Any],
                    root: Optional[Any],
                    label: Optional[Any],
                    reflexive: Optional[bool]) -> Sequence[Node]:
        """
        :return: Returns a sequence of nodes
        """
        pass

    @abstractmethod
    def get_descendants(self,
                        node_id: Any,
                        edge: Optional[Any],
                        label: Optional[Any]) -> Sequence[Node]:
        """
        :return: Returns a sequence of nodes
        """
        pass

    @abstractmethod
    def get_objects(self, subject: Any, predicate: Any) -> Iterator[Any]:
        """
        :return: Returns an iterator of nodes
        """
        pass

    @abstractmethod
    def get_subjects(self, object: Any, predicate: Any) -> Iterator[Any]:
        """
        :return: Returns an iterator of nodes
        """
        pass

    @abstractmethod
    def get_predicate_objects(self, subject: Any) -> Iterator[Tuple[Any,Any]]:
        """
        :return: Returns an iterator of 2 item tuples of nodes that
        correspond to predicates and objects
        """
        pass

    @abstractmethod
    def parse(self, source, format):
        pass

    @abstractmethod
    def query(self, query: str):
        pass
