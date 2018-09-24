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


# All node identifier types, includes literals
IdType = TypeVar('IdType', Curie, Literal, URIRef, BNode)

# All node types that could be a subject, excludes literals
SubjectType = TypeVar('SubjectType', Curie, URIRef, BNode)

# All node types that could be a predicate, excludes literals and bnodes
PredicateType = TypeVar('PredicateType', Curie, URIRef)


class Node(NamedTuple):
    id: IdType
    label: Optional[str] = None


class Axiom(NamedTuple):
    id: IdType
    source: SubjectType
    target: IdType
    property: PredicateType
    parts: Optional[Dict[IdType, List[IdType]]] = {}


class PLDoc(NamedTuple):
    """
    Named tuple for storing a solr document for HPO
    terms with plain language synonyms
    """
    id: str  # curie formatted identifier
    label: str  # primary label
    has_pl_syn: bool
    definition: Optional[str] = None
    exact_synonym: Optional[List[str]] = None
    exact_syn_clin: Optional[List[str]] = None
    narrow_synonym: Optional[List[str]] = None
    narrow_syn_clin: Optional[List[str]] = None
    broad_synonym: Optional[List[str]] = None
    broad_syn_clin: Optional[List[str]] = None
    related_synonym: Optional[List[str]] = None
    related_syn_clin: Optional[List[str]] = None
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
