from HPOIndexer.graph.Graph import Graph
from rdflib import Namespace, URIRef, Literal
from typing import List, Dict, Optional, Union, Tuple


class OWLUtil():
    """
    Utility for interacting with OWL graphs
    """

    def __init__(self, graph:Graph):
        self.graph = graph

    def get_axiom_parts(self,
                        source: URIRef,
                        target: Optional[Union[URIRef,Literal]]=None,
                        property: Optional[URIRef]=None,
                        filter: Optional=None
                        ) -> List[Tuple[URIRef,Union[URIRef,Literal]]]:
        pass