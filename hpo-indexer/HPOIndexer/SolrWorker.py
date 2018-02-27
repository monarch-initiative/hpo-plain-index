from HPOIndexer.graph.Graph import Graph
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie
from typing import List, Optional, Dict, Iterator
from multiprocessing import Lock


class SolrWorker():

    def __init__(self,
                 id_list: List[Curie],
                 graph:Graph,
                 owl_util: OWLUtil,
                 curie_util: CurieUtil,
                 solr: str,
                 lock: Optional[Lock] = None):
        self.id_list = id_list
        self.graph = graph
        self.owl_util = owl_util
        self.curie_util = curie_util
        self.solr = solr
        self.lock = lock # multiprocessing not implemented


    def run(self):
        pass


    def get_anatomy_terms(self, phenotype: Curie) -> Iterator[Curie]:
        anatomy_terms = []
        query = \
        """
            SELECT ?anatomy
            WHERE {{
                VALUES ?relation {{ RO:0000052 RO:0002314 }} 
                {0}  owl:equivalentClass [ a owl:Restriction ;
                    owl:onProperty BFO:0000051 ;
                    owl:someValuesFrom [ a owl:Class ;
                        owl:intersectionOf ( ?quality [ a owl:Restriction ;
                            owl:onProperty ?relation ;
                            owl:someValuesFrom ?anatomy ] [ a owl:Restriction ;
                            owl:onProperty RO:0002573 ;
                            owl:someValuesFrom PATO:0000460 ] ) ] ] .
            }}
        """.format(phenotype.id)


        query_result = self.graph.query(query)
        for res in query_result:
            yield self.curie_util.iri_to_curie(res[0])

        return anatomy_terms

