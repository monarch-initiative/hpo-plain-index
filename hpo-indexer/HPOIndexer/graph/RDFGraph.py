from HPOIndexer.graph.Graph import Graph
from HPOIndexer.model.models import IdType, SubjectType, PredicateType, Node, Curie
from rdflib import Graph as RDFLibGraph
from rdflib import Namespace, URIRef, Literal, BNode
from typing import List, Optional, Iterator, Union, Tuple, Any
import re
import copy


class RDFGraph(RDFLibGraph, Graph):
    """
    Graph class that extends rdflib.graph and provides
    support for Curies
    """

    def __init__(self, curie_util):
        super().__init__()
        self.curie_util = curie_util
        for prefix, reference in curie_util.curie_map.items():
            self.bind(prefix, Namespace(reference))

    def get_closure(self,
                    node: IdType,
                    edge: Optional[PredicateType]=None,
                    root: Optional[SubjectType]=None,
                    label_predicate: Optional[Curie] = Curie('rdfs:label'),
                    reflexive: Optional[bool] = True) -> List[Node]:
        nodes = []
        root_seen = {}
        if isinstance(node, Curie):
            node = URIRef(self.curie_util.curie_to_iri(node))
        if isinstance(edge, Curie):
            edge = URIRef(self.curie_util.curie_to_iri(edge))
        if isinstance(root, Curie):
            root = URIRef(self.curie_util.curie_to_iri(root))
        if root is not None:
            root_seen = {root: 1}
        if isinstance(label_predicate, Curie):
            label_predicate = URIRef(self.curie_util.curie_to_iri(label_predicate))
        for obj in self.transitive_objects(node, edge, root_seen):
            if isinstance(obj, Literal) or isinstance(obj, BNode):
                continue
            if not reflexive and node == obj:
                continue
            node = self._make_node(obj, label_predicate)
            nodes.append(node)

        # Add root to graph
        if root is not None:
            nodes.append(self._make_node(root, label_predicate))

        return nodes

    def get_descendants(
            self,
            node: IdType,
            edge: Optional[PredicateType] = None,
            label_predicate: Optional[PredicateType] = Curie('rdfs:label')) \
            -> List[Node]:

        nodes = []
        if isinstance(node, Curie):
            node = URIRef(self.curie_util.curie_to_iri(node))
        if isinstance(label_predicate, Curie):
            label_predicate = \
                URIRef(self.curie_util.curie_to_iri(label_predicate))
        if isinstance(edge, Curie):
            edge = URIRef(self.curie_util.curie_to_iri(edge))
        for sub in self.transitive_subjects(edge, node):
            if node == sub:
                continue
            if isinstance(sub, Literal):
                continue
            node = self._make_node(sub, label_predicate)
            nodes.append(node)

        return nodes

    def _get_objects_from_prop_chain(
            self,
            subject: Optional[SubjectType],
            predicates: List[Any]) -> Iterator[Union[Literal, Curie]]:
        """
        Traverses a property chain and returns an iterator
        of objects at the end of that chain
        :param subject: Optional curie
        :param predicates: A list of either Curies, or a string
                           of pipe delimitted curies (as strings)
                           for example:
                           [
                             Curie("foo:bar"),
                             "foo:baz|foo:qux"
                           ]
        :return:
        """
        # Don't mutate the reference
        predicate_copy = copy.copy(predicates)
        if len(predicates) is 1:
            predicate = predicate_copy.pop(0)
            predicate_list = RDFGraph._convert_curie_list(predicate)
            for pred in predicate_list:
                for obj in self.get_objects(subject, pred):
                    if isinstance(obj, URIRef):
                        obj = self.curie_util.iri_to_curie(obj)
                    yield obj
        else:
            predicate = predicate_copy.pop(0)
            predicate_list = RDFGraph._convert_curie_list(predicate)
            for pred in predicate_list:
                for obj in self.get_objects(subject, pred):
                    for obj_prop in self._get_objects_from_prop_chain(obj, predicate_copy):
                        yield obj_prop

    def _make_node(self, iri: URIRef, label_predicate: URIRef) -> Node:
        curie = self.curie_util.iri_to_curie(str(iri))
        label = None
        labels = self.objects(iri, label_predicate)
        count = 0
        for lab in labels:
            count += 1
            if count > 1:
                raise ValueError("More than one label for {}".format(curie))
            label = lab.value
        return Node(curie, label)

    def get_objects(self,
                    subject:   Optional[SubjectType] = None,
                    predicate: Union[None, List, PredicateType] = None) \
            -> Iterator[Union[Literal, Curie]]:
        """
        Wrapper for rdflib.Graph.objects
        :param subject: curie formatted identifier
        :param predicate: curie formatted identifier
        :return: Iterator of URIRefs or Literals
        """
        if isinstance(predicate, List):
            for obj in self._get_objects_from_prop_chain(subject, predicate):
                yield obj
        else:
            if isinstance(subject, Curie):
                subject = URIRef(self.curie_util.curie_to_iri(subject))
            if isinstance(predicate, Curie):
                predicate = URIRef(self.curie_util.curie_to_iri(predicate))

            for obj in self.objects(subject, predicate):
                if isinstance(obj, URIRef):
                    obj = self.curie_util.iri_to_curie(obj)
                yield obj

    def get_subjects(self,
                     obj:       Optional[IdType],
                     predicate: Optional[PredicateType]) -> Iterator[Curie]:
        """
        Wrapper for rdflib.Graph.subjects
        :param obj: curie or literal
        :param predicate: curie
        :return: Iterator of subjects (Curie)
        """
        if isinstance(obj, Curie):
            obj = URIRef(self.curie_util.curie_to_iri(obj))
        if isinstance(predicate, Curie):
            predicate = URIRef(self.curie_util.curie_to_iri(predicate))

        for subject in self.subjects(predicate, obj):
            if not isinstance(subject, BNode):
                subject = self.curie_util.iri_to_curie(str(subject))
            yield subject

    def get_predicate_objects(self,
                              subject: Curie) \
            -> Iterator[Tuple[Curie, Union[Curie, Literal]]]:

        if isinstance(subject, Curie):
            subject = URIRef(self.curie_util.curie_to_iri(subject))
        for predicate, obj in self.predicate_objects(subject):
            if isinstance(obj, URIRef):
                obj = self.curie_util.iri_to_curie(obj)
            yield self.curie_util.iri_to_curie(str(predicate)), obj

    def add_triple(self,
                   subject: IdType,
                   predicate: PredicateType,
                   obj: IdType) -> None:

        if isinstance(subject, Curie):
            subject = URIRef(self.curie_util.curie_to_iri(subject))
        if isinstance(predicate, Curie):
            predicate = URIRef(self.curie_util.curie_to_iri(predicate))
        if isinstance(obj, Curie):
            obj = URIRef(self.curie_util.curie_to_iri(obj))
        self.add((subject, predicate, obj))

    def get_label(self, subject: IdType) -> None:

        if isinstance(subject, Curie):
            subject = URIRef(self.curie_util.curie_to_iri(subject))
        return self.label(subject)

    @staticmethod
    def _convert_curie_list(curies: str) -> List[Curie]:
        if isinstance(curies, str) and re.match(r'\\|', curies):
            curie_list = curies.split("|")
            curie_list = [Curie(curie) for curie in curie_list]
        else:
            curie_list = [curies]
        return curie_list
