from typing import List, NamedTuple, Optional, Dict, TypeVar
from rdflib import Literal, BNode, URIRef
import json


class Curie(NamedTuple):
    """
    To use in conjunction with RDFLibs
    identifier Classes (Node, URIRef, Literal, BNode, etc)
    """
    id: str

    def __str__(self) -> str:
        return str(self.id)


# All node types, includes literals
NodeType = TypeVar('NodeType', Curie, Literal, URIRef, BNode)

# All node types that could be a subject, excludes literals
SubjectType = TypeVar('SubjectType', Curie, URIRef, BNode)

# All node types that could be a predicate, excludes literals and bnodes
PredicateType = TypeVar('PredicateType', Curie, URIRef)


class Node(NamedTuple):
    id: NodeType
    label: Optional[str] = None


class Axiom(NamedTuple):
    id: NodeType
    source: SubjectType
    target: NodeType
    property: PredicateType
    parts: Optional[Dict[NodeType, List[NodeType]]] = {}


class PLDoc(NamedTuple):
    """
    Named tuple for storing a solr document for HPO
    terms with plain language synonyms
    """
    id: str # curie formatted identifer
    exact_synonym: Optional[List[str]] = None
    narrow_synonym: Optional[List[str]] = None
    broad_synonym: Optional[List[str]] = None
    related_synonym: Optional[List[str]] = None
    phenotype_closure: Optional[List[str]] = None
    phenotype_closure_label: Optional[List[str]] = None
    anatomy_closure: Optional[List[str]] = None
    anatomy_closure_label: Optional[List[str]] = None

    def _asjson(self, *args, **kwargs) -> str:
        """
        Serialize tuple to a JSON formatted string

        :param kwargs: pass through to json.dumps()
        :return: JSON formatted string
        """
        return json.dumps(self._asdict(), *args, **kwargs)
