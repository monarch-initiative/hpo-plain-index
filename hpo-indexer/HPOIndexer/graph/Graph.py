from abc import ABCMeta, abstractmethod
from HPOIndexer.model.models import Node
from typing import Sequence, Iterator, Optional, Any, Tuple, Union, List
from HPOIndexer.model.models import IdType, SubjectType, PredicateType


class Graph(metaclass=ABCMeta):

    @abstractmethod
    def get_closure(self,
                    node: IdType,
                    edge: Optional[PredicateType],
                    root: Optional[IdType],
                    label_predicate: Optional[PredicateType],
                    reflexive: Optional[bool]) -> Sequence[Node]:
        """
        :return: Returns a sequence of nodes
        """
        pass

    @abstractmethod
    def get_descendants(self,
                        node: IdType,
                        edge: Optional[PredicateType],
                        label_predicate: Optional[PredicateType]) -> Sequence[Node]:
        """
        :return: Returns a sequence of nodes
        """
        pass

    @abstractmethod
    def get_objects(self,
                    subject: SubjectType,
                    predicate: Union[None, List, PredicateType]) -> Iterator[IdType]:
        """
        :return: Returns an iterator of nodes
        """
        pass

    @abstractmethod
    def get_subjects(self, object: IdType, predicate: PredicateType) -> Iterator[Any]:
        """
        :return: Returns an iterator of nodes
        """
        pass

    @abstractmethod
    def get_predicate_objects(
            self, subject: SubjectType) -> Iterator[Tuple[PredicateType, IdType]]:
        """
        :return: Returns an iterator of 2 item tuples of nodes that
        correspond to predicates and objects
        """
        pass

    @abstractmethod
    def get_label(self, subject: SubjectType):
        pass

    @abstractmethod
    def parse(self, source, format):
        pass

    @abstractmethod
    def query(self, query: str):
        pass

    @abstractmethod
    def add_triple(self,
                   subject: SubjectType,
                   predicate: PredicateType,
                   obj: IdType) -> None:
        pass
