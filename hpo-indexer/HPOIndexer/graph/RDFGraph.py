from HPOIndexer.graph.Graph import Graph
from HPOIndexer.model.models import Node
from rdflib import Graph as RDFLibGraph
from rdflib import Namespace, URIRef, Literal
from typing import List, Optional, Iterator, Union
import re


class RDFGraph(RDFLibGraph, Graph):
    """
    RDF Graph that extends rdflib.graph
    """

    def __init__(self, curie_map=None):
        super().__init__()
        if curie_map is not None:
            self.curie_map = curie_map
        else:
            # default map
            self.curie_map = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                'owl': 'http://www.w3.org/2002/07/owl#'
            }

        for prefix, reference in self.curie_map.items():
            self.bind(prefix, Namespace(reference))

    def get_closure(self,
                    node_id: str,
                    edge: Optional[str]=None,
                    root: Optional[str]=None,
                    label: Optional[str] = "rdfs:label",
                    reflexive: Optional[bool] = True) -> List[Node]:
        nodes = []
        node_iri = URIRef(self._curie_to_iri(node_id))
        label_iri = URIRef(self._curie_to_iri(label))
        if edge is not None:
            edge = URIRef(self._curie_to_iri(edge))
        if root is not None:
            root_iri = URIRef(self._curie_to_iri(root))
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

    def get_descendents(self,
                        node_id: str,
                        edge: Optional[str] = None,
                        label: Optional[str] = "rdfs:label") -> List[Node]:
        nodes = []
        node_iri = URIRef(self._curie_to_iri(node_id))
        label_iri = URIRef(self._curie_to_iri(label))
        if edge is not None:
            edge = URIRef(self._curie_to_iri(edge))
        for sub in self.transitive_subjects(edge, node_iri):
            if node_iri == sub:
                continue
            if isinstance(sub, Literal):
                continue
            node = self._make_node(sub, label_iri)
            nodes.append(node)

        return nodes

    def _make_node(self, iri:URIRef, label_predicate:URIRef) -> Node:
        curie = self._iri_to_curie(str(iri))
        label = None
        labels = self.objects(iri, label_predicate)
        count = 0
        for lab in labels:
            count += 1
            if count > 1:
                raise ValueError("More than one label for {}".format(curie))
            label = str(lab)
        return Node(curie, label)

    def get_objects(self, subject: Optional[str],
                    predicate:Optional[str]) -> Iterator[Union[URIRef, Literal]]:
        """
        Wrapper for rdflib.Graph.objects
        :param subject: curie formatted identifier
        :param predicate: curie formatted identifier
        :return: Iterator of URIRefs or Literals
        """
        if subject is not None:
            subject_curie = URIRef(self._curie_to_iri(subject))
        else:
            subject_curie = None
        if predicate is not None:
            predicate_curie = URIRef(self._curie_to_iri(predicate))
        else:
            predicate_curie = None

        for obj in self.objects(subject_curie, predicate_curie):
            yield obj

    def get_subjects(self, obj: Optional[str],
                     predicate:Optional[str]) -> Iterator[Union[URIRef, Literal]]:
        """
        Wrapper for rdflib.Graph.subjects
        :param subject: curie formatted identifier
        :param predicate: curie formatted identifier
        :return: Iterator of URIRefs or Literals
        """
        if obj is not None:
            obj_curie = URIRef(self._curie_to_iri(obj))
        else:
            subject_curie = None
        if predicate is not None:
            predicate_curie = URIRef(self._curie_to_iri(predicate))
        else:
            predicate_curie = None

        for subject in self.subjects(predicate_curie, obj_curie):
            yield subject

    def _curie_to_iri(self, curie:str) -> str:
        parts = curie.split(":")
        prefix = ""
        suffix = ""
        if len(parts) != 2:
            raise ValueError("Misformatted curie: {}".format(curie))
        else:
            prefix, suffix = parts

        return self.curie_map[prefix] + suffix

    def _iri_to_curie(self, iri: str, namespace: Optional[str]=None) -> str:
        reference = ""
        curie = ""
        if namespace is not None:
            try:
                reference = self.curie_map[namespace]
            except KeyError as e:
                raise "Key not found in curie map: {}".format(namespace)
            curie = iri.replace(reference, namespace + ":")
        else:
            '''
            Ideally need something like
            https://github.com/prefixcommons/curie-util/blob/master/
            src/main/java/org/prefixcommons/trie/Trie.java
            
            In the meantime, this hack should work for some obo ontologies
            '''
            parts = re.split(r'_|#', iri)
            if len(parts) != 2:
                raise ValueError("Cannot resolve iri to curie: {}".format(iri))
            else:
                reference = parts[0] + "_"
                suffix = parts[1]
                namespace = [k for k, v in self.curie_map.items()
                             if v == reference]
                if len(namespace) != 1:
                    raise KeyError("Cannot resolve iri"
                                   " to curie: {}".format(iri))
                curie = "{}:{}".format(namespace[0], suffix)

        return curie

    def _make_node(self, iri:URIRef, label_predicate:URIRef) -> Node:
        curie = self._iri_to_curie(str(iri))
        label = None
        labels = self.objects(iri, label_predicate)
        count = 0
        for lab in labels:
            count += 1
            if count > 1:
                raise ValueError("More than one label for {}".format(curie))
            label = str(lab)
        return Node(curie, label)
