from HPOIndexer.graph.Graph import Graph
from HPOIndexer.model.models import NodeType, SubjectType, PredicateType, Node, Curie
from rdflib import Graph as RDFLibGraph
from rdflib import Namespace, URIRef, Literal, BNode
from typing import List, Optional, Iterator, Union, Tuple


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
                    node: NodeType,
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
            if isinstance(obj, Literal):
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
            node: NodeType,
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

    def _make_node(self, iri: URIRef, label_predicate: URIRef) -> Node:
        curie = self.curie_util.iri_to_curie(str(iri))
        label = None
        labels = self.objects(iri, label_predicate)
        count = 0
        for lab in labels:
            count += 1
            if count > 1:
                raise ValueError("More than one label for {}".format(curie))
            label = str(lab)
        return Node(curie, label)

    def get_objects(self,
                    subject:   Optional[SubjectType],
                    predicate: Optional[PredicateType]) \
            -> Iterator[Union[Literal, Curie]]:
        """
        Wrapper for rdflib.Graph.objects
        :param subject: curie formatted identifier
        :param predicate: curie formatted identifier
        :return: Iterator of URIRefs or Literals
        """
        if isinstance(subject, Curie):
            subject = URIRef(self.curie_util.curie_to_iri(subject))
        if isinstance(predicate, Curie):
            predicate = URIRef(self.curie_util.curie_to_iri(predicate))

        for obj in self.objects(subject, predicate):
            if not isinstance(obj, Literal):
                obj = self.curie_util.iri_to_curie(obj)
            yield obj

    def get_subjects(self,
                     obj:       Optional[NodeType],
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

    def _make_node(self,
                   iri: URIRef,
                   label_predicate: URIRef) -> Node:
        curie = self.curie_util.iri_to_curie(str(iri))
        label = None
        labels = self.objects(iri, label_predicate)
        count = 0
        for lab in labels:
            count += 1
            if count > 1:
                raise ValueError("More than one label for {}".format(curie))
            label = str(lab)
        return Node(curie, label)
