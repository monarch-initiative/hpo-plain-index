from HPOIndexer.graph.Graph import Graph
from HPOIndexer.model.models import Node, Curie
from rdflib import Graph as RDFLibGraph
from rdflib import Namespace, URIRef, Literal
from typing import List, Optional, Iterator, Union, Tuple


class RDFGraph(RDFLibGraph, Graph):
    """
    RDF Graph that extends rdflib.graph
    """

    def __init__(self, curie_util):
        super().__init__()
        self.curie_util = curie_util
        for prefix, reference in curie_util.curie_map.items():
            self.bind(prefix, Namespace(reference))

    def get_closure(self,
                    node_id: Curie,
                    edge: Optional[Curie]=None,
                    root: Optional[Curie]=None,
                    label: Optional[str] = 'rdfs:label',
                    reflexive: Optional[bool] = True) -> List[Node]:
        nodes = []
        node_iri = URIRef(self.curie_util.curie_to_iri(node_id))
        label_iri = URIRef(self.curie_util.curie_to_iri(label))
        if edge is not None:
            edge = URIRef(self.curie_util.curie_to_iri(edge))
        if root is not None:
            root_iri = URIRef(self.curie_util.curie_to_iri(root))
            root = {root_iri: 1}
        for obj in self.transitive_objects(node_iri, edge, root):
            if isinstance(obj, Literal):
                continue
            if not reflexive and node_iri == obj:
                continue
            node = self._make_node(obj, label_iri)
            nodes.append(node)

        # Add root to graph
        if root is not None:
            nodes.append(self._make_node(root_iri, label_iri))

        return nodes

    def get_descendants(self,
                        node_id: Curie,
                        edge: Optional[Curie] = None,
                        label: Optional[Curie] = 'rdfs:label') -> List[Node]:
        nodes = []
        node_iri = URIRef(self.curie_util.curie_to_iri(node_id))
        label_iri = URIRef(self.curie_util.curie_to_iri(label))
        if edge is not None:
            edge = URIRef(self.curie_util.curie_to_iri(edge))
        for sub in self.transitive_subjects(edge, node_iri):
            if node_iri == sub:
                continue
            if isinstance(sub, Literal):
                continue
            node = self._make_node(sub, label_iri)
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
                    subject:   Optional[Curie],
                    predicate: Optional[Union[Curie ,Literal]])\
            -> Iterator[Union[Literal, Curie]]:
        """
        Wrapper for rdflib.Graph.objects
        :param subject: curie formatted identifier
        :param predicate: curie formatted identifier
        :return: Iterator of URIRefs or Literals
        """
        if subject is not None:
            subject = URIRef(self.curie_util.curie_to_iri(subject))
        if predicate is not None:
            predicate = URIRef(self.curie_util.curie_to_iri(predicate))

        for obj in self.objects(subject, predicate):
            if not isinstance(obj, Literal):
                obj = self.curie_util.iri_to_curie(obj)
            yield obj

    def get_subjects(self,
                     obj:       Optional[Union[Curie, Literal]],
                     predicate: Optional[Curie]) -> Iterator[Curie]:
        """
        Wrapper for rdflib.Graph.subjects
        :param obj: curie or literal
        :param predicate: curie
        :return: Iterator of subjects (Curie)
        """
        if obj is not None and isinstance(obj, Curie):
            obj = URIRef(self.curie_util.curie_to_iri(obj))
        if predicate is not None:
            predicate = URIRef(self.curie_util.curie_to_iri(predicate))

        for subject in self.subjects(predicate, obj):
            yield self.curie_util.iri_to_curie(str(subject))

    def get_predicate_objects(self,
                              subject: Curie) \
            -> Iterator[Tuple[Curie, Union[Curie, Literal]]]:

        subject = URIRef(self.curie_util.curie_to_iri(subject))
        for predicate, obj in self.predicate_objects(subject):
            if not isinstance(obj, Literal):
                obj = self.curie_util.iri_to_curie(obj)
            yield self.curie_util.iri_to_curie(str(predicate)), obj

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
